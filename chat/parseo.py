import argparse
import random

# get random username
def get_random_username():
    adjectives = ['happy', 'sad', 'angry', 'sleepy', 'hungry', 'thirsty', 'bored', 'excited', 'tired', 'silly']
    nouns = ['cat', 'dog', 'bird', 'fish', 'rabbit', 'hamster', 'turtle', 'parrot', 'snake', 'lizard']
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return f'{adjective.capitalize()} {noun.capitalize()}'

def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat client")
    parser.add_argument("address", nargs='?', type=str, help="Server address", default="127.0.0.1")
    parser.add_argument("port", nargs='?', type=int, help="Server port", default=55555)
    parser.add_argument("username", nargs='?', type=str, help="Username", default=get_random_username())
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    print(args.address)
    print(args.port)
    print(args.username)
