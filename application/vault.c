#include "vault_map.h"

// C libraries
#include <fcntl.h>
#include <errno.h>
#include <sodium.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <unistd.h>

/**
   vault.c - Main implementation of the vault

   The vault is able to load in a file for a particular vault and process it.
   The vault file should have the following format:

   VERSION | PASS_SALT | ENCRYPTED_MASTER | LOC_DATA | KEY-VALUE PAIRS
      8         16           32+24+16

   The version is the version number of the vault file, in case of changes.
   The password salt is used for deriving the encryption key for the master.
   The encrypted master key is loaded and decrypted using the password.

   Afterwards, the location data field exists to specify where in the file.
   The location data field contains the length of the data, followed by
   3 3-byte chunks that specify the start of key-value pair, the key length,
   and the value length, and 2 2-byte chunks that specifcy whether the section
   is currently being used, and whether the chunk points to deleted data.
   The used field is to allow for quick deletions, which will wipe the encrypted
   values but not move around the rest of the data in the file. The number of
   deleted entries can then be banked up until there is a sufficient amount
   to condense many at once. In addition, appending entries is quick, either
   addition or updating, keeping the amount of internal fragmentation on the
   smaller side.

   LENGTH | USED1 | DEL1 | LOC1 | KEY_LEN1 | VAL_LEN1 | USED2 | DEL2 | LOC2 | ...
      4       2      2      4         4         4         2      2      4

   Finally in the file comes the key value pairs, the actual data being stored.
   This section should be aligned at an 8 byte values, with the key and value
   pieces being aligned. The format for a single instance is as follows:

   MTIME | TYPE | KEY | E_VAL | VAL_MAC | VAL_NONCE | HASH
     8      1     KLEN   VLEN     16         24        32

   The buffer lengths can vary, if more metadata is necessary for the first one,
   and the second and third can vary according to what is necessary to algin
   the rest of the components at 8 byte chunks.

 */

// TODO aldenperrine: Clarify error return codes

/**
   vault_box - struct to hold an entry within the vault
 */
struct vault_box {
  char key[BOX_KEY_SIZE];
  char type;
  uint32_t val_len;
  char value[DATA_SIZE];
};

/**
   vault_info - struct to hold info of the currently open vault

   The current box is the box which is currently opened and contains
   an unencrypted password/information.
 */
struct vault_info {
  int is_open;
  int user_fd;
  uint8_t derived_key[MASTER_KEY_SIZE];
  uint8_t decrypted_master[MASTER_KEY_SIZE];
  crypto_generichash_state hash_state;
  struct vault_box current_box;
  struct vault_map* key_info;
};

const char* filename_pattern = "%s/%s.vault";

/**
   Error codes for functions:
   0 - Valid return
   1 - Issues with locking/unlocking memory
   2 - Issues with parameters
   3 - Issues with I/O
   4+ - Function defined
*/
#define WRITE(fd, addr, len, info) do { if (write(fd, addr, len) < 0) { fputs("Write failed\n", stderr); sodium_mprotect_noaccess(info); return VE_IOERR; } } while(0)
#define READ(fd, addr, len, info) do { if (read(fd, addr, len) < 0) { fputs("Read failed\n", stderr); sodium_mprotect_noaccess(info); return VE_IOERR; } } while(0)

/**
   Internal function definitions

   The following functions all have the internal_* prefix and are used as helper
   functions within the file. The main reason these functions exist is to
   prevent code copying when there is functionality shared between multiple
   different functions.

   Most importantly, these files assume that the check for whether a vault is
   opened and that the memory for the information has been made readable and
   writable, and does not reset this upon return.
 */

/**
   function internal_hash_file

   Hashes the file_size-HASH_SIZE bytes of the file. As the hash is keyed with
   the master key, the hash ensures the integrity of the vault file at rest.

   Returns whether the hash was successful.
 */

int internal_hash_file(struct vault_info* info, uint8_t* hash, uint32_t off_end) {
  uint32_t file_size = lseek(info->user_fd, 0, SEEK_END);
  uint32_t bytes_to_hash = file_size - off_end;
  uint8_t buffer[1024];
  lseek(info->user_fd, 0, SEEK_SET);

  if (crypto_generichash_init(&info->hash_state,
                              info->decrypted_master,
                              MASTER_KEY_SIZE,
                              HASH_SIZE) < 0) {
    return VE_CRYPTOERR;
  }

  while (bytes_to_hash > 0) {
    uint32_t amount_at_once = bytes_to_hash > 1024 ? 1024 : bytes_to_hash;
    if (read(info->user_fd, &buffer, amount_at_once) < 0) {
      return VE_IOERR;
    }

    if (crypto_generichash_update(&info->hash_state,
                                  (const char*)  &buffer,
                                  amount_at_once) < 0) {
      return VE_CRYPTOERR;
    }

    bytes_to_hash -= amount_at_once;
  }

  if (crypto_generichash_final(&info->hash_state, hash, HASH_SIZE) < 0) {
    return VE_CRYPTOERR;
  }

  return VE_SUCCESS;
}

/**
   function get_current_time
*/
uint64_t get_current_time() {
  struct timeval tv;
  gettimeofday(&tv, NULL);
  uint64_t millisecondsSinceEpoch =
    (uint64_t)(tv.tv_sec) * 1000 +
    (uint64_t)(tv.tv_usec) / 1000;

  return millisecondsSinceEpoch;
}

/**
   function internal_append_key
 */
int internal_append_key(struct vault_info* info,
                        uint8_t type,
                        const char* key,
                        const char* value) {
  lseek(info->user_fd, HEADER_SIZE-4, SEEK_SET);
  uint32_t loc_len;
  READ(info->user_fd, &loc_len, 4, info);
  uint32_t loc_data[LOC_SIZE/sizeof(uint32_t)];

  for (uint32_t next_loc = 0; next_loc < loc_len; ++next_loc) {
    READ(info->user_fd, &loc_data, LOC_SIZE, info);
    if (loc_data[0]) {
      continue;
    }

    uint32_t file_loc = lseek(info->user_fd, -1*HASH_SIZE, SEEK_END);
    uint32_t key_len = strlen(key);
    uint32_t val_len = strlen(value);
    uint32_t inode_loc = HEADER_SIZE+next_loc*LOC_SIZE;

    uint64_t m_time = get_current_time();

    int input_len =
      ENTRY_HEADER_SIZE + key_len + val_len + MAC_SIZE + NONCE_SIZE + HASH_SIZE;
    uint8_t* to_write_data = malloc(input_len);
    *((uint64_t*) to_write_data) = m_time;
    to_write_data[ENTRY_HEADER_SIZE-1] = type;
    strncpy(to_write_data+ENTRY_HEADER_SIZE, key, key_len);

    uint8_t* val_nonce = to_write_data+input_len-NONCE_SIZE-HASH_SIZE;
    randombytes_buf(val_nonce, NONCE_SIZE);

    if (crypto_secretbox_easy(to_write_data+ENTRY_HEADER_SIZE+key_len,
                              value, val_len, val_nonce,
                              (uint8_t*) &info->decrypted_master) < 0) {
      fputs("Could not encrypt value for key value pair\n", stderr);
      free(to_write_data);
      if (sodium_mprotect_noaccess(info) < 0) {
        fputs("Issues preventing access to memory\n", stderr);
      }
      return VE_CRYPTOERR;
    }

    crypto_generichash(to_write_data+input_len-HASH_SIZE,
                       HASH_SIZE,
                       to_write_data,
                       input_len-HASH_SIZE,
                       info->decrypted_master,
                       MASTER_KEY_SIZE);

    if (write(info->user_fd, to_write_data, input_len) < 0) {
      fputs("Could not write key-value pair to disk\n", stderr);
      free(to_write_data);
      sodium_mprotect_noaccess(info);
      return VE_IOERR;
    }

    loc_data[0] = STATE_ACTIVE;
    loc_data[1] = file_loc;
    loc_data[2] = key_len;
    loc_data[3] = val_len;
    lseek(info->user_fd, inode_loc, SEEK_SET);

    if (write(info->user_fd, loc_data, LOC_SIZE) < 0) {
      fputs("Could not write inode pair to disk\n", stderr);
      free(to_write_data);
      sodium_mprotect_noaccess(info);
      return VE_IOERR;
    }

    uint8_t file_hash[HASH_SIZE];
    internal_hash_file(info, (uint8_t*) &file_hash, 0);
    lseek(info->user_fd, 0, SEEK_END);
    if (write(info->user_fd, (uint8_t*) &file_hash, HASH_SIZE) < 0) {
      fputs("Could not write hash to disk\n", stderr);
      free(to_write_data);
      sodium_mprotect_noaccess(info);
      return VE_IOERR;
    }


    struct key_info*  current_info = malloc(sizeof(struct key_info));
    current_info->inode_loc = inode_loc;
    current_info->m_time = m_time;
    current_info->type = type;

    add_entry(info->key_info, key, current_info);
    free(to_write_data);
    sodium_mprotect_noaccess(info);

    fputs("Added key\n", stderr);
    return VE_SUCCESS;
  }

  return 4;
}

/**
   function create_key_map
 */
int internal_create_key_map(struct vault_info* info) {
  lseek(info->user_fd, HEADER_SIZE-4, SEEK_SET);
  uint32_t loc_len;
  READ(info->user_fd, &loc_len, 4, info);
  uint32_t loc_data[LOC_SIZE/sizeof(uint32_t)];
  info->key_info = init_map(loc_len/2);
  for (uint32_t next_loc = 0; next_loc < loc_len; ++next_loc) {
    READ(info->user_fd, &loc_data, LOC_SIZE, info);
    uint32_t is_active = STATE_ACTIVE & loc_data[0];
    if (!is_active) {
      continue;
    }

    uint32_t file_loc = loc_data[1];
    uint32_t key_len = loc_data[2];
    uint32_t inode_loc = HEADER_SIZE+next_loc*LOC_SIZE;
    uint8_t key[key_len+1];
    struct key_info*  current_info = malloc(sizeof(struct key_info));
    current_info->inode_loc = inode_loc;

    lseek(info->user_fd, file_loc, SEEK_SET);
    READ(info->user_fd, &(current_info->m_time), sizeof(uint64_t), info);
    READ(info->user_fd, &(current_info->type), sizeof (uint8_t), info);
    READ(info->user_fd, &key, key_len, info);
    key[key_len] = 0;

    add_entry(info->key_info, key, current_info);
    lseek(info->user_fd, HEADER_SIZE+(next_loc+1)*LOC_SIZE, SEEK_SET);
  }
  return VE_SUCCESS;
}

/**
   Vault initialization functions

   The following functions are used to handle opening, closing, and creating
   the vault files, as well as initializing and releasing the internal
   information used to represent the currently opened vault.
 */

/**
   function init_vault

   The function to be called at startup of the application, this ensures
   that the vault is setup to safely load in files and run crypto operations
   safely later on.

   Core dumps are disabled to ensure that passwords in memory are not allowed
   to be part of any core dumps later on. In addition, after libsodium is
   initialized, the memory for the vault information that will be used is
   placed in secure memory and locked to prevent access. While there are
   places in code that gives the passwords to the application, all sensitive
   data handled by the library will be within this secure memory. In addition,
   as the decrypted master key is generated by the library and only ever
   kept in the memory, it should never exist in a decrypted form on hard disk.

   If there is an error, a null pointer is returned.

   Returns a pointer to the memory the vault info is being kept in.
 */
struct vault_info* init_vault() {
  if (setrlimit(RLIMIT_CORE, 0) < 0) {
    fputs("Could not decrease core limit", stderr);
    return NULL;
  }

  if (sodium_init() < 0) {
    fputs("Could not init libsodium\n", stderr);
    return NULL;
  }

  struct vault_info* info = sodium_malloc(sizeof(struct vault_info));
  if (sodium_mlock(info, sizeof(struct vault_info))) {
    fputs("Issues locking memory\n", stderr);
    sodium_free(info);
    return NULL;
  }

  info->is_open = 0;
  if (sodium_mprotect_noaccess(info) < 0) {
    fputs("Issues preventing access to memory\n", stderr);
    return NULL;
  }

  return info;
}

/**
   function release_vault

   The function to be called at the end of using the vault, this releases
   all the memory allocated for the vault information. As sodium_free will
   handle zeroing the memory allocated for the vault_info structure, it does
   not have to be manually done. However ensuring that all allocated memory
   is freed is important, and done mainly in the key map.
 */
int release_vault(struct vault_info* info) {
  sodium_mprotect_readwrite(info);
  if (info->is_open) {
    close(info->user_fd);
    delete_map(info->key_info);
  }
  sodium_munlock(info, sizeof(struct vault_info));
  sodium_free(info);
  return 0;
}

/**
   Specific error return codes:
     4 - snprintf syscall failure
     5 - File already exists
     6 - No access available to create file
     7 - Other open error
     8 - Already have a vault open
     9 - Password derivation issues
     10 - Master key encryption issues
   It is likely that only 5, 7 and 8 are of major concern.
 */
int create_vault(char* directory,
                 char* username,
                 char* password,
                 struct vault_info* info) {
  if (directory == NULL || username == NULL || password == NULL ||
      strlen(directory) > MAX_PATH_LEN || strlen(username) > MAX_USER_SIZE
      || strlen(password) > MAX_PASS_SIZE) {
    return VE_PARAMERR;
  }

  int max_size = strlen(directory)+strlen(username)+10;
  char* pathname = malloc(max_size);
  if (snprintf(pathname, max_size, filename_pattern, directory, username) < 0) {
    return 4;
  }

  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return VE_MEMERR;
  }

  if (info->is_open) {
    fputs("Already have a vault open\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return VE_VOPEN;
  }

  int open_results =
    open(pathname, O_RDWR | O_CREAT | O_EXCL | O_DSYNC, S_IRUSR | S_IWUSR);
  if (open_results < 0) {
    if (errno == EEXIST) {
      return 5;
    } else if (errno == EACCES) {
      return 6;
    } else {
      return 7;
    }
  }

  info->user_fd = open_results;
  crypto_secretbox_keygen(info->decrypted_master);

  uint8_t salt[SALT_SIZE];
  randombytes_buf(salt, sizeof salt);
  if (crypto_pwhash(info->derived_key,
                    MASTER_KEY_SIZE,
                    password,
                    strlen(password),
                    salt,
                    crypto_pwhash_OPSLIMIT_MODERATE,
                    crypto_pwhash_MEMLIMIT_MODERATE,
                    crypto_pwhash_ALG_ARGON2ID13) < 0) {
    fputs("Could not dervie password key\n", stderr);
    close(open_results);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return VE_CRYPTOERR;
  }

  uint8_t encrypted_master[MASTER_KEY_SIZE+MAC_SIZE];
  uint8_t master_nonce[NONCE_SIZE];
  randombytes_buf(master_nonce, sizeof master_nonce);
  if (crypto_secretbox_easy(encrypted_master,
                            info->decrypted_master,
                            MASTER_KEY_SIZE,
                            master_nonce,
                            info->derived_key) < 0) {
    fputs("Could not encrypt master key\n", stderr);
    close(open_results);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return VE_CRYPTOERR;
  }

  uint32_t loc_len = INITIAL_SIZE;
  uint8_t zeros[INITIAL_SIZE*LOC_SIZE] = { 0 };
  uint8_t version = VERSION;
  WRITE(info->user_fd, &version, 1, info);
  WRITE(info->user_fd, &zeros, 7, info);
  WRITE(info->user_fd, &salt, crypto_pwhash_SALTBYTES, info);
  WRITE(info->user_fd, &encrypted_master, MASTER_KEY_SIZE+MAC_SIZE, info);
  WRITE(info->user_fd, &master_nonce, NONCE_SIZE, info);
  WRITE(info->user_fd, &loc_len, sizeof(uint32_t), info);
  WRITE(info->user_fd, &zeros, INITIAL_SIZE*LOC_SIZE, info);

  uint8_t file_hash[HASH_SIZE];
  internal_hash_file(info, (uint8_t*) &file_hash, 0);
  lseek(info->user_fd, 0, SEEK_END);
  if (write(info->user_fd, &file_hash, HASH_SIZE) < 0) {
    fputs("Could not write hash to disk\n", stderr);
    sodium_mprotect_noaccess(info);
    return VE_IOERR;
  }


  info->key_info = init_map(INITIAL_SIZE/2);
  info->current_box.key[0] = 0;
  info->is_open = 1;

  if (sodium_mprotect_noaccess(info) < 0) {
    fputs("Issues preventing access to memory\n", stderr);
  }

  fputs("Created file successfully\n", stderr);
  return VE_SUCCESS;
}

/**
   function open_vault
 */
int open_vault(char* directory,
               char* username,
               char* password,
               struct vault_info* info) {
  if (directory == NULL || username == NULL || password == NULL ||
      strlen(directory) > MAX_PATH_LEN || strlen(username) > MAX_USER_SIZE
      || strlen(password) > MAX_PASS_SIZE) {
    return 2;
  }

  int max_size = strlen(directory)+strlen(username)+10;
  char* pathname = malloc(max_size);
  if (snprintf(pathname, max_size, filename_pattern, directory, username) < 0) {
    return 4;
  }

  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return VE_MEMERR;
  }

  if (info->is_open) {
    fputs("Already have a vault open\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return VE_VOPEN;
  }

  int open_results = open(pathname, O_RDWR | O_NOFOLLOW);
  if (open_results < 0) {
    if (errno == EEXIST) {
      return 5;
    } else if (errno == EACCES) {
      return 6;
    } else {
      return 7;
    }
  }

  lseek(open_results, 8, SEEK_SET);
  int open_info_length = SALT_SIZE+MAC_SIZE+MASTER_KEY_SIZE+NONCE_SIZE;
  uint8_t open_info[open_info_length];
  READ(open_results, open_info, open_info_length, info);


  info->user_fd = open_results;

  if (crypto_pwhash(info->derived_key,
                    MASTER_KEY_SIZE,
                    password,
                    strlen(password),
                    open_info,
                    crypto_pwhash_OPSLIMIT_MODERATE,
                    crypto_pwhash_MEMLIMIT_MODERATE,
                    crypto_pwhash_ALG_ARGON2ID13) < 0) {
    fputs("Could not dervie password key\n", stderr);
    close(open_results);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return VE_CRYPTOERR;
  }

  if (crypto_secretbox_open_easy(info->decrypted_master,
                                 open_info+SALT_SIZE,
                                 MASTER_KEY_SIZE+MAC_SIZE,
                                 open_info+open_info_length-NONCE_SIZE,
                                 info->derived_key) < 0) {
    fputs("Could not decrypt master key\n", stderr);
    close(open_results);
    sodium_memzero(info->derived_key, MASTER_KEY_SIZE);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return VE_CRYPTOERR;
  }

  uint8_t file_hash[HASH_SIZE];
  uint8_t current_hash[HASH_SIZE];
  internal_hash_file(info, (uint8_t*) &file_hash, HASH_SIZE);
  lseek(info->user_fd, -1*HASH_SIZE, SEEK_END);
  READ(info->user_fd, &current_hash, HASH_SIZE, info);
  if (memcmp(&file_hash, &current_hash, HASH_SIZE) != 0) {
    fputs("FILE HASHES DO NOT MATCH\n", stderr);
    sodium_mprotect_noaccess(info);
    return VE_IOERR;
  }


  internal_create_key_map(info);

  info->current_box.key[0] = 0;
  info->is_open = 1;

  if (sodium_mprotect_noaccess(info) < 0) {
    fputs("Issues preventing access to memory\n", stderr);
  }

  fputs("Opened the vault\n", stderr);
  return VE_SUCCESS;
}

/**
   function close_vault
 */
int close_vault(struct vault_info* info) {
  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return VE_MEMERR;
  }

  if (!info->is_open) {
    fputs("Already have a vault closed\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return VE_VCLOSE;
  }

  close(info->user_fd);
  delete_map(info->key_info);
  sodium_memzero(info->derived_key, MASTER_KEY_SIZE);
  sodium_memzero(info->decrypted_master, MASTER_KEY_SIZE);
  sodium_memzero(&info->current_box, sizeof(struct vault_box));
  info->is_open = 0;

  if (sodium_mprotect_noaccess(info) < 0) {
    fputs("Issues preventing access to memory\n", stderr);
  }

  fputs("Closed the vault\n", stderr);
  return VE_SUCCESS;
}

/**
   function condense_file
*/
int condense_file(struct vault_info* info) {
  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return VE_MEMERR;
  }

  if (!info->is_open) {
    fputs("Vault closed\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return VE_VCLOSE;
  }

  uint8_t header[HEADER_SIZE];
  uint32_t loc_size;
  uint32_t* loc_data;
  uint8_t* box_data;
  uint32_t box_len;
  uint32_t current_file_size = lseek(info->user_fd, -1*HASH_SIZE, SEEK_END);
  uint32_t data_replacement_loc = 0;
  uint32_t loc_replacement_index = 0;

  lseek(info->user_fd, 0, SEEK_SET);
  READ(info->user_fd, &header, HEADER_SIZE, info);
  loc_size = *((uint32_t*) (header+HEADER_SIZE-4));

  uint32_t old_data_offset = (loc_size*LOC_SIZE) + HEADER_SIZE;
  uint32_t new_data_offset = (loc_size*LOC_SIZE) + old_data_offset;

  loc_data = malloc(loc_size * LOC_SIZE);
  READ(info->user_fd, loc_data, loc_size * LOC_SIZE, info);
  box_len = current_file_size - old_data_offset;
  box_data = malloc(box_len);
  READ(info->user_fd, box_data, box_len, info);

  for (uint32_t i = 0; i < loc_size; ++i) {
    uint32_t* current_loc_data = loc_data + i * 4;
    uint32_t current_box_len =
      current_loc_data[2]+current_loc_data[3]+ENTRY_HEADER_SIZE+MAC_SIZE+NONCE_SIZE+HASH_SIZE;
    uint32_t current_loc = current_loc_data[1] - old_data_offset;
    if (current_loc_data[0] == ((1 << 16) | 1)) {
      if (loc_replacement_index == i) {
        loc_replacement_index++;
        continue;
      }

      memmove(box_data+data_replacement_loc, box_data+current_loc, current_box_len);
      current_loc_data[1] = new_data_offset+data_replacement_loc;
      data_replacement_loc += current_box_len;

      uint32_t* new_loc_placement = loc_data + loc_replacement_index * 4;
      memmove(new_loc_placement, current_loc_data, LOC_SIZE);
      loc_replacement_index++;

      continue;
    } else if (current_loc_data[0] == 0) {
      break;
    } else {
      if (data_replacement_loc == 0)
        data_replacement_loc = current_loc;
    }
  }

  uint32_t new_data_size = data_replacement_loc;
  uint32_t valid_loc_entries = loc_replacement_index;
  uint32_t new_file_size = new_data_offset + new_data_size;
  uint32_t new_loc_size = loc_size * 2;

  lseek(info->user_fd, new_data_offset, SEEK_SET);
  WRITE(info->user_fd, box_data, new_data_size, info);
  lseek(info->user_fd, HEADER_SIZE-4, SEEK_SET);
  WRITE(info->user_fd, &new_loc_size, 4, info);
  WRITE(info->user_fd, loc_data, valid_loc_entries*LOC_SIZE, info);

  uint32_t num_zeros = (loc_size*2 - valid_loc_entries) * LOC_SIZE;
  uint8_t* zeros = malloc(num_zeros);
  sodium_memzero(zeros, num_zeros);
  WRITE(info->user_fd, zeros, num_zeros, info);
  ftruncate(info->user_fd, new_file_size);

  uint8_t file_hash[HASH_SIZE];
  internal_hash_file(info, (uint8_t*) &file_hash, 0);
  lseek(info->user_fd, 0, SEEK_END);
  if (write(info->user_fd, &file_hash, HASH_SIZE) < 0) {
    fputs("Could not write hash to disk\n", stderr);
    sodium_mprotect_noaccess(info);
    return VE_IOERR;
  }

  delete_map(info->key_info);
  internal_create_key_map(info);

  free(loc_data);
  free(box_data);
  free(zeros);
  sodium_mprotect_noaccess(info);
  fputs("Condensed file and increased loc size\n", stderr);
  return VE_SUCCESS;
}

/**
   function add_key
 */
int add_key(struct vault_info* info,
            uint8_t type,
            const char* key,
            const char* value) {
  if (info == NULL || key == NULL || value == NULL ||
      strlen(value) > DATA_SIZE || strlen(key) > BOX_KEY_SIZE - 1) {
    return VE_PARAMERR;
  }

  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return VE_MEMERR;
  }

  if (!info->is_open) {
    fputs("Already have a vault closed\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return VE_VCLOSE;
  }

  if (get_info(info->key_info, key)) {
    fputs("Key already in map; use update\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return 3;
  }

  if (internal_append_key(info, type, key, value) != 0) {
    condense_file(info);
    if (sodium_mprotect_readwrite(info) < 0) {
      fputs("Issues gaining access to memory\n", stderr);
      return 1;
    }
    return internal_append_key(info, type, key, value);
  }

  sodium_mprotect_noaccess(info);
  return 0;
}

// Result needs to be freed by caller
char** get_vault_keys(struct vault_info* info) {
  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return NULL;
  }

  if (!info->is_open) {
    fputs("Already have a vault closed\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return NULL;
  }

  char** result = get_keys(info->key_info);
  sodium_mprotect_noaccess(info);
  return result;
}

/**
   function num_vault_keys
 */
uint32_t num_vault_keys(struct vault_info* info) {
  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return 0;
  }

  if (!info->is_open) {
    fputs("No open vault\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return 0;
  }

  uint32_t result = num_keys(info->key_info);
  sodium_mprotect_noaccess(info);
  return result;
}

/**
   function last_modified_time
 */
uint64_t last_modified_time(struct vault_info* info, const char* key) {
  if (info == NULL || key == NULL || strlen(key) > BOX_KEY_SIZE - 1) {
    return 0;
  }

  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return 0;
  }

  if (!info->is_open) {
    fputs("Already have a vault closed\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return 0;
  }

  const struct key_info* current_info;
  if (!(current_info = get_info(info->key_info, key))) {
    fputs("Key not in map\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return 0;
  }

  sodium_mprotect_noaccess(info);
  return current_info->m_time;
}

/**
   function open_key
 */
int open_key(struct vault_info* info, const char* key) {
  if (info == NULL || key == NULL || strlen(key) > BOX_KEY_SIZE - 1) {
    return 2;
  }

  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return 1;
  }

  if (!info->is_open) {
    fputs("Already have a vault closed\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return 2;
  }

  const struct key_info* current_info;
  if (!(current_info = get_info(info->key_info, key))) {
    fputs("Key not in map\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return 3;
  }

  if (info->current_box.key[0] != 0 &&
      strncmp(key, (char*) &(info->current_box.key), BOX_KEY_SIZE) == 0) {
    sodium_mprotect_noaccess(info);
    return 0;
  }

  lseek(info->user_fd, current_info->inode_loc, SEEK_SET);
  uint32_t loc_data[LOC_SIZE/sizeof(uint32_t)];
  READ(info->user_fd, loc_data, LOC_SIZE, info);
  uint32_t file_loc = loc_data[1];
  uint32_t key_len = loc_data[2];
  uint32_t val_len = loc_data[3];

  int box_len = ENTRY_HEADER_SIZE+key_len+val_len+MAC_SIZE+NONCE_SIZE+HASH_SIZE;
  uint8_t* box = malloc(box_len);
  lseek(info->user_fd, file_loc, SEEK_SET);
  READ(info->user_fd, box, box_len, info);

  uint8_t hash[HASH_SIZE];
  crypto_generichash((uint8_t*) &hash,
                     HASH_SIZE,
                     box,
                     box_len-HASH_SIZE,
                     info->decrypted_master,
                     MASTER_KEY_SIZE);

  if (memcmp((char*) &hash, box+box_len-HASH_SIZE, HASH_SIZE) != 0) {
    fputs("ENTRY HASH INVALID\n", stderr);
    free(box);
    sodium_mprotect_noaccess(info);
    return 4;
  }

  uint32_t val_loc = ENTRY_HEADER_SIZE+key_len;
  if (crypto_secretbox_open_easy((uint8_t*) &(info->current_box.value),
                                 box+val_loc, val_len+MAC_SIZE,
                                 box+box_len-HASH_SIZE-NONCE_SIZE,
                                 (uint8_t*) &info->decrypted_master) < 0) {
    fputs("Could not decrypt value\n", stderr);
    free(box);
    sodium_mprotect_noaccess(info);
    return 5;
  }

  strncpy((char*) &(info->current_box.key), key, BOX_KEY_SIZE);
  info->current_box.type = box[ENTRY_HEADER_SIZE-1];
  info->current_box.val_len = val_len;
  free(box);
  sodium_mprotect_noaccess(info);

  fputs("Opened a key\n", stderr);
  return 0;
}

/**
   function delete_key
 */
int delete_key(struct vault_info* info, const char* key) {
  if (info == NULL || key == NULL || strlen(key) > BOX_KEY_SIZE - 1) {
    return 2;
  }

  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return 1;
  }

  if (!info->is_open) {
    fputs("No vault opened\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return 2;
  }

  const struct key_info* current_info;
  if (!(current_info = get_info(info->key_info, key))) {
    fputs("Key not in map\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return 3;
  }

  lseek(info->user_fd, current_info->inode_loc, SEEK_SET);
  uint32_t loc_data[LOC_SIZE/sizeof(uint32_t)];
  READ(info->user_fd, loc_data, LOC_SIZE, info);
  uint32_t file_loc = loc_data[1];
  uint32_t key_len = loc_data[2];
  uint32_t val_len = loc_data[3];

  delete_entry(info->key_info, key);
  lseek(info->user_fd, current_info->inode_loc, SEEK_SET);
  uint32_t state_update = 1;
  WRITE(info->user_fd, &state_update, sizeof(uint32_t), info);
  int size = val_len+MAC_SIZE;
  char* zeros = malloc(size);
  sodium_memzero(zeros, size);

  lseek(info->user_fd, file_loc+ENTRY_HEADER_SIZE+key_len, SEEK_SET);
  if (write(info->user_fd, zeros, size) < 0) {
    free(zeros);
    sodium_mprotect_noaccess(info);
    return 4;
  }

  uint8_t file_hash[HASH_SIZE];
  internal_hash_file(info, (uint8_t*) &file_hash, 0);
  lseek(info->user_fd, 0, SEEK_END);
  if (write(info->user_fd, &file_hash, HASH_SIZE) < 0) {
    fputs("Could not write hash to disk\n", stderr);
    sodium_mprotect_noaccess(info);
    return VE_IOERR;
  }

  free(zeros);
  sodium_mprotect_noaccess(info);
  fputs("Deleted key\n", stderr);
  return 0;
}

/**
   function update_key
 */
int update_key(struct vault_info* info,
               uint8_t type,
               const char* key,
               const char* value) {
  if (info == NULL || key == NULL || value == NULL ||
      strlen(value) > DATA_SIZE || strlen(key) > BOX_KEY_SIZE - 1) {
    return 2;
  }

  delete_key(info, key);
  add_key(info, type, key, value);
}

char* UNSAFE_get_current_value(struct vault_info* info) {
  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return NULL;
  }
  char* result = malloc(info->current_box.val_len + 1);
  strncpy(result, (char*) &info->current_box.value, info->current_box.val_len);
  result[info->current_box.val_len] = 0;

  sodium_mprotect_noaccess(info);
  return result;
}

int main(int argc, char** argv) {
  if (argc != 4) {
    fputs("Wrong inputs\n", stderr);
    return 1;
  }

  printf("Smoke\n");
  struct vault_info* vault = init_vault();
  create_vault(argv[1], argv[2], argv[3], vault);
  close_vault(vault);
  open_vault(argv[1], argv[2], argv[3], vault);
  add_key(vault, 65, "aldenperrine", "password");
  add_key(vault, 65, "devenpatel", "password");
  add_key(vault, 65, "kevinli", "password");
  delete_key(vault, "kevinli");
  char** keys = get_vault_keys(vault);
  uint32_t num_keys = num_vault_keys(vault);
  for(uint32_t i = 0; i < num_keys; ++i) {
    open_key(vault, keys[i]);
    char* value = UNSAFE_get_current_value(vault);
    uint64_t time = last_modified_time(vault, keys[i]);
    printf("\t%s\t%s\t%ld\n", keys[i], value, time);
    free(keys[i]);
    free(value);
  }
  free(keys);
  close_vault(vault);

  open_vault(argv[1], argv[2], argv[3], vault);
  update_key(vault, 65, "aldenperrine", "newpass");
  keys = get_vault_keys(vault);
  num_keys = num_vault_keys(vault);
  for(uint32_t i = 0; i < num_keys; ++i) {
    open_key(vault, keys[i]);
    char* value = UNSAFE_get_current_value(vault);
    printf("\t%s\t%s\n", keys[i], value);
    free(keys[i]);
    free(value);
  }
  free(keys);
  close_vault(vault);

  open_vault(argv[1], argv[2], argv[3], vault);
  for(uint32_t i = 0; i < 120; ++i) {
    char keyname[10];
    snprintf(keyname, 10, "user%i", i);
    add_key(vault, 65,(const char*) &keyname, "somepass");
  }
  close_vault(vault);

  open_vault(argv[1], argv[2], argv[3], vault);
  keys = get_vault_keys(vault);
  num_keys = num_vault_keys(vault);
  printf("%d\n", num_keys);
  for(uint32_t i = 0; i < num_keys; ++i) {
    open_key(vault, keys[i]);
    char* value = UNSAFE_get_current_value(vault);
    printf("\t%s\t%s\n", keys[i], value);
    free(keys[i]);
    free(value);
  }
  free(keys);
  close_vault(vault);
  release_vault(vault);
  return 0;
}
