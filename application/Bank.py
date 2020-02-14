"""Main password bank application

This module creates and defines a main Bank object that interacts with
the rest of the application, acting as the entrypoint to the application
"""
from dataclasses import dataclass
import struct
import sys
import os
from abc import *


from application.vault import Vault
import server.database as db

class Bank_intf(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    # AWS functionality
    @abstractmethod
    def create_user(self, username, password):
        # this will probably be called by server_update() after create_file() is used
        raise NotImplementedError

    @abstractmethod
    def login(self, username, password):
        raise NotImplementedError

    @abstractmethod
    def server_update(self):
        raise NotImplementedError

    # Chrome Extension functionality
    @abstractmethod
    def send_message_chrome(self, message):
        raise NotImplementedError

    @abstractmethod
    def read_message_chrome(self):
        # likely will need to be implemented asynchronously/via threads
        raise NotImplementedError

    @abstractmethod
    def send_login_chrome(self, website):  # bridge between chrome and vault
        raise NotImplementedError

    # C Vault functionality
    @abstractmethod
    def create_user_file(self, username, password):
        raise NotImplementedError

    @abstractmethod
    def open_user_file(self):
        raise NotImplementedError

    @abstractmethod
    def add_credential(self, website, username, password):
        raise NotImplementedError

    @abstractmethod
    def get_credentials(self, website):
        raise NotImplementedError

    @abstractmethod
    def get_keys(self):
        raise NotImplementedError

class Bank(Bank_intf):
    def __init__(self):
        self._vault = Vault()

    # AWS functionality
    def create_user(self, username, password):
        # this will probably be called by server_update() after create_file() is used
        db.create_user(username, )
        raise NotImplementedError

    def login(self, username, password):
        raise NotImplementedError

    def server_update(self):
        raise NotImplementedError

    # Chrome Extension functionality
    def send_message_chrome(self, message):
        sys.stdout.write(struct.pack('I', len(message)).decode('utf-8'))
        sys.stdout.write(message)
        sys.stdout.flush()

    def read_message_chrome(self, queue): # asynchronously fills queue with data read
        while True:
            msg_len_b = sys.stdin.read(4)

            if len(msg_len_b) == 0:
                queue.put(None)
                sys.exit(1)

            msg_len = struct.unpack('i', msg_len_b)[0]
            msg = sys.stdin.read(msg_len).decode('utf-8')

            queue.put(msg)

    def send_login_chrome(self, website):
        username, password = self._vault.get_value(website) # python memory security
        self.send_message_chrome('{"username": "{}", "password": "{}"}'.format(username, password))

    # C Vault functionality
    def create_user_file(self, username, password):
        path = os.path.join('../vault', username)
        return self._vault.create_vault(path, username, password)

    def open_user_file(self, username, password):
        path = os.path.join('../vault', username)
        return self._vault.open_vault(path, username, password)

    def add_credential(self, website, username, password):
        return self._vault.add_key(website, (username, password))

    def get_credentials(self, website):
        return self._vault.get_value(website)

    def get_keys(self):
        raise NotImplementedError
