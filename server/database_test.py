# pprint library is used to make the output look more pretty
from pprint import pprint
import time

test_dict = {}

# ------------------------------------------------------------
#                   Table operations
#------------------------------------------------------------

# create a document for the user in the database with the following information
# returns True on success and None on failure
def create_user(username, validation, salt, master_key):
    user_count = len(test_dict.keys())
    test_dict[user_count + 1] = {        
        "username":username,
        "hashed_validation":validation,
        "salt":salt,
        "encrypted_master_key":master_key,
        "logins":{}
    }

# remove a user and its data from the document
# returns True on success and None on failure
def delete_user(username):
    for id in test_dict.keys():
        if test_dict[id]["username"] == username:
            del test_dict[id]
            return True
    return None

# given a user, add a key value pair and use the system time as the timestamp
# returns True on success and None on failure
def add_key_value_pair(username, key, value):
    for id in test_dict.keys():
        if test_dict[id]["username"] == username:
            test_dict[id]["logins"][key] = (value, time.time() * 1000)
            return True
    return None

# given a user and a key, update the value and timestamp for the given key
# returns True on success and None on failure
def modify_key_value_pair(username, key, value):
    return add_key_value_pair(username, key, value)

# given a user and a key, delete the value by setting it to null and update the timestamp
# returns True on success and None on failure
def delete_key_value_pair(username, key):
    for id in test_dict.keys():
        if test_dict[id]["username"] == username:
            if key in test_dict[id]["logins"]:
                test_dict[id]["logins"][key] = (None, time.time() * 1000)
                return True
    return None

# given a user and a key, get the value from the database
# returns the value on success and None on failure
def get_value_given_user_and_key(username, key):
    for id in test_dict.keys():
        if test_dict[id]["username"] == username:
            if key in test_dict[id]["logins"]:
                return test_dict[id]["logins"][key][0]
    return None

# given a user, return a list of the keys associated with him
# returns a list of keys on success, and None on failure
def get_keys_given_user(username):
    for id in test_dict.keys():
        if test_dict[id]["username"] == username:
            return test_dict[id]["logins"].keys()
    return None

# given a user and a key, return the last time that key was modified
# returns a timestamp with millisecond granularity since Epoch on success, and None on failure
def get_modified_time(username, key):
    for id in test_dict.keys():
        if test_dict[id]["username"] == username:
            if key in test_dict[id]["logins"]:
                return test_dict[id]["logins"][key][1]
    return None


# given a user, return a list of the keys associated with him that have null values
# returns a list of keys with null values on success, and None on failure
def get_null_keys_given_user(username):
    for id in test_dict.keys():
        if test_dict[id]["username"] == username:
            return [key for key in test_dict[id]["logins"].keys() if test_dict[id]["logins"][key][0] is None]
    return None

def print_dict():
    pprint(test_dict)