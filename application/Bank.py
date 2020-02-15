"""Main password bank application

This module creates and defines a main Bank object that interacts with
the rest of the application, acting as the entrypoint to the application
"""
import datetime
from queue import Queue, Empty
import struct
import sys
import threading
import time
import os
from abc import *

from application.utils import *
import application.vault as vault
import server.database as db


class Bank_intf(ABC):
    """Abstract interface to describe how to communicate with the bank object.
    """
    # Clipboard thread
    @abstractmethod
    def start_clipboard(self) -> None:
        """Starts a thread to watch for values to the clipboard
        """
        raise NotImplementedError

    # UI functionality
    @abstractmethod
    def sign_up(self, username: str, password: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def forgot_password(self, username: str):
        raise NotImplementedError

    @abstractmethod
    def log_in(self, username: str, password: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_websites(self):
        raise NotImplementedError

    @abstractmethod
    def get_login_info(self, website: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def add_login_info(self, website: str, username, password):
        raise NotImplementedError

    # AWS functionality
    @abstractmethod
    def create_user(self, username, password):
        raise NotImplementedError

    @abstractmethod
    def login(self, username, password):
        raise NotImplementedError

    @abstractmethod
    def server_update(self):
        raise NotImplementedError

    # Chrome Extension functionality
    # should now open tcp listening server
    @abstractmethod
    def send_message_chrome(self, message):
        raise NotImplementedError

    # asynchronously fills queue with data read
    @abstractmethod
    def read_message_chrome(self, queue):
        raise NotImplementedError

    @abstractmethod
    def send_login_chrome(self, website):
        raise NotImplementedError

    # C Vault functionality
    @abstractmethod
    def create_user_file(self, username, password):
        raise NotImplementedError

    @abstractmethod
    def open_user_file(self, username, password):
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
        self._vault = vault.Vault()

    # Clipboard thread
    def start_clipboard(self):
        threading.Thread(None, self._clipboard_bg_process,
                         args=(self.clipboard_queue,), daemon=True)

    def _clipboard_bg_process(self, item_q: Queue):
        last_item = datetime.datetime.utcnow()
        while True:
            if datetime.datetime.utcnow() - last_item > datetime.timedelta(seconds=30):
                clear_clipboard()
            try:
                item = item_q.get(block=False)
                last_item = datetime.datetime.utcnow()
                copy_clipboard(item)
            except Empty:
                time.sleep(0.1)

    # UI functionality
    def sign_up(self, username, password):
        raise NotImplementedError

    def forgot_password(self, username):
        raise NotImplementedError

    def log_in(self, username, password):
        return self.open_user_file(username, password)

    def get_websites(self):
        raise NotImplementedError

    def get_login_info(self, website):
        raise NotImplementedError

    def add_login_info(self, website, username, password):
        raise NotImplementedError

    # AWS functionality
    def create_user(self, username, password):
        # this will probably be called by server_update() after create_file() is used
        # db.create_user(username, )
        raise NotImplementedError

    def login(self, username, password):
        raise NotImplementedError

    def server_update(self):
        raise NotImplementedError

    # Chrome Extension functionality
    # should now open tcp listening server
    def send_message_chrome(self, message):
        raise NotImplementedError

    # asynchronously fills queue with data read
    def read_message_chrome(self, queue):
        raise NotImplementedError

    def send_login_chrome(self, website):
        username, password = self._vault.get_value(
            website)  # python memory security
        self.send_message_chrome(
            '{"username": "{}", "password": "{}"}'.format(username, password))

    # C Vault functionality
    def create_user_file(self, username, password):
        return self._vault.create_vault('../vault', username, password)

    def open_user_file(self, username, password):
        return self._vault.open_vault('../vault', username, password)

    def add_credential(self, website, username, password):
        value = struct.pack('i', len(username))
        value += username.encode()
        value += password.encode()

        return self._vault.add_key(0, website, value)

    def get_credentials(self, website):
        key_type, data = self._vault.get_value(website)
        if key_type == 1:
            return (data,)
        elif key_type == 0:
            user_len = struct.unpack(data[0:4])
            username = data[4:4 + user_len].decode('utf-8')
            password = data[4 + user_len:].decode('utf-8')
            return (username, password)
        return tuple()

    def get_keys(self):
        raise NotImplementedError
