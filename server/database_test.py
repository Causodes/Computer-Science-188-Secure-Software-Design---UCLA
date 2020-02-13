# pprint library is used to make the output look more pretty
from pprint import pprint
import time
from database import Database_intf



class database_test(Database_intf):

    # ------------------------------------------------------------
    #                   Table operations
    #------------------------------------------------------------
    def __init__(self):
        self.test_dict = {}
    # create a document for the user in the database with the following information
    # returns True on success and None on failure
    def create_user(self, username, validation, salt, master_key, recovery_key,
                    data1, data2, q1, q2, dbs11, dbs12, dbs21, dbs22):
        user_count = len(self.test_dict.keys())
        self.test_dict[user_count + 1] = {        
            "username":username,
            "hashed_validation":validation,
            "salt":salt,
            "encrypted_master_key":master_key,
            "logins":{},
            "recovery_key": recovery_key,
            "data1": data1,
            "data2": data2,
            "q1": q1,
            "q2": q2,
            "last_vault": None,
            "last_login": None,
            'dbs11': dbs11, 
            'dbs12': dbs12, 
            'dbs21': dbs21, 
            'dbs22': dbs22
        }
        return True

    # get the recovery_key and 2 data fields for a user
    # returns a tuple of the 3 on success and None on failure
    def get_data_recovery_given_user(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                user = self.test_dict[id]
                return (user['recovery_key'], user['data1'], user['data2'])
        return None

    # get the 4 salts for a user
    # returns a tuple of the 4 on success and None on failure
    def get_salts_given_user(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                user = self.test_dict[id]
                return (user['dbs11'], user['dbs12'], user['dbs21'], user['dbs22'])
        return None

    # get the qs for a user
    # returns tuple of qs on success and None on failure
    def get_qs_given_user(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                user = self.test_dict[id]
                return (user['q1'], user['q2'])
        return None

    # get the master_key for a user
    # returns master_key on success and None on failure
    def get_mk_given_user(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                user = self.test_dict[id]
                return user['encrypted_master_key']
        return None

    # get the salt for a user
    # returns salt on success and None on failure
    def get_salt_given_user(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                user = self.test_dict[id]
                return user['salt']
        return None

    # get the val for a user
    # returns tuple val,logintime on success and None on failure
    def get_val_given_user(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                user = self.test_dict[id]
                return (user['hashed_validation'], user['last_login'])
        return None

    # get the last vault accessed time for a user
    # returns timestamp on success and None on failure
    def get_last_vault_time(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                user = self.test_dict[id]
                return user['last_vault']
        return None

    # set the last vault accessed time for a user
    # returns True on success and None on failure
    def set_last_vault_time(self, username, time):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                self.test_dict[id]['last_vault'] = time
                return True
        return None

    # set the last login accessed time for a user
    # returns True on success and None on failure
    def set_last_login_time(self, username, time):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                self.test_dict[id]['last_login'] = time
                return True
        return None

    # remove a user and its data from the document
    # returns True on success and None on failure
    def delete_user(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                del self.test_dict[id]
                return True
        return None

    # given a user, add a key value pair and use the system time as the timestamp
    # returns True on success and None on failure
    def add_key_value_pair(self, username, key, value):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                self.test_dict[id]["logins"][key] = (value, time.time() * 1000)
                return True
        return None

    # given a user and a key, update the value and timestamp for the given key
    # returns True on success and None on failure
    def modify_key_value_pair(self, username, key, value):
        return add_key_value_pair(username, key, value)

    # given a user and a key, delete the value by setting it to null and update the timestamp
    # returns True on success and None on failure
    def delete_key_value_pair(self, username, key):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                if key in self.test_dict[id]["logins"]:
                    self.test_dict[id]["logins"][key] = (None, time.time() * 1000)
                    return True
        return None

    # given a user and a key, get the value from the database
    # returns the value on success and None on failure
    def get_value_given_user_and_key(self, username, key):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                if key in self.test_dict[id]["logins"]:
                    return self.test_dict[id]["logins"][key][0]
        return None

    # given a user, return a list of the keys associated with him
    # returns a list of keys on success, and None on failure
    def get_keys_given_user(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                return self.test_dict[id]["logins"].keys()
        return None

    # given a user and a key, return the last time that key was modified
    # returns a timestamp with millisecond granularity since Epoch on success, and None on failure
    def get_modified_time(self, username, key):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                if key in self.test_dict[id]["logins"]:
                    return self.test_dict[id]["logins"][key][1]
        return None


    # given a user, return a list of the keys associated with him that have null values
    # returns a list of keys with null values on success, and None on failure
    def get_null_keys_given_user(self, username):
        for id in self.test_dict.keys():
            if self.test_dict[id]["username"] == username:
                return [key for key in self.test_dict[id]["logins"].keys() if self.test_dict[id]["logins"][key][0] is None]
        return None

    def print_dict(self):
        pprint(self.test_dict)
