import re
import pyperclip
import pandas as pd
from os import urandom
import random
import time
import secrets
import requests

try:
    rnd = secrets.SystemRandom()
except:
    try:
        rnd = urandom.SystemRandom()
    except:
        try:
            rnd = urandom.Random()
        except:
            rnd = random.Random()
choice = rnd.choice

# -------------------------------------

_deltatime = 0
try:
    _deltatime = requests.post('https://noodlespasswordvault.com/time',
                               verify=True).json()['time'] - time.time()
except:
    pass


def get_time():
    return int(time.time() - _deltatime)


# -------------------------------------


class PasswordGenerator():
    # generates a password with maximum specified length
    # permits repetition of characters from the character set to increase size of search space

    character_set = {
        'lwrcase': 'abcdefghijklmnopqrstuvwxyz',
        'uprcase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'numbers': '0123456789',
        'special': '!@#$%^&*()-_=+\\/,.?;:[]{}<>|\'\"'
    }

    @staticmethod
    def generate_password(length=0):
        if not length:
            length = secrets.randbelow(17) + 8
        password = []
        while len(password) < length:
            char_set = choice(list(PasswordGenerator.character_set.values()))
            password.append(choice(char_set))
        return ''.join(password)


# -------------------------------------------------------

# import date from csv file
# file must be in same directory, otherwise include path as well
# template by column: url, username, password


def read_csv(filename):
    data = pd.read_csv(filename)
    for index, row in data.iterrows():
        if not (row[0] and row[1] and row[2]):
            print("Error: missing data field for entry number " +
                  str(index + 1))
            continue
        url, username, password = row
        """
        Add code here to incorporate data to password vault
        """


# -------------------------------------


def copy_clipboard(password):
    pyperclip.copy(password)
    pyperclip.paste()


def clear_clipboard():
    pyperclip.copy("")
    pyperclip.paste()


# ------------------------------------


class PasswordVerifier():
    # checks complexity of password
    keyboard_row_set = [
        '`1234567890-=', '~!@#$%^&*()_+', 'qwertyuiop[]\\', 'QWERTYUIOP{}|',
        'asdfghjkl;\'', 'ASDFGHJKL:\"', 'zxcvbnm,./', 'ZXCVBNM<>?'
    ]

    @staticmethod
    def simplicity_checker(password):
        length = len(password)
        if not length:
            print("Password is of length 0.")
            return False

        digits = 0
        lowerCase = 0
        upperCase = 0
        others = 0
        unknowns = 0
        adjacentCharCount = 0
        uniqueCharSet = set()
        flag = 1

        for i, element in enumerate(password):
            # check number of unique types of characters
            if ord(element) >= 128:
                unknowns += 1
            elif element.isdigit():
                digits += 1
            elif element.islower():
                lowerCase += 1
            elif element.isupper():
                upperCase += 1
            else:
                others += 1
            uniqueCharSet.add(element)

            # check for adjacent characters on keyboard
            keyboard_row = list(
                filter(lambda x: element in x,
                       PasswordVerifier.keyboard_row_set))[0]
            row_index = PasswordVerifier.keyboard_row_set.index(keyboard_row)
            element_index = PasswordVerifier.keyboard_row_set[row_index].find(
                element)
            row_index = int(row_index / 2) * 2
            if element_index and i:
                if password[i -
                            1] == PasswordVerifier.keyboard_row_set[row_index][
                                element_index - 1] or password[
                                    i - 1] == PasswordVerifier.keyboard_row_set[
                                        row_index + 1][element_index - 1]:
                    adjacentCharCount += 1
            if element_index < len(PasswordVerifier.keyboard_row_set[row_index]
                                  ) - 1 and i < len(password) - 1:
                if password[i +
                            1] == PasswordVerifier.keyboard_row_set[row_index][
                                element_index + 1] or password[
                                    i + 1] == PasswordVerifier.keyboard_row_set[
                                        row_index + 1][element_index + 1]:
                    adjacentCharCount += 1

        # check for number of unique classes
        uniqueClasses = 0
        if digits:
            uniqueClasses += 1
        if lowerCase:
            uniqueClasses += 1
        if upperCase:
            uniqueClasses += 1
        if others:
            uniqueClasses += 1
        if unknowns:
            uniqueClasses += 1

        if length < 8:
            print(
                "Please use a password with a length of at least 8 characters")
            flag = 0

        # check for interleaving
        if len(re.split('(\d+)', password)) <= 3:
            print("Too many consecutive character types; try interleaving.")
            flag = 0

        if len(uniqueCharSet) > len(password) / 2:
            print("Not enough unique characters in the password.")
            flag = 0
        if uniqueClasses < 3:
            print("Not enough diversity in character type.")
            flag = 0
        if flag:
            return True
        return False
