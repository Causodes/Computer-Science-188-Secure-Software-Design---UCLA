#include <stdint.h>

#define VERSION 1
#define HASH_SIZE 32       // Okay to use small hash size as only for hash table
#define MAX_PATH_LEN 4096  // Max path length for finding files
#define BOX_KEY_SIZE 120   // Max length of key in vault
#define MAX_USER_SIZE 80   // Max username size
#define ENTRY_HEADER_SIZE 9

#define STATE_UNUSED 0
#define STATE_ACTIVE ((1 << 16) | 1)
#define STATE_DELETED 1

#define VE_SUCCESS 0
#define VE_MEMERR 1
#define VE_PARAMERR 2
#define VE_IOERR 3
#define VE_CRYPTOERR 4
#define VE_VOPEN 5
#define VE_VCLOSE 6

struct key_info {
  uint64_t m_time;
  uint32_t inode_loc;
  uint8_t type;
};

struct vault_map;

struct vault_map* init_map(uint32_t);

void delete_map(struct vault_map*);

uint8_t add_entry(struct vault_map*, const char*, struct key_info*);

struct key_info* get_info(struct vault_map*, const char*);

uint8_t delete_entry(struct vault_map*, const char*);

char** get_keys(struct vault_map*);

uint32_t num_keys(struct vault_map*);
