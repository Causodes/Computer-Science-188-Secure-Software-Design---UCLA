"""Main password bank application

This module creates and defines a main Bank object that interacts with
the rest of the application, acting as the entrypoint to the application
"""
import asyncio
from collections import defaultdict
import json
import itertools
from queue import Queue, Empty
import struct
import sys
import threading
import time
import os
import sys
from abc import *
from base64 import *

import janus

from application.utils import *
import application.vault as vault
from chrome_extension.bank_server import BankServer
# from application.utils import *
# import application.vault as vault
import requests


# class Bank_intf(ABC):
#     """Abstract interface to describe how to communicate with the bank object.
#     """
#     # Clipboard thread
#     @abstractmethod
#     def start_clipboard(self) -> None:
#         """Starts a thread to watch for values to the clipboard
#         """
#         raise NotImplementedError

#     # UI functionality
#     @abstractmethod
#     def sign_up(self, username: str, password: str) -> bool:
#         raise NotImplementedError

#     @abstractmethod
#     def forgot_password(self, username: str):
#         raise NotImplementedError

#     @abstractmethod
#     def log_in(self, username: str, password: str) -> bool:
#         raise NotImplementedError

#     @abstractmethod
#     def get_websites(self):
#         raise NotImplementedError

#     @abstractmethod
#     def get_login_info(self, website: str) -> str:
#         raise NotImplementedError

#     @abstractmethod
#     def add_login_info(self, website: str, username, password):
#         raise NotImplementedError

#     # AWS functionality
#     @abstractmethod
#     def create_user(self, username, password):
#         raise NotImplementedError

#     @abstractmethod
#     def login(self, username, password):
#         raise NotImplementedError

#     @abstractmethod
#     def server_update(self):
#         raise NotImplementedError

#     # Chrome Extension functionality
#     # should now open tcp listening server
#     @abstractmethod
#     def send_message_chrome(self, message):
#         raise NotImplementedError

#     # asynchronously fills queue with data read
#     @abstractmethod
#     def read_message_chrome(self, queue):
#         raise NotImplementedError

#     @abstractmethod
#     def send_login_chrome(self, website):
#         raise NotImplementedError

#     # C Vault functionality
#     @abstractmethod
#     def create_user_file(self, username, password):
#         raise NotImplementedError

#     @abstractmethod
#     def open_user_file(self, username, password):
#         raise NotImplementedError

#     @abstractmethod
#     def add_credential(self, website, username, password):
#         raise NotImplementedError

#     @abstractmethod
#     def get_credentials(self, website):
#         raise NotImplementedError

#     @abstractmethod
#     def get_keys(self):
#         raise NotImplementedError


class Bank():

    @staticmethod
    def decode_credentials(credentials: bytes) -> str:
        user_len = struct.unpack('i', credentials[0:4])[0]
        username = credentials[4:4 + user_len].decode('utf-8')
        password = credentials[4 + user_len:].decode('utf-8')
        return (username, password)

    @staticmethod
    def encode_credentials(username: str, password: str) -> bytes:
        value = struct.pack('i', len(username))
        value += username.encode()
        value += password.encode()
        return value

    def __init__(self):
        self._vault = vault.Vault()
        self.cur_user = None
        self.cur_changes = defaultdict(lambda: -1)

    # Clipboard thread
    def start_clipboard(self):
        t = threading.Thread(None, self._clipboard_bg_process,
                             args=(self.clipboard_queue,), daemon=True)
        t.start()

    def _clipboard_bg_process(self, item_q: Queue):
        last_item = time.time()
        while True:
            if time.time() - last_item > 30:
                clear_clipboard()
            try:
                item = item_q.get(block=False)
                last_item = time.time()
                copy_clipboard(item)
            except Empty:
                time.sleep(0.1)

    # UI functionality
    def sign_up(self, username, password, recovery1, recovery2):
        if not self.create_and_open(username, password):
            print('Failed to create file', file=sys.stderr)
            return False
        if not self.create_user(recovery1, recovery2):
            print('User exists in cloud', file=sys.stderr)
            return False
        self.server_login(username)
        return True

    def get_recovery_questions(self, username):
        questions_response = requests.post(
            'https://noodlespasswordvault.com/recovery_questions',
            json={'username': username},
            verify=True)
        if questions_response.status_code != 200:
            return False
        return questions_response.json()['q1'], questions_response.json()['q2']

    def forgot_password(self, username, new_pass, response1, response2):
        questions_response = requests.post(
            'https://noodlespasswordvault.com/recovery_questions',
            json={'username': username},
            verify=True)

        q_json = questions_response.json()

        d_salt11, d_salt12 = q_json['data_salt_11'], q_json['data_salt_12']
        d_salt21, d_salt22 = q_json['data_salt_21'], q_json['data_salt_22']

        resp1, resp2 = self._vault.create_responses_for_server(
            response1, response2, d_salt11, d_salt12, d_salt21, d_salt22)

        recovery_response = requests.post('https://noodlespasswordvault.com/recover',
                                          json={
                                              'username': username,
                                              'r1': b64encode(resp1).decode('ascii'),
                                              'r2': b64encode(resp2).decode('ascii')
                                          },
                                          verify=True)

        if recovery_response.status_code != 200:
            return False

        try:
            vault_resp = self._vault.update_key_from_recovery('../vault', username, response1, response2, b64decode(
                recovery_response.json()['recovery_key']), d_salt11, d_salt21, new_pass)
        except:
            return False

        recover_change = requests.post('https://noodlespasswordvault.com/recovery_change',
                                       json={
                                           'username': username,
                                           'recovery_1': b64encode(resp1).decode('ascii'),
                                           'recovery_2': b64encode(resp2).decode('ascii'),
                                           'new_password': b64encode(vault_resp['password']).decode('ascii'),
                                           'new_salt_1': b64encode(vault_resp['pass_salt_1']).decode('ascii'),
                                           'new_salt_2': b64encode(vault_resp['pass_salt_2']).decode('ascii'),
                                           'new_master': b64encode(vault_resp['recovery_key']).decode('ascii')
                                       },
                                       verify=True)
        if recover_change.status_code != 200:
            return False
        return True

    def log_in(self, username, password):
        if not self.open_user_file(username, password):
            return False
        return self.server_login(username)

    def get_websites(self):
        return self.get_keys()

    def get_login_info(self, website):
        return self.get_credentials(website)

    def add_login_info(self, website, username, password):
        return self.add_credential(website, username, password)

    # CHROME communication
    def start_bank_server(self):
        self.bank_server = BankServer(6969)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.bank_server.run_server_forever())
        print('hello')

    def listen_bank_server(self):
        for cli, q in self.bank_server.client_messages.items():
            if q.sync_q:
                msg = q.sync_q.get()
                print(f'{cli} sent {msg}', file=sys.stderr, flush=True)

    # AWS functionality
    def create_user(self, recovery1, recovery2):
        # recovery is a (question, answer) string tuple
        reg_json = self._vault.create_data_for_server(
            recovery1[1], recovery2[1])
        # currently ignorning error code
        # will take a long time so maybe give UI indication

        # ignoring error code
        reg_json['encrypted_master'] = self._vault.get_vault_header()

        for key in reg_json.keys():
            reg_json[key] = b64encode(reg_json[key]).decode('ascii')

        reg_json['q1'] = recovery1[0]
        reg_json['q2'] = recovery2[0]
        reg_json['username'] = self.cur_user

        reg_resp = requests.post(
            'https://noodlespasswordvault.com/register',
            json=reg_json,
            verify=True)

        if reg_resp.status_code != 200:
            return False
        self._vault.set_last_contact_time(int(reg_resp.json()['time']))
        return True

    def server_login(self, username):
        salt_request = requests.post('https://noodlespasswordvault.com/salt',
                                     json={'username': username},
                                     verify=True)
        if salt_request.status_code != 200:
            return False
        self.salt1 = b64decode(salt_request.json()[
                               'pass_salt_1'].encode('ascii'))
        self.salt2 = b64decode(salt_request.json()[
                               'pass_salt_2'].encode('ascii'))
        return True

    def server_update(self):
        # pull server updates
        encoded_pass = self.b64encode(
            self._vault.create_password_for_server(self.salt2)).decode('ascii')

        check_json = {'username': self.cur_user, 'password': encoded_pass,
                      'last_update_time': self._vault.get_last_contact_time()}  # TIME
        check_resp = requests.post(
            'https://noodlespasswordvault.com/check', json=check_json, verify=True)

        if check_resp.status_code != 200:
            return False

        server_changes = defaultdict(lambda: -1, check_resp.json()['updates'])
        server_updates = {}
        local_updates = {}

        for key in set(itertools.chain(server_changes.keys(), self.cur_changes.keys())):
            if server_changes[key][1] > self.cur_changes[key][1]:
                local_updates[key] = server_changes[key]
            else:
                server_updates[key] = self.cur_changes[key]

        for site, (new_creds, _time) in local_updates.items():
            self.modify_credential(site, *Bank.decode_credentials(new_creds))

        update_resp = requests.post('https://noodlespasswordvault.com/update',
                                    json={
                                        'username': self.cur_user,
                                        'password': encoded_pass,
                                        # 'last_updated_time': 0,
                                        'updates': server_updates
                                    },
                                    verify=True)
        self.cur_changes.clear()

        check2_json = {'username': self.cur_user, 'password': encoded_pass,
                       'last_update_time': check_resp.json()['time']}  # TIME
        check2_resp = requests.post(
            'https://noodlespasswordvault.com/check', json=check2_json, verify=True)

        server_changes = check2_resp.json()['updates']

        for site, (new_creds, _time) in server_changes.items():
            if (new_creds, _time) != server_updates[site]:
                print(
                    f'Changing because server_updates[{site}] == {server_updates[site]} != server_changes[{site}] == {server_changes[site]}')
                self.modify_credential(
                    site, *Bank.decode_credentials(new_creds))
        # check each against local copy to see which is newer
        # if local newer,

    # Chrome Extension functionality
    # should now open tcp listening server

    # C Vault functionality

    def create_and_open(self, username, password):
        if not self._vault.create_vault('../vault', username, password):
            return False
        self.cur_user = username
        return True

    def open_user_file(self, username, password):
        if not self._vault.open_vault('../vault', username, password):
            return False
        self.cur_user = username
        return True

    def add_credential(self, website, username, password):
        cur_time = get_time()
        if not self._vault.add_key(0, website, Bank.encode_credentials(username, password), cur_time):
            return False
        self.cur_changes[website] = (self._vault.get_encrypted_value(
            website), cur_time)
        return True

    def modify_credential(self, website, username, new_password):
        try:
            if self.add_credential(website, username, new_password):
               return True
        except:
            pass

        cur_time = get_time()
        if not self._vault.update_value(0, website, Bank.encode_credentials(username, new_password), cur_time):
            return False
        self.cur_changes[website] = (self._vault.get_encrypted_value(
            website), cur_time)
        return True

    def delete_credential(self, website):
        cur_time = get_time()
        self._vault.delete_value(website, cur_time)
        self.cur_changes[website] = (None, cur_time)
        return True

    def get_credentials(self, website):
        key_type, data = self._vault.get_value(website)
        if key_type == 1:
            return (data,)
        elif key_type == 0:
            return Bank.decode_credentials(data)
        return tuple()

    def get_keys(self):
        return self._vault.get_vault_keys()
