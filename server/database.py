from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint

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
    pass

# remove a user and its data from the document
# returns True on success and None on failure
def delete_user(username):
    pass

# given a user, add a key value pair and use the system time as the timestamp
# returns True on success and None on failure
def add_key_value_pair(username, key, value):
    pass

# given a user and a key, update the value and timestamp for the given key
# returns True on success and None on failure
def modify_key_value_pair(username, key, value):
    pass

# given a user and a key, delete the value by setting it to null and update the timestamp
# returns True on success and None on failure
def delete_key_value_pair(username, key):
    pass

# given a user and a key, get the value from the database
# returns the value on success and None on failure
def get_keys_given_user(username):
    pass

# given a user, return a list of the keys associated with him
# returns a list of keys on success, and None on failure
def get_keys_given_user(username):
    pass

# given a user and a key, return the last time that key was modified
# returns a timestamp with millisecond granularity since Epoch on success, and None on failure
def get_modified_time(username, key):
    pass


# given a user, return a list of the keys associated with him that have null values
# returns a list of keys with null values on success, and None on failure
def get_null_keys_given_user(username):
    pass
