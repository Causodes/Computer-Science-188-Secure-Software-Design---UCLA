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
from base64 import *
from ctypes import *
import os
import time
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
        self.data_size = 0
        self.initialize()

    def initialize(self):
        self.vault_lib.init_vault.restype = POINTER(c_ulonglong)
        self.vault_lib.create_vault.argtypes = [
            c_char_p, c_char_p, c_char_p,
            POINTER(c_ulonglong)
        ]
        self.vault_lib.create_from_header.argtypes = [
            c_char_p, c_char_p, c_char_p, c_char_p,
            POINTER(c_ulonglong)
        ]
        self.vault_lib.open_vault.argtypes = [
            c_char_p, c_char_p, c_char_p,
            POINTER(c_ulonglong)
        ]
        self.vault_lib.close_vault.argtypes = [POINTER(c_ulonglong)]
        self.vault_lib.last_modified_time.restype = c_ulonglong
        self.vault_lib.get_last_server_time.restype = c_ulonglong
        self.vault_lib.set_last_server_time.argtypes = [
            POINTER(c_ulonglong), c_ulonglong
        ]
        self.vault = self.vault_lib.init_vault()
        self.data_size = self.vault_lib.max_value_size()

    def deinitialize(self):
        self.vault_lib.release_vault(self.vault)

    def create_vault(self, directory, username, password):
        dir_param = directory.encode('ascii')
        user_param = username.encode('ascii')
        pass_param = password.encode('ascii')
        return self.vault_lib.create_vault(dir_param, user_param, pass_param,
                                           self.vault)

    def open_vault(self, directory, username, password):
        dir_param = directory.encode('ascii')
        user_param = username.encode('ascii')
        pass_param = password.encode('ascii')
        return self.vault_lib.open_vault(dir_param, user_param, pass_param,
                                         self.vault)

    def close_vault(self):
        return self.vault_lib.close_vault(self.vault)

    def add_key(self, value_type, key, value):
        key_param = key.encode('ascii')
        if value_type == 1:
            value_param = value.encode('ascii')
        else:
            value_param = value
        type_param = c_byte(value_type)
        return self.vault_lib.add_key(self.vault, type_param, key_param,
                                      value_param)

    def get_value(self, key):
        key_param = key.encode('ascii')
        res = self.vault_lib.open_key(self.vault, key_param)
        if res != 0:
            return (res, 0, "")
        value = create_string_buffer(self.data_size)
        value_length = c_int(0)
        type_ = c_byte(0)
        res = self.vault_lib.place_open_value(self.vault, value,
                                              byref(value_length), byref(type_))
        if res != 0:
            return (res, 0, "")
        if type_.value == 1:
            ret_val = value.value.decode('ascii')
        else:
            ret_val = value[0:value_length.value]
        return (0, type_.value, ret_val)

    def update_value(self, value_type, key, value):
        key_param = key.encode('ascii')
        if value_type == 1:
            value_param = value.encode('ascii')
        else:
            value_param = value
        type_param = c_byte(value_type)
        return self.vault_lib.update_key(self.vault, type_param, key_param,
                                         value_param)

    def delete_value(self, key):
        key_param = key.encode('ascii')
        return self.vault_lib.delete_key(self.vault, key_param)

    def last_updated_time(self, key):
        key_param = key.encode('ascii')
        ret_val = self.vault_lib.last_modified_time(self.vault, key_param)
        if ret_val < 0:
            return (ret_val, 0)
        return (0, ret_val)

    def change_password(self, old_password, new_password):
        old_param = old_password.encode('ascii')
        new_param = new_password.encode('ascii')
        return self.vault_lib.change_password(self.vault, old_param, new_param)

    def get_encrypted_value(self, key):
        key_param = key.encode('ascii')
        value = create_string_buffer(self.data_size + 40)
        value_length = c_int(0)
        type_ = c_byte(0)
        res = self.vault_lib.get_encrypted_value(self.vault, key_param, value,
                                                 byref(value_length),
                                                 byref(type_))
        if res != 0:
            return (res, 0, "")
        return (0, type_.value, value[0:value_length.value])

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
        return self.vault_lib.add_encrypted_value(self.vault, key_param,
                                                  encrypted_value, val_length,
                                                  type_param)

    def get_last_contact_time(self):
        ret_val = self.vault_lib.get_last_server_time(self.vault)
        if ret_val < 10:
            return (ret_val, 0)
        return (0, ret_val)

    def set_last_contact_time(self, timestamp):
        return self.vault_lib.set_last_server_time(self.vault, timestamp)

    def get_vault_header(self):
        ret_val = create_string_buffer(104)
        res = self.vault_lib.get_header(self.vault, ret_val)
        if res != 0:
            return res, []
        return res, ret_val[0:104]

    def create_vault_from_server_data(self, directory, username, password,
                                      header, encrypted_values):
        dir_param = directory.encode('ascii')
        user_param = username.encode('ascii')
        pass_param = password.encode('ascii')
        res = self.vault_lib.create_from_header(dir_param, user_param,
                                                pass_param, header, self.vault)
        if res != 0:
            return res
        for key, type_, en_val in encrypted_values:
            res = self.add_encrypted_value(type_, key, en_val)
            if res != 0:
                return res
        return 0

    def create_data_for_server(self, response1, response2):
        res1_param = response1.encode('ascii')
        res2_param = response2.encode('ascii')
        salt1 = create_string_buffer(16)
        salt2 = create_string_buffer(16)
        salt3 = create_string_buffer(16)
        salt4 = create_string_buffer(16)
        salt5 = create_string_buffer(16)
        salt6 = create_string_buffer(16)
        key1 = create_string_buffer(32)
        key2 = create_string_buffer(32)
        key3 = create_string_buffer(32)
        recovery_data = create_string_buffer(112)
        res = self.vault_lib.create_data_for_server(self.vault, res1_param,
                                                    res2_param, salt1, salt2,
                                                    recovery_data, key1, key2,
                                                    salt3, salt4, salt5, salt6,
                                                    key3)
        if res != 0:
            return (res, {})

        results = {
            'data_salt_11': salt3.raw,
            'data_salt_12': salt4.raw,
            'data_salt_21': salt5.raw,
            'data_salt_22': salt6.raw,
            'pass_salt_1': salt1.raw,
            'pass_salt_2': salt2.raw,
            'recovery_key': recovery_data.raw,
            'data2': key2.raw,
            'data1': key1.raw,
            'password': key3.raw
        }
        return res, results

    def create_password_for_server(self, second_salt):
        server_pass = create_string_buffer(32)
        res = self.vault_lib.create_password_for_server(self.vault, second_salt,
                                                        server_pass)
        if res != 0:
            return res, b''
        return res, server_pass.raw

    def make_password_for_server(self, password, first_salt, second_salt):
        password_param = password.encode('ascii')
        server_pass = create_string_buffer(32)
        res = self.vault_lib.make_password_for_server(password_param,
                                                      first_salt, second_salt,
                                                      server_pass)
        if res != 0:
            return res, b''
        return res, server_pass.raw

    def create_responses_for_server(self, response1, response2, data_salt_11,
                                    data_salt_12, data_salt_21, data_salt_22):
        res1_param = response1.encode('ascii')
        res2_param = response2.encode('ascii')
        data1 = create_string_buffer(32)
        data2 = create_string_buffer(32)
        res = self.vault_lib.create_responses_for_server(
            res1_param, res2_param, data_salt_11, data_salt_12, data_salt_21,
            data_salt_22, data1, data2)
        if res != 0:
            return res, b'', b''
        return res, data1.raw, data2.raw

    def update_key_from_recovery(self, directory, username, response1,
                                 response2, recovery_data, data_salt_1,
                                 data_salt_2, new_password):
        res1_param = response1.encode('ascii')
        res2_param = response2.encode('ascii')
        dir_param = directory.encode('ascii')
        user_param = username.encode('ascii')
        pass_param = new_password.encode('ascii')
        pass_salt_1 = create_string_buffer(16)
        pass_salt_2 = create_string_buffer(16)
        server_pass = create_string_buffer(32)
        new_recovery_data = create_string_buffer(112)
        res = self.vault_lib.update_key_from_recovery(
            self.vault, dir_param, user_param, res1_param, res2_param,
            recovery_data, data_salt_1, data_salt_2, pass_param, pass_salt_1,
            pass_salt_2, server_pass, new_recovery_data)
        if res != 0:
            return res, {}
        return res, {
            'pass_salt_1': pass_salt_1.raw,
            'pass_salt_2': pass_salt_2.raw,
            'password': server_pass.raw,
            'recovery_key': new_recovery_data.raw
        }


Vault_intf.register(Vault)

# Smoke tests to see if surrect values are returned on good inputs
# Also contains a bit of profiling
if __name__ == "__main__":
    v = Vault()

    try:
        os.remove('./test.vault')
        os.remove('./test2.vault')
    except OSError:
        pass

    v.create_vault("./", "test", "password")
    assert v.add_key(1, "google", "oldpass") == 0
    assert v.last_updated_time("google")[0] == 0
    assert v.get_value("google") == (0, 1, "oldpass")
    assert v.update_value(1, "google", "newpass") == 0
    res, update_time = v.last_updated_time("google")
    assert res == 0
    assert v.change_password("password", "str0nkp@ssw0rd") == 0
    assert v.close_vault() == 0
    assert v.open_vault("./", "test", "str0nkp@ssw0rd") == 0
    assert v.get_value("google")[0] == 0
    res, type_, en_val = v.get_encrypted_value("google")
    assert res == 0
    assert v.delete_value("google") == 0
    assert v.get_value("google")[0] == 10
    assert v.add_encrypted_value(type_, "google", en_val) == 0
    assert v.get_value("google")[0] == 0
    assert v.add_key(1, "amazon", "anotherpass") == 0
    assert v.add_key(1, "facebook", "morepasses") == 0

    for i in range(120):
        assert v.add_key(1, "test" + str(i), "testpass") == 0

    assert v.set_last_contact_time(update_time) == 0
    assert v.get_last_contact_time()[0] == 0
    header_res, header = v.get_vault_header()
    v.close_vault()
    assert v.create_vault_from_server_data("./", "test2", "str0nkp@ssw0rd",
                                           header,
                                           [("google", type_, en_val)]) == 0
    assert v.add_key(1, "amazon", "anotherpass") == 0
    assert v.add_key(1, "facebook", "morepasses") == 0
    assert v.delete_value("amazon") == 0
    res, keys = v.get_vault_keys()
    for i in range(len(keys)):
        print(keys[i], v.get_value(keys[i]))
    t0 = time.process_time()
    res, server_data = v.create_data_for_server("chris", "christie")
    t1 = time.process_time()
    print("Data creation time: " + str(t1 - t0))

    t0 = time.process_time()
    res, server_pass = v.create_password_for_server(server_data['pass_salt_2'])
    t1 = time.process_time()
    print("Password derivation time: " + str(t1 - t0))

    assert server_pass == server_data['password']
    v.close_vault()
    res, made_pass = v.make_password_for_server('str0nkp@ssw0rd',
                                                server_data['pass_salt_1'],
                                                server_data['pass_salt_2'])
    assert made_pass == server_pass
    res, data1, data2 = v.create_responses_for_server(
        'chris', 'christie', server_data['data_salt_11'],
        server_data['data_salt_12'], server_data['data_salt_21'],
        server_data['data_salt_22'])
    assert data1 == server_data['data1'] and data2 == server_data['data2']

    recovery_res = v.update_key_from_recovery("./", "test2", 'chris',
                                              'christie',
                                              server_data['recovery_key'],
                                              server_data['data_salt_11'],
                                              server_data['data_salt_21'],
                                              "str0nk3stp@ssw0rd")
    res, keys = v.get_vault_keys()
    for i in range(len(keys)):
        print(keys[i], v.get_value(keys[i]))
    v.close_vault()
    assert v.open_vault("./", "test2", "str0nkp@ssw0rd") != 0
    assert v.open_vault("./", "test2", "str0nk3stp@ssw0rd") == 0
    v.close_vault()
