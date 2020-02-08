#include "vault_map.h"

// C libraries
#include <fcntl.h>
#include <errno.h>
#include <sodium.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/resource.h>
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

// TODO aldenperrine: Hash entire file and loc data for integrity
// TODO aldenperrine: Write and check if interuption of data writing

/**
   vault_box - struct to hold an entry within the vault
 */
struct vault_box {
  char key[BOX_KEY_SIZE];
  char type;
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
#define WRITE(fd, addr, len, info) do { if (write(fd, addr, len) < 0) { fputs("Write failed\n", stderr); sodium_mprotect_noaccess(info); return 3; } } while(0)
#define READ(fd, addr, len, info) do { if (read(fd, addr, len) < 0) { fputs("Read failed\n", stderr); sodium_mprotect_noaccess(info); return 3; } } while(0)

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

int release_vault(struct vault_info* info) {
  sodium_mprotect_readwrite(info);
  if (info->is_open)
    close(info->user_fd);
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
int create_vault(char* directory, char* username, char* password, struct vault_info* info) {
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
    return 1;
  }

  if (info->is_open) {
    fputs("Already have a vault open\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 1;
    }
    return 8;
  }

  int open_results = open(pathname, O_RDWR | O_CREAT | O_EXCL | O_DSYNC, S_IRUSR | S_IWUSR);
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
  if (crypto_pwhash(info->derived_key, MASTER_KEY_SIZE, password, strlen(password), salt,
                    crypto_pwhash_OPSLIMIT_MODERATE,
                    crypto_pwhash_MEMLIMIT_MODERATE,
                    crypto_pwhash_ALG_ARGON2ID13) < 0) {
    fputs("Could not dervie password key\n", stderr);
    close(open_results);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 1;
    }
    return 9;
  }

  uint8_t encrypted_master[MASTER_KEY_SIZE+MAC_SIZE];
  uint8_t master_nonce[NONCE_SIZE];
  randombytes_buf(master_nonce, sizeof master_nonce);
  if (crypto_secretbox_easy(encrypted_master, info->decrypted_master,
                            MASTER_KEY_SIZE, master_nonce, info->derived_key) < 0) {
    fputs("Could not encrypt master key\n", stderr);
    close(open_results);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 1;
    }
    return 10;
  }

  uint32_t loc_len = 100;
  uint8_t zeros[100*LOC_SIZE] = { 0 };
  uint8_t version = VERSION;
  WRITE(info->user_fd, &version, 1, info);
  WRITE(info->user_fd, &zeros, 7, info);
  WRITE(info->user_fd, &salt, crypto_pwhash_SALTBYTES, info);
  WRITE(info->user_fd, &encrypted_master, MASTER_KEY_SIZE+MAC_SIZE, info);
  WRITE(info->user_fd, &master_nonce, NONCE_SIZE, info);
  WRITE(info->user_fd, &loc_len, 4, info);
  WRITE(info->user_fd, &zeros, loc_len*LOC_SIZE, info);

  info->key_info = init_map(100);
  info->current_box.key[0] = 0;
  info->is_open = 1;

  if (sodium_mprotect_noaccess(info) < 0) {
    fputs("Issues preventing access to memory\n", stderr);
  }

  fputs("Created file successfully\n", stderr);
  return 0;
}

int open_vault(char* directory, char* username, char* password, struct vault_info* info) {
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

  int open_results = open(pathname, O_RDWR | O_NOFOLLOW);

  lseek(open_results, 8, SEEK_SET);
  int open_info_length = SALT_SIZE+MAC_SIZE+MASTER_KEY_SIZE+NONCE_SIZE;
  uint8_t open_info[open_info_length];
  READ(open_results, open_info, open_info_length, info);

  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    close(open_results);
    return 1;
  }
  info->user_fd = open_results;

  if (crypto_pwhash(info->derived_key, MASTER_KEY_SIZE, password, strlen(password), open_info,
                    crypto_pwhash_OPSLIMIT_MODERATE,
                    crypto_pwhash_MEMLIMIT_MODERATE,
                    crypto_pwhash_ALG_ARGON2ID13) < 0) {
    fputs("Could not dervie password key\n", stderr);
    close(open_results);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 1;
    }
    return 5;
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
      return 1;
    }
    return 6;
  }

  uint32_t loc_len;
  READ(info->user_fd, &loc_len, 4, info);
  uint32_t loc_data[LOC_SIZE/sizeof(uint32_t)];
  info->key_info = init_map(loc_len/2);
  for (uint32_t next_loc = 0; next_loc < loc_len; ++next_loc) {
    READ(info->user_fd, &loc_data, LOC_SIZE, info);
    uint16_t is_active = *(((uint16_t *) &loc_data) + 1);
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
    lseek(info->user_fd, 7, SEEK_CUR);
    READ(info->user_fd, &key, key_len, info);
    key[key_len] = 0;

    add_entry(info->key_info, key, current_info);
    lseek(info->user_fd, HEADER_SIZE+(next_loc+1)*LOC_SIZE, SEEK_SET);
  }

  info->is_open = 1;

  if (sodium_mprotect_noaccess(info) < 0) {
    fputs("Issues preventing access to memory\n", stderr);
  }

  fputs("Opened the vault\n", stderr);
  return 0;
}

int close_vault(struct vault_info* info) {
  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return 1;
  }

  if (!info->is_open) {
    fputs("Already have a vault closed\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 1;
    }
    return 2;
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
  return 0;
}

int add_key(struct vault_info* info, uint8_t type, const char* key, const char* value) {
  if (info == NULL || key == NULL || value == NULL ||
      strlen(value) > DATA_SIZE || strlen(key) > BOX_KEY_SIZE) {
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

  if (get_info(info->key_info, key)) {
    fputs("Key already in map; use update\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
    }
    return 3;
  }

  lseek(info->user_fd, HEADER_SIZE-4, SEEK_SET);
  uint32_t loc_len;
  READ(info->user_fd, &loc_len, 4, info);
  uint32_t loc_data[LOC_SIZE/sizeof(uint32_t)];

  for (uint32_t next_loc = 0; next_loc < loc_len; ++next_loc) {
    READ(info->user_fd, &loc_data, LOC_SIZE, info);
    if (loc_data[0]) {
      continue;
    }

    uint32_t file_loc = lseek(info->user_fd, file_loc, SEEK_END);
    uint32_t key_len = strlen(key);
    uint32_t val_len = strlen(value);
    uint32_t inode_loc = HEADER_SIZE+next_loc*LOC_SIZE;

    // TODO aldenperrine: implement time stuff
    uint64_t m_time = 0;

    int input_len = 9+key_len+val_len+MAC_SIZE+NONCE_SIZE+HASH_SIZE;
    uint8_t* to_write_data = malloc(input_len);
    *((uint64_t*) to_write_data) = m_time;
    to_write_data[8] = type;
    strncpy(to_write_data+9, key, key_len);

    uint8_t* val_nonce = to_write_data+input_len-NONCE_SIZE-HASH_SIZE;
    randombytes_buf(val_nonce, NONCE_SIZE);

    if (crypto_secretbox_easy(to_write_data+9+key_len, value,
                              val_len, val_nonce, info->decrypted_master) < 0) {
      fputs("Could not encrypt value for key value pair\n", stderr);
      free(to_write_data);
      if (sodium_mprotect_noaccess(info) < 0) {
        fputs("Issues preventing access to memory\n", stderr);
      }
      return 10;
    }

    crypto_generichash(to_write_data+input_len-HASH_SIZE, HASH_SIZE,
                       to_write_data, input_len-HASH_SIZE, NULL, 0);

    if (write(info->user_fd, to_write_data, input_len) < 0) {
      fputs("Could not write key-value pair to disk\n", stderr);
      free(to_write_data);
      sodium_mprotect_noaccess(info);
      return 3;
    }

    loc_data[0] = (1 << 16) | 1;
    loc_data[1] = file_loc;
    loc_data[2] = key_len;
    loc_data[3] = val_len;
    lseek(info->user_fd, inode_loc, SEEK_SET);

    if (write(info->user_fd, loc_data, LOC_SIZE) < 0) {
      fputs("Could not write inode pair to disk\n", stderr);
      free(to_write_data);
      sodium_mprotect_noaccess(info);
      return 3;
    }

    struct key_info*  current_info = malloc(sizeof(struct key_info));
    current_info->inode_loc = inode_loc;
    current_info->m_time = m_time;
    current_info->type = type;

    add_entry(info->key_info, key, current_info);
    free(to_write_data);
    sodium_mprotect_noaccess(info);

    fputs("Added key\n", stderr);
    return 0;
  }


  // TODO aldenperrine: do file movement increase stuff
  return 6;
}

/**
   TODO aldenperrine: create these methods

   get_keys

   open_key

   update_key

   delete_key

   last_modified_time
 */

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
  printf("%d\n", add_key(vault, 65, "aldenperrine", "password"));
  close_vault(vault);
  release_vault(vault);
  return 0;
}
