#include "vault_map.h"

#include <stdint.h>
#include <sodium.h>
#include <stdlib.h>
#include <string.h>

struct node {
  struct node* next_node;
  char key[BOX_KEY_SIZE];
  struct key_info* info;
};

struct vault_map {
  uint32_t size;
  uint32_t num_entries;
  struct node** node_table;
};

struct vault_map* init_map(uint32_t size) {
  struct vault_map* map = malloc(sizeof(struct vault_map));
  map->size = size;
  map->num_entries = 0;
  map->node_table = malloc(sizeof(struct node)*size);
  for(uint32_t i = 0; i < size; ++i) {
    map->node_table[i] = NULL;
  }
  return map;
}

void delete_map(struct vault_map* map) {
  for(uint32_t i = 0; i < map->size; ++i) {
    if (!map->node_table[i]) {
      continue;
    }

    struct node* bucket = map->node_table[i];
    while(bucket) {
      free(bucket->info);
      struct node* temp = bucket->next_node;
      free(bucket);
      bucket = temp;
    }
  }
  free(map->node_table);
  free(map);
}

// https://crypto.stackexchange.com/questions/2043/
uint32_t hash_func(const char* key, uint32_t size) {
  uint8_t hash[HASH_SIZE];
  size_t key_length = strlen(key);
  if (key_length > BOX_KEY_SIZE) {
    exit(1);
  }
  crypto_generichash(hash, sizeof hash, (uint8_t *) key,
		     key_length, NULL, 0);

  // This is safe as the entire hash is distributed equally
  // Creates a slightly higher probablity of collision
  // Okay because its used in a hash table
  uint64_t* converted_hash = (uint64_t*) &hash;
  return (*converted_hash) % size;
}

// Expects that info is malloced
uint8_t add_entry(struct vault_map* map, const char* key,
		  struct key_info* info) {
  if (map == NULL || key == NULL || info == NULL) {
    return 1;
  }
  if (strlen(key) > BOX_KEY_SIZE) {
    return 2;
  }
  uint32_t bucket_num = hash_func(key, map->size);
  struct node** where_to_place = &(map->node_table[bucket_num]);
  struct node* bucket = map->node_table[bucket_num];
  while(bucket) {
    if (strncmp(bucket->key, key, BOX_KEY_SIZE) == 0) {
      return 3;
    }
    where_to_place = &bucket->next_node;
    bucket = bucket->next_node;
  }
  bucket = malloc(sizeof(struct node));
  bucket->next_node = NULL;
  strncpy(bucket->key, key, BOX_KEY_SIZE);
  bucket->info = info;
  *where_to_place = bucket;
  (map->num_entries)++;
  return 0;
}

// Do not delete result, shared pointer
struct key_info* get_info(struct vault_map* map, const char* key) {
  if (map == NULL || key == NULL) {
    return NULL;
  }
  if (strlen(key) > BOX_KEY_SIZE) {
    return NULL;
  }
  uint32_t bucket_num = hash_func(key, map->size);
  struct node* bucket = map->node_table[bucket_num];
  while(bucket) {
    if (strncmp(bucket->key, key, BOX_KEY_SIZE) == 0) {
      return bucket->info;
    }
    bucket = bucket->next_node;
  }
  return NULL;
}

uint8_t delete_entry(struct vault_map* map, const char* key) {
  if (map == NULL || key == NULL) {
    return 1;
  }
  if (strlen(key) > BOX_KEY_SIZE) {
    return 2;
  }
  uint32_t bucket_num = hash_func(key, map->size);
  struct node** where_to_place = &(map->node_table[bucket_num]);
  struct node* bucket = map->node_table[bucket_num];
  while(bucket) {
    if (strncmp(bucket->key, key, BOX_KEY_SIZE) == 0) {
      *where_to_place = bucket->next_node;
      free(bucket->info);
      free(bucket);
      (map->num_entries)--;
      return 0;
    }
    where_to_place = &bucket->next_node;
    bucket = bucket->next_node;
  }
  return 0;
}

char** get_keys(struct vault_map* map) {
  if (map == NULL) {
    return NULL;
  }
  char** keys = malloc(sizeof(char*)*(map->num_entries));
  uint32_t key_index = 0;
  for (uint32_t bucket_index = 0; bucket_index < map->size; ++bucket_index) {
    struct node* bucket = map->node_table[bucket_index];
    while(bucket) {
      keys[key_index] = malloc((strlen(bucket->key)+1)*sizeof(char));
      strcpy(keys[key_index++], bucket->key);
      bucket = bucket->next_node;
    }
  }
  return keys;
}

uint32_t num_keys(struct vault_map* map) {
  return map->num_entries;
}

int main(int argc, char** argv) {
  if (sodium_init() < 0) {
    printf("Could not initialize libsoidum\n");
    exit(1);
  }

  if (argc == 1) {
    printf("Wrong inputs\n");
    exit(1);
  }

  uint8_t result;
  uint32_t size = 10;
  struct vault_map * map = init_map(size);

  for (int i = 1; i < argc; ++i) {
    char* key = argv[i];
    struct key_info* info = malloc(sizeof(struct key_info));
    info->type = 1;
    info->last_modified_time = 100;
    info->inode_loc = 120;

    if((result = add_entry(map, key, info))) {
      printf("Adding returned %d\n", result);
      exit(1);
    }

    const struct key_info* res_info = get_info(map, key);
  }

  for (int i = 1; i < argc; ++i) {
    char* key = argv[i];
    const struct key_info* res_info = get_info(map, key);
  }

  char** keys = get_keys(map);
  uint8_t key_count = num_keys(map);

  for (uint32_t i = 0; i < key_count; ++i) {
    printf("%s\n", keys[i]);
  }

  delete_map(map);
  return 0;
}
