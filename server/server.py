import nacl.pwhash
import base64
import database
import database_test
import time

class Server:
    def __init__(self, istest=False):
        if istest:
            self.db = database_test.database_test()
        else:
            #TODO aldenperrine: inport information from KMS
            self.db = database_impl.database_impl("Inputstuffs")


    @staticmethod
    def __get_current_time():
        return time.time() * 1000


    @staticmethod
    def __check_data(password, hashed_value):
        try:
            nacl.pwhash.verify(hashed_value, password)
            return True
        except nacl.exceptions.InvalidkeyError:
            return False


    @staticmethod
    def __hash_data(data):
        return nacl.pwhash.argon2id.str(data,
                                        opslimit=nacl.pwhash.argon2i.OPSLIMIT_INTERACTIVE,
                                        memlimit=nacl.pwhash.argon2i.MEMLIMIT_INTERACTIVE)


    def register_user(self, username, password, salt, m_key, r_key, q1, q2, d1, d2, ds11, ds12, ds21, ds22):
        validation_info = self.db.get_val_given_user(username)
        if validation_info is not None:
            return None
        hashed_pass = Server.__hash_data(password)
        hashed_d1 = Server.__hash_data(d1)
        hashed_d2 = Server.__hash_data(d2)
        res = self.db.create_user(username, hashed_pass, salt, m_key, r_key,
                             hashed_d1, hashed_d2, q1, q2, ds11, ds12, ds21, ds22)
        if res is None:
            print(1)
            return None
        current_time = Server.__get_current_time()
        if self.db.set_last_vault_time(username, current_time) is None:
            print(2)
            return None
        if self.db.set_last_login_time(username, current_time - 15000) is None:
            print(3)
            return None
        return current_time


    def get_salt(self, username):
        return self.db.get_salt_given_user(username)


    def check_for_updates(self, username, password, last_updated_time):
        validation_info = self.db.get_val_given_user(username)
        if validation_info is None:
            return None
        current_time = Server.__get_current_time()
        hashed_pass, last_login = validation_info
        if (current_time - last_login < 10000):
            return (0, None)
        if not Server.__check_data(password, hashed_pass):
            self.db.set_last_login_time(username, current_time)
            return (1, None)
        last_vault_update = self.db.get_last_vault_time(username)
        if last_vault_update is None:
            return (2, None)
        if last_vault_update > last_updated_time:
            return (3, None)

        all_keys = self.db.get_keys_given_user(username)
        ret_list = []
        for key in all_keys:
            m_time = self.db.get_modified_time(username, key)
            if m_time > last_updated_time:
                encr_val = self.db.get_value_given_user_and_key(username, key)
                ret_list.append((key, encr_val))

        current_time = Server.__get_current_time()
        return (current_time, ret_list)


    def update_server(self, username, password, last_updated_time, updates):
        validation_info = self.db.get_val_given_user(username)
        if validation_info is None:
            return None
        current_time = Server.__get_current_time()
        hashed_pass, last_login = validation_info
        if (current_time - last_login < 10000):
            return 0
        if not Server.__check_data(password, hashed_pass):
            self.db.set_last_login_time(username, current_time)
            return 1
        last_vault_update = self.db.get_last_vault_time(username)
        if last_vault_update is None:
            return 2

        for update in updates:
            if update[1] is None:
                self.db.delete_key_value_pair()
            else:
                self.db.modify_key_value_pair(username, update[0], update[1])
        current_time = Server.__get_current_time()
        return current_time


    def recovery_questions(self, username):
        qs = self.db.get_qs_given_user(username)
        salts = self.db.get_salts_given_user(username)
        return (qs[0], qs[1], salts[0], salts[1], salts[2], salts[3])


    def check_recovery(self, username, r1, r2):
        recovery_info = self.db.get_data_recovery_given_user(username)
        if not Server.__check_data(r1, recovery_info[1]) or not Server.__check_data(r2, recovery_info[2]):
            self.db.set_last_login_time(username, current_time)
            return (0, None)
        return(Server.__get_current_time(), recovery_info[0])


    def password_change_pass(username, password, new_password, new_salt, new_master):
        valdiation_info = self.db.get_val_given_user(username)
        if validation_info is None:
            return None
        current_time = Server.__get_current_time()
        hashed_pass, last_login = validation_info
        if (current_time - last_login < 10000):
            return 0
        if not Server.__check_data(password, hashed_pass):
            self.db.set_last_login_time(username, current_time)
            return 1


        hashed_pass = Server.__hash_data(new_password)
        self.db.set_mk_and_validation_salt(username, new_master, hashed_pass, new_salt)

        return current_time


    def password_change_recover(username, r1, r2, new_password, new_salt, new_master):
        valdiation_info = self.db.get_val_given_user(username)
        if validation_info is None:
            return None
        current_time = Server.__get_current_time()
        hashed_pass, last_login = validation_info
        if (current_time - last_login < 10000):
            return 0
        if not Server.__check_data(r1, recovery_info[1]) or not Server.__check_data(r2, recovery_info[2]):
            self.db.set_last_login_time(username, current_time)
            return 1


        hashed_pass = Server.__hash_data(new_password)
        self.db.set_mk_and_validation_and_salt(username, new_master, hashed_pass, new_salt)

        return current_time


    def download_vault(self, username, password):
        validation_info = self.db.get_val_given_user(username)
        if validation_info is None:
            return None
        current_time = Server.__get_current_time()
        hashed_pass, last_login = validation_info
        if (current_time - last_login < 10000):
            return (0, None, None)
        if not Server.__check_data(password, hashed_pass):
            self.db.set_last_login_time(username, current_time)
            return (1, None, None)

        header = self.db.get_mk_given_user(username)
        keys = self.db.get_keys_given_user(username)

        res_keys = []
        for key in keys:
            value = self.db.get_value_given_user_and_key(username, key)
            if value is not None:
                res_keys.append(key, value)

        return (current_time, header, res_keys)


    def delete_user(self, username, password, r1, r2):
        validation_info = self.db.get_val_given_user(username)
        if validation_info is None:
            return None
        current_time = Server.__get_current_time()
        hashed_pass, last_login = validation_info
        if (current_time - last_login < 10000):
            return 0
        if not Server.__check_data(password, hashed_pass):
            self.db.set_last_login_time(username, current_time)
            return 1
        recovery_info = self.db.get_data_recovery_given_user(username)
        if not Server.__check_data(r1, recovery_info[1]) or not Server.__check_data(r2, recovery_info[2]):
            return 2

        self.db.delete_user(username)
        return current_time





if __name__ == "__main__":
    test_server = Server(istest=True)
    username = "aldenperrine"
    salt = b'thisissome128bitnumberthatsasalt'
    validation = b'anotherlongderivedkeythatshouldbe256bits'
    master_key = b'somelongencrypted256bitkeywitha192bitnonceand128bitmac'
    recovery_key = b'oneanotherencyrptionbutthistimewithtwoderiveedkeys'
    data1 = b'passwordhashtwiceofsomeanswertoahardquestion'
    data2 = b'anotherpasswordhashofadifferentquestionjustobesure'
    q1 = "Some string question"
    q2 = "Another string question"
    dbs11 = b'anothersalt'
    dbs12 = b'moreslats'
    dbs21 = b'sosaltynow'
    dbs22 = b'saltysalt'

    create_time = test_server.register_user(username, validation, salt, master_key, recovery_key,
                                            q1, q2, data1, data2, dbs11, dbs12, dbs21, dbs22)

    if test_server.get_salt(username) != salt:
        print("Salts do not match")

    if test_server.recovery_questions(username) != (q1, q2, dbs11, dbs12, dbs21, dbs22):
        print("Questions do not match")

    download_time, master_header, keys = test_server.download_vault(username, validation)
    if master_header != master_key:
        print("Master does not match")

    recovery_time, recovery_data = test_server.check_recovery(username, data1, data2)
    if recovery_data != recovery_key:
        print("Recovery does not work")

    update_time = test_server.update_server(username, validation, create_time, [("my key", b'somesupersecurepasswordicannotremember')])

    check_time, updates = test_server.check_for_updates(username, validation, recovery_time)
    print(updates)

    delete_time = test_server.delete_user(username, validation, data1, data2)
    if delete_time < 10:
        print("Deletion failed")
