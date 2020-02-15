default: clean vault

CCFLAGS = -fPIC

debug: CCFLAGS += -D VAULT_DEBUG
debug: clean vault

vault: vault.o
	@gcc -shared -Wall -Wextra -Werror -fstack-protector-all -o vault_lib.so -fPIC vault.o vault_map.o -lsodium

vault.o: vault_map.o vault.c
	@gcc -c -o vault.o vault.c $(CCFLAGS)

vault_map.o: vault_map.c
	@gcc -c -o vault_map.o vault_map.c $(CCFLAGS)

clean:
	@rm -f vault.o vault_map.o vault_lib.so
