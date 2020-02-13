from os import urandom
import random
import secrets

# generates a password with maximum specified length
# permits repetition of characters from the character set to increase size of search space
character_set = {'lwrcase': 'abcdefghijklmnopqrstuvwxyz',
                 'uprcase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                 'numbers': '0123456789',
                 'special': '!@#$%^&*()-_=+\\/,.?;:[]{}<>|\'\"'
                }
    
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

def generate_password(length=0):
    if not length:
        length = secrets.randbelow(17)+8
    password = []
    while len(password) < length:
        char_set = choice(list(character_set.values()))
        password.append(choice(char_set))
    return ''.join(password)