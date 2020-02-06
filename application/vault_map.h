#include <stdint.h>

#define VERSION 1

// Okay to use small hash size as only for hash table
#define HASH_SIZE 16
#define MAX_PATH_LEN 4096
#define MAX_PASS_SIZE 256

// 256-bit key for XSalsa20
#define MASTER_KEY_SIZE 32
#define BOX_KEY_SIZE 120
#define DATA_SIZE 4096
#define MAX_USER_SIZE 80

struct key_info {
  uint64_t last_modified_time;
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
