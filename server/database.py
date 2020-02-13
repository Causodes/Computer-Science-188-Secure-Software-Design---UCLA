from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
from abc import *

# connect to MongoDB, TODO: Update to mongo and securly store info
client = MongoClient("mongodb://User:Pass@notifier-shard-00-00-wcy1w.azure.mongodb.net:27017,notifier-shard-00-01-wcy1w.azure.mongodb.net:27017,notifier-shard-00-02-wcy1w.azure.mongodb.net:27017/test?ssl=true&replicaSet=Notifier-shard-0&authSource=admin&retryWrites=true")
db=client.dbName

# NOTE: Uncomment this for server status debugging
# serverStatusResult=db.command("serverStatus")
# pprint(serverStatusResult)

# ------------------------------------------------------------
#                   Table operations
#------------------------------------------------------------
class Database_intf(ABC):
    # create a document for the user in the database with the following information
    # returns True on success and None on failure
    @abstractmethod
    def create_user(self, username, validation, salt, master_key, recovery_key,
                    data1, data2, q1, q2, dbs11, dbs12, dbs21, dbs22):
        raise NotImplementedError

    # get the recovery_key and 2 data fields for a user
    # returns a tuple of the 3 on success and None on failure
    @abstractmethod
    def get_data_recovery_given_user(self, username):
        raise NotImplementedError

    # get the 4 salts for a user
    # returns a tuple of the 4 on success and None on failure
    @abstractmethod
    def get_salts_given_user(self, username):
        raise NotImplementedError

    # get the salt for a user
    # returns salt on success and None on failure
    @abstractmethod
    def get_salt_given_user(self, username):
        raise NotImplementedError

    # get the val for a user
    # returns tuple val,logintime on success and None on failure
    @abstractmethod
    def get_val_given_user(self, username):
        raise NotImplementedError

    # get the last vault accessed time for a user
    # returns timestamp on success and None on failure
    @abstractmethod
    def get_last_vault_time(self, username):
        raise NotImplementedError

    # set the last vault accessed time for a user
    # returns True on success and None on failure
    @abstractmethod
    def set_last_vault_time(self, username, time):
        raise NotImplementedError

    # set the last login accessed time for a user
    # returns True on success and None on failure
    @abstractmethod
    def set_last_login_time(self, username, time):
        raise NotImplementedError

    # get the qs for a user
    # returns tuple of qs on success and None on failure
    @abstractmethod
    def get_qs_given_user(self, username):
        raise NotImplementedError

    # get the master_key for a user
    # returns master_key on success and None on failure
    @abstractmethod
    def get_mk_given_user(self, username):
        raise NotImplementedError
        
    # set the mk and validation for a user
    # returns True on success and None on failure
    @abstractmethod
    def set_mk_and_validation_and_salt(self, username, mk, validation, salt):
        raise NotImplementedError

    # remove a user and its data from the document
    # returns True on success and None on failure
    @abstractmethod
    def delete_user(self, username):
        raise NotImplementedError

    # given a user, add a key value pair and use the system time as the timestamp
    # returns True on success and None on failure
    @abstractmethod
    def add_key_value_pair(self, username, key, value):
        raise NotImplementedError

    # given a user and a key, update the value and timestamp for the given key
    # returns True on success and None on failure
    @abstractmethod
    def modify_key_value_pair(self, username, key, value):
        raise NotImplementedError

    # given a user and a key, delete the value by setting it to null and update the timestamp
    # returns True on success and None on failure
    @abstractmethod
    def delete_key_value_pair(self, username, key):
        raise NotImplementedError

    # given a user and a key, get the value from the database
    # returns the value on success and None on failure
    def get_value_given_user_and_key(self, username, key):
        raise NotImplementedError

    # given a user and a key, get the value from the database
    # returns the value on success and None on failure
    @abstractmethod
    def get_keys_given_user(self, username):
        raise NotImplementedError

    # given a user, return a list of the keys associated with him
    # returns a list of keys on success, and None on failure
    @abstractmethod
    def get_keys_given_user(self, username):
        raise NotImplementedError

    # given a user and a key, return the last time that key was modified
    # returns a timestamp with millisecond granularity since Epoch on success, and None on failure
    @abstractmethod
    def get_modified_time(self, username, key):
        raise NotImplementedError


    # given a user, return a list of the keys associated with him that have null values
    # returns a list of keys with null values on success, and None on failure
    @abstractmethod
    def get_null_keys_given_user(self, username):
        raise NotImplementedError
