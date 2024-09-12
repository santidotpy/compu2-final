# utils.py
import bcrypt
import random

def authenticate(queue, response_queue):
    """Proceso simple de autenticación de usuarios."""
    users_db = {"user1": "$2b$12$RMnLBi9JqPwyJjhbHSJYzePcHfTWPYed/re4wrZ7fnvuY78uqgWp6", 
                "user2": "password2"}  # Dummy users
    
    while True:
        data = queue.get()
        if data == 'STOP':
            break
        
        username, password = data

        if username in users_db and users_db[username] == password:
            response_queue.put((username, True))
        else:
            response_queue.put((username, False))


def get_random_username():
    adjectives = ['happy', 'sad', 'angry', 'sleepy', 'hungry', 'thirsty', 'bored', 'excited', 'tired', 'silly']
    nouns = ['cat', 'dog', 'bird', 'fish', 'rabbit', 'hamster', 'turtle', 'parrot', 'snake', 'lizard']
    return f'{random.choice(adjectives).capitalize()} {random.choice(nouns).capitalize()}'


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
