"""Main password bank application

This module creates and defines a main Bank object that interacts with
the rest of the application, acting as the entrypoint to the application
"""
from dataclasses import dataclass


@dataclass
class Credentials:
    """Data struct to bundle user data together

    Attributes
    ----------
    website : str
        String representation of the website to match (e.g. google)
    username : str
        The user's username for that website
    password : str
        The user's password for that website
    """
    website: str = None
    username: str = None
    password: str = None


class Bank:
    def __init__(self):
        raise NotImplementedError

    # AWS functionality
    def create_user(self, username, password):
        # this will probably be called by server_update() after create_file() is used
        raise NotImplementedError

    def login(self, username, password):
        raise NotImplementedError

    def server_update(self):
        raise NotImplementedError

    # Chrome Extension functionality
    def send_message_chrome(self, message):
        raise NotImplementedError

    def read_message_chrome(self):
        # likely will need to be implemented asynchronously/via threads
        raise NotImplementedError

    def send_login_chrome(self, website):  # bridge between chrome and vault
        raise NotImplementedError

    # C Vault functionality
    def create_user_file(self, username, password):
        raise NotImplementedError

    def open_user_file(self):
        raise NotImplementedError

    def add_credential(self, website, username, password)

    def get_credentials(self, website):
        raise NotImplementedError

    def get_keys(self):
        raise NotImplementedError
