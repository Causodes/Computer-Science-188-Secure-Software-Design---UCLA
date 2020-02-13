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
        #self.db_connection = Database_intf
        pass


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

    def regiser_user(username, password, m_key, r_key, q1, q2, d1, d2):

        # Check if user in DB

        # Hash password and data

        # Create a user, return time
        print(username)
        hashed_pass = __hash_data(password)
        hashed_d1 = __hash_data(d1)
        hashed_d2 = __hash_data(d2)


    def get_salt(username):
        pass

    def check_for_updates(username, password, last_updated_time):
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
