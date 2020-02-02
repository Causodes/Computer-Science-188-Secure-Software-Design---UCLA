from os import urandom
from random import SystemRandom

# use choice rather than urandom for platform independence
choice = SystemRandom().choice

character_set = {'lwrcase': 'abcdefghijklmnopqrstuvwxyz',
                 'uprcase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                 'numbers': '0123456789',
                 'special': '!@#$%^&*()-_=+\\/,.?;:[]{}<>|\'\"'
                }
 
# generates a password with maximum specified length
# permits repetition of characters from the character set to increase size of search space
def generate_password(length=15):
    password = []
    char_set = choice(character_set)
    while len(password) < length:
        password.append(choice(char_set))
    return ''.join(password)