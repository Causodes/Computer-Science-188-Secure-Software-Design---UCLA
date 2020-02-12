"""
Main class which interacts with the underlying C vault

The vault handles the encryption/decryption of pieces of data,
storing them in a file whose location is given by the Bank.

The vault maintains control of its own memory to attempt to
decrease the amount that Python allows the passwords to
exist within memory on their own. The class takes input
in Python, passes it to the low-level C application, and then
returns results.
"""

from abc import *
from ctypes import *

"""
Interface Class for the vault

Create this to allow for dependency injection in tests.
Provides the methods that are required by the Bank.
"""
class Vault_intf(ABC):
    # Method for creating the vault for a user
    @abstractmethod
    def create_vault(self, directory, username, password):
        raise NotImplementedError

    # Method for opening a vault by decrypting the master key
    @abstractmethod
    def open_vault(self, diretory, username, password):
        raise NotImplementedError

    # Method for closing a vault, wiping the associated memory
    @abstractmethod
    def close_vault(self):
        raise NotImplementedError

    # Method for adding a key value pair to the vault
    @abstractmethod
    def add_key(self, key, value):
        raise NotImplementedError

    # Method for retrieving a value from the vault
    @abstractmethod
    def get_value(self, key):
        raise NotImplementedError

    # Method for updating a value in the vault
    @abstractmethod
    def update_value(self, key, value):
        raise NotImplementedError

    # Method for deleting a key value pair in the vault
    @abstractmethod
    def delete_value(self, key):
        raise NotImplementedError

    # Method for checking what the last update time of a key was
    @abstractmethod
    def last_updated_time(self, key):
        raise NotImplementedError

    # Method for re-encrypting the master key with a new password
    @abstractmethod
    def change_password(self, old_password, new_password):
        raise NotImplementedError

    # Method for validating the contents of the vault
    @abstractmethod
    def validate_vault(self):
        raise NotImplementedError


"""
Implementation of the Vault

"""

class Vault(Vault_intf):
    def __init__(self):
        self.vault_lib = CDLL("./vault_lib.so")
        self.vault = c_void_p(0)
        self.initialize()

    def initialize(self):
        self.vault_lib.init_vault.restype = POINTER(c_ulonglong)
        self.vault_lib.create_vault.argtypes = [c_char_p, c_char_p, c_char_p, POINTER(c_ulonglong)]
        self.vault_lib.open_vault.argtypes = [c_char_p, c_char_p, c_char_p, POINTER(c_ulonglong)]
        self.vault_lib.close_vault.argtypes = [POINTER(c_ulonglong)]
        self.vault = self.vault_lib.init_vault()

    def deinitialize(self):
        self.vault_lib.release_vault(self.vault)

    def create_vault(self, directory, username, password):
        dir_param = directory.encode('ascii')
        user_param = username.encode('ascii')
        pass_param = password.encode('ascii')
        return self.vault_lib.create_vault(dir_param, user_param, pass_param, self.vault)

    def open_vault(self, directory, username, password):
        dir_param = directory.encode('ascii')
        user_param = username.encode('ascii')
        pass_param = password.encode('ascii')
        return self.vault_lib.open_vault(dir_param, user_param, pass_param, self.vault)

    def close_vault(self):
        return self.vault_lib.close_vault(self.vault)

    def add_key(self, key, value):
        raise NotImplementedError

    def get_value(self, key):
        raise NotImplementedError

    def update_value(self, key, value):
        raise NotImplementedError

    def delete_value(self, key):
        raise NotImplementedError

    def last_updated_time(self, key):
        raise NotImplementedError

    def change_password(self, old_password, new_password):
        raise NotImplementedError

    def validate_vault(self):
        raise NotImplementedError


Vault_intf.register(Vault)
