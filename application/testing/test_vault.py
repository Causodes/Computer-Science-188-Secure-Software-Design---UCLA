"""
A test implementation of the vault to be used in unit tests for the bank

DO NOT USE IN PROD
This is a simple dict that keeps everything in Python's memory, which
is neither stateful among reboots nor has any inbuilt security.

Contains smoke tests for the test itself.

"""
import sys
sys.path.insert(1, "../")


from vault import *
from dataclasses import dataclass
import time

@dataclass
class TestVaultData:
    password: str
    vault: dict

testuser = "testuser"
testpass = "password"
testtime = 1580757288

class TestVault(Vault_intf):
    def __init__(self):
        self.internal_vaults = { testuser : TestVaultData(password = testpass,
                                                          vault = {"amazon.com":("pass", testtime)})}
        self.current_vault = None
        self.current_password = None

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
            self.current_password = self.internal_vaults[username].password
            return True

    def close_vault(self):
        self.current_vault = None
        self.current_password = None

    @staticmethod
    def __get_current_time():
        return time.time() * 1000

    def add_key(self, key, value):
        if self.current_vault is None:
            return False
        if key in self.current_vault.keys():
            return False
        else:
            self.current_vault[key] = (value, TestVault.__get_current_time())
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
            self.current_vault[key] = (value, TestVault.__get_current_time())
            return True

    def delete_value(self, key):
        if self.current_vault is None:
            return False
        else:
            self.current_vault.pop(key, None)
            return True

    def last_updated_time(self, key):
        if self.current_vault is None:
            return None
        if key not in self.current_vault.keys():
            return None
        else:
            return self.current_vault[key][1]

    def change_password(self, old_password, new_password):
        if self.current_vault is None:
            return False
        elif old_password != self.current_password:
            return False
        else:
            return True

    def validate_vault(self):
        return True


def test_vault_smoke_test():
    print("Beginning smoke test of the TestVault...")
    test = TestVault()
    user = "someone"
    password = "weakpass"

    # Test creating vaults
    assert test.create_vault("", testuser, "") == False, "Overwrote someones vault"
    assert test.create_vault("", user, password) == True, "Could not make new vault"

    # Test opening vaults
    assert test.open_vault("", testuser, testpass) == True, "Could not open vault"
    assert test.open_vault("", user, password) == False, "Multiple openings allowed"
    test.close_vault()
    assert test.open_vault("", user, password) == True, "Cannot open after close"

    # Test using test vault as key-value store
    assert test.add_key("accounts.google.com", "somepass") == True, "Could not add password"
    assert test.add_key("accounts.google.com", "otherpass") == False, "Does not stop adding twice"
    assert test.get_value("accounts.google.com") == "somepass", "Wrong vaule returned"
    assert test.get_value("amazon.com") == None, "Returned non-existent value"
    assert test.update_value("accounts.google.com", "new_pass") == True, "Could not update"
    assert test.update_value("amazon.com", "pass") == False, "Updated non-existent value"
    assert test.get_value("accounts.google.com") == "new_pass", "Did not update value"
    assert test.delete_value("accounts.google.com") == True, "Could not remove value"

    # Test password change
    assert test.change_password(password, "otherpass") == True, "Could not change password"
    print("Finished smoke test successfully")


if __name__ == "__main__":
    test_vault_smoke_test()
