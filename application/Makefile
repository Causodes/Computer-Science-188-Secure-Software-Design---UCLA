default: vault

vault: vault.o
	gcc -shared -Wall -Wextra -Werror -fstack-protector-all -o vault_lib.so -fPIC vault.o vault_map.o -lsodium

vault.o: vault_map.o vault.c
	gcc -c -o vault.o vault.c -fPIC

vault_map.o: vault_map.c
	gcc -c -o vault_map.o vault_map.c -fPIC
