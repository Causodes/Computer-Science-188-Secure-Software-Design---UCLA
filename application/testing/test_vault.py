"""
A test implementation of the vault to be used in unit tests for the bank

DO NOT USE IN PROD
This is a simple dict that keeps everything in Python's memory, which
is neither stateful among reboots nor has any inbuilt security.

Contains smoke tests for the test itself.

"""

from vault import *
from dataclasses import dataclass
import time

@dataclass
class TestVaultData:
    password: str
    vault: dict

class TestVault(Vault_intf):
    def __init__(self):
        self.internal_vaults = { "testuser" :
                                 TestVaultData(password="password",
                                               vault = {"amazon.com":("pass", 1580757288)})}
        self.current_vault = None

    def create_vault(self, directory, username, password):
        if username not in self.internal_vaults.keys():
            self.internal_vaults[username] = TestVaultData(password, vault={})
            return True
        else:
            return False

    def open_vault(self, diretory, username, password):
        if self.current_vault is not None:
            return False
        elif username not in self.internal_vaults.keys():
            return False
        elif self.internal_vaults[username].password != password:
            return False
        else:
            self.current_vault = self.internal_vaults[username].vault
            return True

    def close_vault(self):
        self.current_vault = None

    def __get_current_time(self):
        return time.time() * 1000

    def add_key(self, key, value):
        if self.current_vault is None:
            return False
        if key in self.current_vault.keys():
            return False
        else:
            self.current_vault[key] = (value, __get_current_time())
            return True

    def get_value(self, key):
        if self.current_vault is None:
            return None
        if key not in self.current_vault.keys():
            return None
        else:
            return self.current_vault[key][0]

    def update_value(self, key, value):
        if self.current_vault is None:
            return False
        if key not in self.current_vault.keys():
            return False
        else:
            self.current_vault[key] = (value, __get_current_time())
            return True

    def delete_value(self, key):
        if self.current_vault is None:
            return False
        else:
            dict.pop(key, None)
            return True

    def last_updated_time(self, key):
        raise NotImplementedError

    def change_password(self, old_password, new_password):
        raise NotImplementedError

    def validate_vault(self):
        raise NotImplementedError

