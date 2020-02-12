from os import urandom
from random import SystemRandom
import pandas as pd
 
# generates a password with maximum specified length
# permits repetition of characters from the character set to increase size of search space
def generate_password(length=15):
    # use choice rather than urandom for platform independence
    choice = SystemRandom().choice
    character_set = {'lwrcase': 'abcdefghijklmnopqrstuvwxyz',
                    'uprcase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                    'numbers': '0123456789',
                    'special': '!@#$%^&*()-_=+\\/,.?;:[]{}<>|\'\"'
                    }
    password = []
    while len(password) < length:
        char_set = choice(list(character_set.values()))
        password.append(choice(char_set))
    return ''.join(password)

# import date from csv file
# file must be in same directory, otherwise include path as well
# template by column: url, username, password
def read_csv(filename):
    data = pd.read_csv(filename)
    for index, row in data.iterrows():
        if row[0] == "" or row[1] == "" or row[2] == "":
            print("Error: missing data field for entry number " + str(index + 1))
            continue
        url = row[0]
        username = row[1]
        password = row[2]
        """
        Add code here to incorporate data to password vault
        """