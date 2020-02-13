from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
from database import Database_intf
import time

# connect to MongoDB, TODO: Update to mongo and securly store info

class database_impl(Database_intf):
    # ------------------------------------------------------------
    #                   Table operations
    #------------------------------------------------------------

    def __init__(self, validation_input):
        #TODO devenvimalpatel: use the input to create the client
        client = MongoClient("mongodb+srv://HIDDEN@notifier-wcy1w.azure.mongodb.net/test?retryWrites=true&w=majority")
        db=client.Password_Vault

    # create a document for the user in the database with the following information
    # returns True on success and None on failure
    def create_user(self, username, validation, salt, master_key, recovery_key,
                    data1, data2, q1, q2, dbs11, dbs12, dbs21, dbs22):
        if self.user_exists(username):
            return None
        user = {
            'username' : username,
            'hashed_validation' : validation,
            'salt' : salt,
            'encrypted_master_key': master_key,
            'logins': {},
            'recovery_key': recovery_key,
            'data1': data1,
            'data2': data2,
            'q1': q1,
            'q2': q2,
            'last_login': None,
            'last_vault': None,
            'dbs11': dbs11, 
            'dbs12': dbs12, 
            'dbs21': dbs21, 
            'dbs22': dbs22
        }
        result = self.db.users.insert_one(user)
        # print the object id; basically if this runs, it went through.
        return True if result.acknowledged else None

    # get the 4 salts for a user
    # returns a tuple of the 4 on success and None on failure
    def get_salts_given_user(self, username):
        if not self.user_exists(username): return None
        users = self.db.users.find(
            {'username' : username}
        )
        user = users.next()
        return (user['dbs11'], user['dbs12'], user['dbs21'], user['dbs22'])

    # get the recovery_key and 2 data fields for a user
    # returns a tuple of the 3 on success and None on failure
    def get_data_recovery_given_user(self, username):
        if not self.user_exists(username): return None
        users = self.db.users.find(
            {'username' : username}
        )
        user = users.next()
        return (user['recovery_key'], user['data1'], user['data2'])

    # get the qs for a user
    # returns tuple of qs on success and None on failure
    def get_qs_given_user(self, username):
        if not self.user_exists(username): return None
        users = self.db.users.find(
            {'username' : username}
        )
        user = users.next()
        return (user['q1'], user['q2'])

    # get the salt for a user
    # returns salt on success and None on failure
    def get_salt_given_user(self, username):
        if not self.user_exists(username): return None
        users = self.db.users.find(
            {'username' : username}
        )
        user = users.next()
        return user['salt']

    # get the val for a user
    # returns tuple val,logintime on success and None on failure
    def get_val_given_user(self, username):
        if not self.user_exists(username): return None
        users = self.db.users.find(
            {'username' : username}
        )
        user = users.next()
        return (user['hashed_validation'], user['last_login'])

    # get the last vault accessed time for a user
    # returns timestamp on success and None on failure
    def get_last_vault_time(self, username):
        if not self.user_exists(username): return None
        users = self.db.users.find(
            {'username' : username}
        )
        user = users.next()
        return user['last_vault']

    # set the last vault accessed time for a user
    # returns True on success and None on failure
    def set_last_vault_time(self, username, time):
        if not self.user_exists(username): return None
        col = self.db.users
        result = col.update_one(
            {'username' : username},
            {'$set' :
                {'last_vault' : time}
            }
        )
        return True if result.acknowledged else None

    # set the last login accessed time for a user
    # returns True on success and None on failure
    def set_last_login_time(self, username, time):
        if not self.user_exists(username): return None
        col = self.db.users
        result = col.update_one(
            {'username' : username},
            {'$set' :
                {'last_login' : time}
            }
        )
        return True if result.acknowledged else None

    # get the master_key for a user
    # returns master_key on success and None on failure
    def get_mk_given_user(self, username):
        if not self.user_exists(username): return None
        users = self.db.users.find(
            {'username' : username}
        )
        user = users.next()
        return user['encrypted_master_key']

    # set the mk and validation for a user
    # returns True on success and None on failure
    def set_mk_and_validation_and_salt(self, username, mk, validation, salt):
        if not self.user_exists(username): return None
        col = self.db.users
        result = col.update_one(
            {'username' : username},
            {'$set' :
                {'encrypted_master_key' : mk,
                 'hashed_validation': validation,
                 'salt': salt
                }
            }
        )
        return True if result.acknowledged else None
    
    # remove a user and its data from the document
    # returns True on success and None on failure
    def delete_user(self, username):
        result = self.db.users.delete_one(
            {'username' : username}
        )
        return True if result.acknowledged else None

    # given a user, add a key value pair and use the system time as the timestamp
    # returns True on success and None on failure
    def add_key_value_pair(self, username, key, value):
        if not self.user_exists(username): return None
        current_login_dict = self.get_logins_from_user(username)
        current_login_dict[key] = (value, time.time() * 1000)
        col = self.db.users
        result = col.update_one(
            {'username' : username},
            {'$set' :
                {'logins' : current_login_dict}
            }
        )
        return True if result.acknowledged else None


    # given a user and a key, update the value and timestamp for the given key
    # returns True on success and None on failure
    def modify_key_value_pair(self, username, key, value):
        return self.add_key_value_pair(username, key, value)

    # given a user and a key, delete the value by setting it to null and update the timestamp
    # returns True on success and None on failure
    def delete_key_value_pair(self, username, key):
        if not self.user_exists(username): return None
        current_login_dict = self.get_logins_from_user(username)
        if key in current_login_dict:
            current_login_dict[key] = (None, time.time() * 1000)
            col = self.db.users
            result = col.update_one(
                {'username' : username},
                {'$set' :
                    {'logins' : current_login_dict}
                }
            )
            return True if result.acknowledged else None
        else:
            return None

    # given a user and a key, get the value from the database
    # returns the value on success and None on failure
    def get_value_given_user_and_key(self, username, key):
        if not self.user_exists(username): return None
        current_login_dict = self.get_logins_from_user(username)
        if key in current_login_dict:
            return current_login_dict[key][0]
        else:
            return None

    # given a user, return a list of the keys associated with him
    # returns a list of keys on success, and None on failure
    def get_keys_given_user(self, username):
        if not self.user_exists(username): return None
        current_login_dict = self.get_logins_from_user(username)
        return current_login_dict.keys()

    # given a user and a key, return the last time that key was modified
    # returns a timestamp with millisecond granularity since Epoch on success, and None on failure
    def get_modified_time(self, username, key):
        if not self.user_exists(username): return None
        current_login_dict = self.get_logins_from_user(username)
        if key in current_login_dict:
            return current_login_dict[key][1]
        else:
            return None


    # given a user, return a list of the keys associated with him that have null values
    # returns a list of keys with null values on success, and None on failure
    def get_null_keys_given_user(self, username):
        if not self.user_exists(username): return None
        current_login_dict = self.get_logins_from_user(username)
        return [key for key in current_login_dict.keys() if current_login_dict[key][0] is None]


    # ------------------------------------------------------------
    #                   Table Helpers
    #-------------------------------------------------------------
    def user_exists(self, username):
        user = self.db.users.find(
            {'username' : username}
        )
        return user.count() > 0

    def get_logins_from_user(self, username):
        users = self.db.users.find(
            {'username' : username}
        )
        logins = users.next()['logins']
        return logins
