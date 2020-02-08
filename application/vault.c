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
   4 8-byte chunks that specify the start of key-value pair, the key length,
   the value length, and whether the section is currently being used.
   The used field is to allow for quick deletions, which will wipe the encrypted
   values but not move around the rest of the data in the file. The number of
   deleted entries can then be banked up until there is a sufficient amount
   to condense many at once.

   LENGTH | USED1 | LOC1 | KEY_LEN1 | VAL_LEN1 | USED2 | LOC2 | KEY_LEN2 | ...
      4       4      4        4          4         4      4        4

   Finally in the file comes the key value pairs, the actual data being stored.
   This section should be aligned at an 8 byte values, with the key and value
   pieces being aligned. The format for a single instance is as follows:

   MTIME | TYPE | BUF |  KEY  | BUF | E_VAL | VAL_MAC | BUF | HASH
     8      1      7     KLEN    V     VLEN     24       V     32

   The buffer lengths can vary, if more metadata is necessary for the first one,
   and the second and third can vary according to what is necessary to algin
   the rest of the components at 8 byte chunks.

 */

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
}

int create_vault(char* directory, char* username, char* password, struct vault_info* info) {
  if (directory == NULL || username == NULL || password == NULL ||
      strlen(directory) > MAX_PATH_LEN || strlen(username) > MAX_USER_SIZE
      || strlen(password) > MAX_PASS_SIZE) {
    return 1;
  }

  int max_size = strlen(directory)+strlen(username)+10;
  char* pathname = malloc(max_size);
  if (snprintf(pathname, max_size, filename_pattern, directory, username) < 0) {
    return 2;
  }

  int open_results = open(pathname, O_RDWR | O_CREAT | O_EXCL | O_DSYNC, S_IRUSR | S_IWUSR);
  if (open_results < 0) {
    if (errno == EEXIST) {
      return 3;
    } else if (errno == EACCES) {
      return 4;
    } else {
      return 5;
    }
  }

  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return 6;
  }

  if (info->is_open) {
    fputs("Already have a vault open\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 6;
    }
    return 7;
  }

  info->is_open = 1;
  info->user_fd = open_results;
  crypto_secretbox_keygen(info->decrypted_master);

  uint8_t salt[crypto_pwhash_SALTBYTES];
  randombytes_buf(salt, sizeof salt);
  if (crypto_pwhash(info->derived_key, MASTER_KEY_SIZE, password, strlen(password), salt,
                    crypto_pwhash_OPSLIMIT_INTERACTIVE,
                    crypto_pwhash_MEMLIMIT_INTERACTIVE,
                    crypto_pwhash_ALG_ARGON2ID13) < 0) {
    fputs("Could not dervie password key\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 6;
    }
    return 8;
  }

  uint8_t encrypted_master[crypto_secretbox_MACBYTES+MASTER_KEY_SIZE];
  uint8_t master_nonce[crypto_secretbox_NONCEBYTES];
  randombytes_buf(master_nonce, sizeof master_nonce);
  if (crypto_secretbox_easy(encrypted_master, info->decrypted_master,
                            MASTER_KEY_SIZE, master_nonce, info->derived_key) < 0) {
    fputs("Could not encrypt master key\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 6;
    }
    return 9;
  }

  uint8_t zeros[300] = {0};
  uint8_t version = VERSION;
  write(info->user_fd, &version, 1);
  write(info->user_fd, &zeros, 7);
  write(info->user_fd, &salt, crypto_pwhash_SALTBYTES);
  write(info->user_fd, &encrypted_master, crypto_secretbox_MACBYTES+MASTER_KEY_SIZE);
  write(info->user_fd, &master_nonce, crypto_secretbox_NONCEBYTES);
  uint32_t loc_len = 100;
  write(info->user_fd, &loc_len, 4);
  write(info->user_fd, &zeros, loc_len*3);

  info->key_info = init_map(100);
  info->current_box.key[0] = 0;
  info->is_open = 1;

  if (sodium_mprotect_noaccess(info) < 0) {
    fputs("Issues preventing access to memory\n", stderr);
    return 6;
  }

  fputs("Created file successfully\n", stderr);
  return 0;
}

int open_vault(char* directory, char* username, char* password, struct vault_info* info) {
  if (directory == NULL || username == NULL || password == NULL ||
      strlen(directory) > MAX_PATH_LEN || strlen(username) > MAX_USER_SIZE
      || strlen(password) > MAX_PASS_SIZE) {
    return 1;
  }

  int max_size = strlen(directory)+strlen(username)+10;
  char* pathname = malloc(max_size);
  if (snprintf(pathname, max_size, filename_pattern, directory, username) < 0) {
    return 2;
  }

  int open_results = open(pathname, O_RDWR | O_NOFOLLOW);

  lseek(open_results, 8, SEEK_SET);
  int open_info_length = crypto_pwhash_SALTBYTES+crypto_secretbox_MACBYTES+MASTER_KEY_SIZE+crypto_secretbox_NONCEBYTES;
  uint8_t open_info[open_info_length];
  read(open_results, open_info, open_info_length);


  if (sodium_mprotect_readwrite(info) < 0) {
    fputs("Issues gaining access to memory\n", stderr);
    return 1;
  }
  info->user_fd = open_results;

  if (crypto_pwhash(info->derived_key, MASTER_KEY_SIZE, password, strlen(password), open_info,
                    crypto_pwhash_OPSLIMIT_INTERACTIVE,
                    crypto_pwhash_MEMLIMIT_INTERACTIVE,
                    crypto_pwhash_ALG_ARGON2ID13) < 0) {
    fputs("Could not dervie password key\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 1;
    }
    return 8;
  }

  if (crypto_secretbox_open_easy(info->decrypted_master,
                                 open_info+crypto_pwhash_SALTBYTES,
                                 MASTER_KEY_SIZE+crypto_secretbox_MACBYTES,
                                 open_info+open_info_length-crypto_secretbox_NONCEBYTES, info->derived_key) < 0) {
    fputs("Could not decrypt master key\n", stderr);
    if (sodium_mprotect_noaccess(info) < 0) {
      fputs("Issues preventing access to memory\n", stderr);
      return 1;
    }
    return 9;
  }

  // TODO aldenperrine: read in keys from file

  info->key_info = init_map(100);
  info->is_open = 1;

  if (sodium_mprotect_noaccess(info) < 0) {
    fputs("Issues preventing access to memory\n", stderr);
    return 1;
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
    return 1;
  }

  fputs("Closed the vault\n", stderr);
  return 0;
}

/**
   TODO aldenperrine: create these methods

   open_vault

   get_keys

   add_key

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
  close_vault(vault);
  release_vault(vault);
  return 0;
}
