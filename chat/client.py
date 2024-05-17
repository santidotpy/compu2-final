import threading
import socket
import argparse
import random

def get_random_username():
    adjectives = ['happy', 'sad', 'angry', 'sleepy', 'hungry', 'thirsty', 'bored', 'excited', 'tired', 'silly']
    nouns = ['cat', 'dog', 'bird', 'fish', 'rabbit', 'hamster', 'turtle', 'parrot', 'snake', 'lizard']
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return f'{adjective.capitalize()} {noun.capitalize()}'

def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat client")
    parser.add_argument("-a", "--address", nargs='?', type=str, help="Server address", default="127.0.0.1")
    parser.add_argument("port", nargs='?', type=int, help="Server port", default=55555)
    parser.add_argument("username", nargs='?', type=str, help="Username", default=get_random_username())
    return parser.parse_args()

shutdown_event = threading.Event()

def receive(client, username):
    while not shutdown_event.is_set():
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(username.encode('utf-8'))
            elif message == 'EXIT':
                print("Shutdown signal received.")
                shutdown_event.set()
                break
            else:
                print(message)
        except:
            print("Error receiving messages.")
            shutdown_event.set()
            client.close()
            break

def send_image(client, username):
    try:
        client.send(f'IMAGE:{username}'.encode('utf-8'))
        with open('../images/homelander.jpg', 'rb') as file:  # Adjust the path as necessary
            while True:
                image_data = file.read(2048)
                if not image_data:
                    break
                client.send(image_data)
            client.send(b'ENDIMG')  # Sending an end signal to indicate that image transfer is complete
    except:
        print("Error sending image.")

def send(client, username):
    while not shutdown_event.is_set():
        message = input("")
        if message.strip().upper() == "EXIT":
            client.send("EXIT".encode('utf-8'))
            shutdown_event.set()
            break
        elif message.strip() == "":  # Ignore empty messages
            continue
        elif message == "/img":
            # client.send(f"IMAGE".encode('utf-8'))
            try:
                send_image(client, username)
            except:
                print("Error sending image.")
        else:
            client.send(f'{username}: {message}'.encode('utf-8'))

if __name__ == '__main__':
    args = parse_arguments()
    address = args.address
    port = args.port
    username = args.username

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((address, port))

    receive_thread = threading.Thread(target=receive, args=(client, username))
    receive_thread.start()

    send_thread = threading.Thread(target=send, args=(client, username))
    send_thread.start()

    receive_thread.join()
    send_thread.join()
    client.close()
    print("Connection closed.")
