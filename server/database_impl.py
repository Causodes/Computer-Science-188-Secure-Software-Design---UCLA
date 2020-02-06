from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
import time

# connect to MongoDB, TODO: Update to mongo and securly store info
client = MongoClient("mongodb://User:Pass@notifier-shard-00-00-wcy1w.azure.mongodb.net:27017,notifier-shard-00-01-wcy1w.azure.mongodb.net:27017,notifier-shard-00-02-wcy1w.azure.mongodb.net:27017/test?ssl=true&replicaSet=Notifier-shard-0&authSource=admin&retryWrites=true")
db=client.dbName

# NOTE: Uncomment this for server status debugging
# serverStatusResult=db.command("serverStatus")
# pprint(serverStatusResult)

# ------------------------------------------------------------
#                   Table operations
#------------------------------------------------------------

# create a document for the user in the database with the following information
# returns True on success and None on failure
def create_user(username, validation, salt, master_key):
    if user_exists(username):
        return None
    user = {
        'username' : username,
        'hashed_validation' : validation,
        'salt' : salt,
        'encrypted_master_key': master_key
        'logins': dict()
    }
    result = db.users.insert_one(user)
    # print the object id; basically if this runs, it went through.
    return True if result.acknowledged else None

# remove a user and its data from the document
# returns True on success and None on failure
def delete_user(username):
    result = db.users.delete_one(
        {'username' : username}
    )
    return True if result.acknowledged else None

# given a user, add a key value pair and use the system time as the timestamp
# returns True on success and None on failure
def add_key_value_pair(username, key, value):
    if not user_exists(username) return None
    current_login_dict = get_logins_from_user(username)
    current_login_dict[key] = (value, time.time() * 1000)
    col = db.logins
    result = col.update_one(
        {'username' : username},
        {'$set' :
            {'logins' : current_login_dict}
        }
    )
    return True if result.acknowledged else None


# given a user and a key, update the value and timestamp for the given key
# returns True on success and None on failure
def modify_key_value_pair(username, key, value):
    return add_key_value_pair(username, key, value)

# given a user and a key, delete the value by setting it to null and update the timestamp
# returns True on success and None on failure
def delete_key_value_pair(username, key):
    if not user_exists(username) return None
    current_login_dict = get_logins_from_user(username)
    if key in current_login_dict:
        current_login_dict[key] = (None, time.time() * 1000)
        col = db.logins
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
def get_value_given_user_and_key(username, key):
    if not user_exists(username) return None
    current_login_dict = get_logins_from_user(username)
    if key in current_login_dict:
        return current_login_dict[key][0]
    else:
        return None

# given a user, return a list of the keys associated with him
# returns a list of keys on success, and None on failure
def get_keys_given_user(username):
    if not user_exists(username) return None
    current_login_dict = get_logins_from_user(username)
    return current_login_dict.keys()

# given a user and a key, return the last time that key was modified
# returns a timestamp with millisecond granularity since Epoch on success, and None on failure
def get_modified_time(username, key):
    if not user_exists(username) return None
    current_login_dict = get_logins_from_user(username)
    if key in current_login_dict:
        return current_login_dict[key][1]
    else:
        return None


# given a user, return a list of the keys associated with him that have null values
# returns a list of keys with null values on success, and None on failure
def get_null_keys_given_user(username):
    if not user_exists(username) return None
    current_login_dict = get_logins_from_user(username)
    return [key for key in current_login_dict.keys() if current_login_dict[key][0] is None]


# ------------------------------------------------------------
#                   Table Helpers
#-------------------------------------------------------------
def user_exists(username):
    user = db.users.find(
        {'username' : username}
    )
    return user.count() > 0

def get_logins_from_user(username):
    users = db.users.find(
        {'username' : username}
    )
    logins = users.next()['logins']

