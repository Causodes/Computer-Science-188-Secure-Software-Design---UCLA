#include <stdint.h>

#define VERSION 1
#define HASH_SIZE 32 // Okay to use small hash size as only for hash table
#define MAX_PATH_LEN 4096 // Max path length for finding files
#define MAX_PASS_SIZE 256 // Max password size
#define MASTER_KEY_SIZE 32 // 256-bit key for XSalsa20
#define SALT_SIZE 16 // Should be same as crypto_pwhash_SALTBYTES
#define MAC_SIZE 16 // Should be same as crypto_secretbox_MACBYTES
#define NONCE_SIZE 24 // Should be same as crypto_secretbox_NONCEBYTES
#define HEADER_SIZE 8+MASTER_KEY_SIZE+SALT_SIZE+MAC_SIZE+NONCE_SIZE+4
#define LOC_SIZE 16 // Number of bytes each entry is in the loc field
#define BOX_KEY_SIZE 120 // Max length of key in vault
#define DATA_SIZE 4096 // Max size of binary data stored
#define MAX_USER_SIZE 80 // Max username size
#define ENTRY_HEADER_SIZE 9
#define INITIAL_SIZE 100
#define STATUS_WRITING (char) 1
#define STATUS_STABLE (char) 0

struct key_info {
  uint64_t m_time;
  uint32_t inode_loc;
  uint8_t type;
};

struct vault_map;

struct vault_map* init_map(uint32_t);

void delete_map(struct vault_map*);

uint8_t add_entry(struct vault_map*,
                  const char*,
                  struct key_info*);

struct key_info* get_info(struct vault_map*, const char*);

uint8_t delete_entry(struct vault_map*, const char*);

char** get_keys(struct vault_map*);

uint32_t num_keys(struct vault_map*);
