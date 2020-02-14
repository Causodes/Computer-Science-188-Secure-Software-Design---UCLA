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

    @abstractmethod
    def initialize():
        raise NotImplementedError

    @abstractmethod
    def deinitialize():
        raise NotImplementedError

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
    def add_key(self, value_type, key, value):
        raise NotImplementedError

    # Method for retrieving a value from the vault
    @abstractmethod
    def get_value(self, key):
        raise NotImplementedError

    # Method for updating a value in the vault
    @abstractmethod
    def update_value(self, value_type, key, value):
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

    @abstractmethod
    def last_updated_time(self, key):
        raise NotImplementedError

    @abstractmethod
    def get_encrypted_value(self, key):
        raise NotImplementedError

    @abstractmethod
    def add_encrypted_value(self, type_, key, encrypted_value):
        raise NotImplementedError


"""
Implementation of the Vault

All of this is effictively a wrapper to the C library

Assumes the shared library built is in the same directory

Type 0 is bytes, Type 1 is ascii

"""

class Vault(Vault_intf):
    def __init__(self):
        self.vault_lib = CDLL("./vault_lib.so")
        self.vault = c_void_p(0)
        self.data_size = 0;
        self.initialize()


    def initialize(self):
        self.vault_lib.init_vault.restype = POINTER(c_ulonglong)
        self.vault_lib.create_vault.argtypes = [c_char_p, c_char_p, c_char_p, POINTER(c_ulonglong)]
        self.vault_lib.open_vault.argtypes = [c_char_p, c_char_p, c_char_p, POINTER(c_ulonglong)]
        self.vault_lib.close_vault.argtypes = [POINTER(c_ulonglong)]
        self.vault_lib.last_modified_time.restype = c_ulonglong
        self.vault_lib.get_last_server_time.restype = c_ulonglong
        self.vault_lib.set_last_server_time.argtypes = [POINTER(c_ulonglong), c_ulonglong]
        self.vault = self.vault_lib.init_vault()
        self.data_size = self.vault_lib.max_value_size()


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


    def add_key(self, value_type, key, value):
        key_param = key.encode('ascii')
        if value_type == 1:
            value_param = value.encode('ascii')
        else:
            value_param = value
        type_param = c_byte(value_type)
        return self.vault_lib.add_key(self.vault, type_param, key_param, value_param)


    def get_value(self, key):
        key_param = key.encode('ascii')
        res = self.vault_lib.open_key(self.vault, key_param)
        if res != 0:
            return (-1, "")
        value = create_string_buffer(self.data_size)
        value_length = c_int(0);
        type_ = c_byte(0)
        res = self.vault_lib.place_open_value(self.vault, value, byref(value_length), byref(type_))
        if res != 0:
            return (-1, "")
        if type_.value == 1:
            ret_val = value.value.decode('ascii')
        else:
            ret_val = value[0:value_length.value]
        return (type_.value, ret_val)


    def update_value(self, value_type, key, value):
        key_param = key.encode('ascii')
        if value_type == 1:
            value_param = value.encode('ascii')
        else:
            value_param = value
        type_param = c_byte(value_type)
        return self.vault_lib.update_key(self.vault, type_param, key_param, value_param)


    def delete_value(self, key):
        key_param = key.encode('ascii')
        return self.vault_lib.delete_key(self.vault, key_param)


    def last_updated_time(self, key):
        key_param = key.encode('ascii')
        return self.vault_lib.last_modified_time(self.vault, key_param)


    def change_password(self, old_password, new_password):
        old_param = old_password.encode('ascii')
        new_param = new_password.encode('ascii')
        return self.vault_lib.change_password(self.vault, old_param, new_param)

    def get_encrypted_value(self, key):
        key_param = key.encode('ascii')
        value = create_string_buffer(self.data_size+40)
        value_length = c_int(0);
        type_ = c_byte(0)
        res = self.vault_lib.get_encrypted_value(self.vault, key_param, value, byref(value_length), byref(type_))
        if res != 0:
            return (-1, "")
        return (type_.value, value[0:value_length.value])

    def get_vault_keys(self):
        num_keys = self.vault_lib.num_vault_keys(self.vault)
        ret_type = POINTER(c_char) * num_keys
        ret_val = ret_type()
        for i in range(num_keys):
            ret_val[i] = create_string_buffer(130)
        res = self.vault_lib.get_vault_keys(self.vault, ret_val)
        if res != 0:
            return (res, [])
        python_strings = []
        for i in range(num_keys):
            python_strings.append(string_at(ret_val[i]).decode('ascii'))
        return (res, python_strings)


    def add_encrypted_value(self, type_, key, encrypted_value):
        key_param = key.encode('ascii')
        val_length = c_int(len(encrypted_value))
        type_param = c_byte(type_)
        return self.vault_lib.add_encrypted_value(self.vault, key_param, encrypted_value, val_length, type_param)


    def get_last_contact_time(self):
        return self.vault_lib.get_last_server_time(self.vault)

    def set_last_contact_time(self, timestamp):
        return self.vault_lib.set_last_server_time(self.vault, timestamp)

Vault_intf.register(Vault)

if __name__ == "__main__":
    v = Vault()
    v.create_vault("./", "test", "password")
    print(v.add_key(1, "google", "oldpass"))
    print(v.last_updated_time("google"))
    print(v.get_value("google"))
    print(v.update_value(1, "google", "newpass"))
    update_time = v.last_updated_time("google")
    print(update_time)
    print(v.change_password("password", "str0nkp@ssw0rd"))
    print(v.close_vault())
    print(v.open_vault("./", "test", "str0nkp@ssw0rd"))
    print(v.get_value("google"))
    type_, en_val = v.get_encrypted_value("google")
    print(v.delete_value("google"))
    print(v.get_value("google"))
    print(v.add_encrypted_value(type_, "google", en_val))
    print(v.get_value("google"))
    print(v.add_key(1, "amazon", "anotherpass"))
    print(v.add_key(1, "facebook", "morepasses"))
    res, keys = v.get_vault_keys()
    for i in range(len(keys)):
        print(keys[i])

    print(v.set_last_contact_time(update_time))
    print(v.get_last_contact_time())
    v.close_vault()
