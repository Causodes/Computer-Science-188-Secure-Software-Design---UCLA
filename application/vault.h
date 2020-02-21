#ifndef __VAULT_H__
#define __VAULT_H__

#include <stdint.h>

#define VE_SUCCESS 0
#define VE_MEMERR 1
#define VE_PARAMERR 2
#define VE_IOERR 3
#define VE_CRYPTOERR 4
#define VE_VOPEN 5
#define VE_VCLOSE 6
#define VE_SYSCALL 7
#define VE_EXIST 8
#define VE_ACCESS 9
#define VE_KEYEXIST 10
#define VE_FILE 11
#define VE_NOSPACE 12
#define VE_WRONGPASS 13

#define MASTER_KEY_SIZE 32  // 256-bit keys for XSalsa20 and from Argon2id
#define SALT_SIZE 16        // 128-bit salt for Argon2id
#define MAC_SIZE 16         // 128-bit mac from Poly1305
#define NONCE_SIZE 24       // 192-bit nonce for XSalsa 20
#define HEADER_SIZE 8 + MASTER_KEY_SIZE + SALT_SIZE + MAC_SIZE + NONCE_SIZE + 12
#define LOC_SIZE 16          // Number of bytes each entry is in the loc field
#define ENTRY_HEADER_SIZE 9  // One for type, eight for time
#define INITIAL_SIZE 100     // Initial amount of key locs before extension
#define DATA_SIZE 4096       // Maximum data size
#define MAX_PASS_SIZE 120    // Maximum password length

struct vault_info;

struct vault_info* init_vault();

int max_value_size();

int release_vault(struct vault_info* info);

int create_vault(char* directory, char* username, char* password,
                 struct vault_info* info);

int create_from_header(char* directory, char* username, char* password,
                       uint8_t* header, struct vault_info* info);

int open_vault(char* dreictory, char* username, char* password,
               struct vault_info* info);

int close_vault(struct vault_info* info);

int create_data_for_server(struct vault_info* info, uint8_t* response1,
                           uint8_t* response2, uint8_t* first_pass_salt,
                           uint8_t* second_pass_salt, uint8_t* recovery_result,
                           uint8_t* dataencr1, uint8_t* dataencr2,
                           uint8_t* data_salt_11, uint8_t* data_salt_12,
                           uint8_t* data_salt_21, uint8_t* data_salt_22,
                           uint8_t* server_pass);

int create_password_for_server(struct vault_info* info, uint8_t* salt,
                               uint8_t* server_pass);

int make_password_for_server(const char* password, const uint8_t* first_salt,
                             const uint8_t* second_salt, uint8_t* server_pass);

int create_responses_for_server(const uint8_t* response1,
                                const uint8_t* response2,
                                const uint8_t* data_salt_11,
                                const uint8_t* data_salt_12,
                                const uint8_t* data_salt_21,
                                const uint8_t* data_salt_22, uint8_t* dataencr1,
                                uint8_t* dataencr2);

int update_key_from_recovery(struct vault_info* info, const char* directory,
                             const char* username, const uint8_t* response1,
                             const uint8_t* response2, const uint8_t* recovery,
                             const uint8_t* data_salt_1,
                             const uint8_t* data_salt_2,
                             const uint8_t* new_password,
                             uint8_t* new_first_salt, uint8_t* new_second_salt,
                             uint8_t* new_server_pass, uint8_t* new_header);

int add_key(struct vault_info* info, uint8_t type, const char* key,
            const char* value, uint64_t m_time, uint32_t len);

int get_vault_keys(struct vault_info* info, char** results);

uint32_t num_vault_keys(struct vault_info* info);

uint64_t last_modified_time(struct vault_info* info, const char* key);

int open_key(struct vault_info* info, const char* key);

int delete_key(struct vault_info* info, const char* key);

int update_key(struct vault_info* info, uint8_t type, const char* key,
               const char* vaule, uint64_t m_time, uint32_t len);

int change_password(struct vault_info* info, const char* old_password,
                    const char* new_password);

int place_open_value(struct vault_info*, char*, int*, char*);

int add_encrypted_value(struct vault_info* info, const char* key,
                        const char* value, int len, uint8_t type, uint64_t m_time);

int get_encrypted_value(struct vault_info* info, const char* key, char* result,
                        int* len, uint8_t* type);

int get_header(struct vault_info* info, char* result);

uint64_t get_last_server_time(struct vault_info* info);

int set_last_server_time(struct vault_info* info, uint64_t timestamp);

#endif
