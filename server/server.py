from nacl import *
import base64
import database
import database_test
import database_impl
import time

# Size defs
SALT_SIZE = 32
MAC_SIZE = 16
NONCE_SIZE = 24
KEY_SIZE = 32

class Server:
    def __init__(self, istest=False):
        if istest:
            self.db = database_test.database_test()
        else:
            self.db = database_test.


    def __get_current_time():
        return time.time() * 1000


    def __check_data(password, hashed_value):
        try:
            pwhash.verify(hashed_value, password)
            return True
        except InvalidKeyError:
            return False


    def __hash_data(data):
        pwhash.argon2id.str(data)


    def regiser_user(username, password, salt, m_key, r_key, q1, q2, d1, d2):
        valdiation_info = db.get_val_given_user(username)
        if validation_info is not None:
            return None
        print(username)
        hashed_pass = __hash_data(password)
        hashed_d1 = __hash_data(d1)
        hashed_d2 = __hash_data(d2)
        res = db.create_user(username, hashed_pass, salt, m_key, r_key, hashed_d1, hashed_d2, q1, q2)
        if res is None:
            return None
        current_time = __get_current_time()
        if db.set_last_vault_time(username, current_time) is None:
            return None
        if db.set_last_login_time(username, current_time) is None:
            return None
        return current_time


    def get_salt(username):
        return db.get_salt_given_user(username)


    def check_for_updates(username, password, last_updated_time):
        valdiation_info = db.get_val_given_user(username)
        if validation_info is not None:
            return None
        current_time = __get_current_time()
        hashed_pass, last_login = validation_info
        if (current_time - last_login < 10000):
            return (0, None)
        if not __check_data(password, hashed_pass):
            db.set_last_login_time(username, current_time)
            return (1, None)
        last_vault_update = db.get_last_vault_time(username)

        #Get user password

        # Check user password

        # If failed, update next available time

        # Check last updated time of vault info

        # If the last_checked_time is before last_update_time, return

        # Get modified times, return encrypted blobs that have been updated
        pass


    def update_server(username, password, last_updated_time, updates):
        # Check user password

        # Check times on updates

        # Send back any blobs which are more recent than the update


        pass







if __name__ == "main":
    test_server = Server(istest=True)
