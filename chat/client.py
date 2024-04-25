import threading
import socket
import argparse
import random


# get random username
def get_random_username():
    adjectives = ['happy', 'sad', 'angry', 'sleepy', 'hungry', 'thirsty', 'bored', 'excited', 'tired', 'silly']
    nouns = ['cat', 'dog', 'bird', 'fish', 'rabbit', 'hamster', 'turtle', 'parrot', 'snake', 'lizard']
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return f'{adjective.capitalize()} {noun.capitalize()}'

# parse arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat client")
    parser.add_argument("address", nargs='?', type=str, help="Server address", default="127.0.0.1")
    parser.add_argument("port", nargs='?', type=int, help="Server port", default=55555)
    parser.add_argument("username", nargs='?', type=str, help="Username", default=get_random_username())
    return parser.parse_args()




def receive(client, username):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(username.encode('utf-8'))
            else:  
                print(message)
        except:
            print("Error al recibir mensajes.")
            client.close()
            break


def send(client, username):
    while True:
        message = f'{username}: {input("")}'
        client.send(message.encode('utf-8'))


# receive_thread = threading.Thread(target=receive)
# receive_thread.start()

# send_thread = threading.Thread(target=send)
# send_thread.start()


if __name__ == '__main__':
    args = parse_arguments()
    print(args)
    address = args.address
    port = args.port
    username = args.username

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((address, port))


    receive_thread = threading.Thread(target=receive, args=(client, username))
    receive_thread.start()

    send_thread = threading.Thread(target=send, args=(client, username))
    send_thread.start()
    # client = Client(address, port)
    # client.send_thread.join()
    # client.receive_thread.join()