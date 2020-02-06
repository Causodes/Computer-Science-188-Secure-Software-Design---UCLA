#include "vault_map.h"

// C libraries
#include <fcntl.h>
#include <errno.h>
#include <sodium.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
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
  char decrypted_master[MASTER_KEY_SIZE];
  struct vault_box current_box;
  struct vault_map* key_info;
};

const char* filename_pattern = "%s/%s.vault";

struct vault_info* init_vault() {
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

  int open_results = open(pathname, O_RDWR | O_CREAT | O_EXCL, S_IRUSR | S_IWUSR);
  if (open_results < 0) {
    if (errno == EEXIST) {
      return 3;
    } else if (errno == EACCES) {
      return 4;
    } else {
      return 5;
    }
  }

  // TODO aldenperrine: Create file in correct file

  return 0;
}

/**
   TODO aldenperrine: create these methods

   open_vault

   close_vault

   get_keys

   add_key

   open_key

   update_key

   delete_key

   last_modified_time
 */

int main(int argc, char** argv) {
  printf("Smoke\n");
  return 0;
}
