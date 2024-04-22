import threading
import socket
import argparse
import random

# class Client:
#     def __init__(self, address, port):
#         self
#         self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.client.connect((address, port))
#         self.receive_thread = threading.Thread(target=self.receive)
#         self.receive_thread.start()
#         self.send_thread = threading.Thread(target=self.send)
#         self.send_thread.start()





#     #     # self.receive_thread = threading.Thread(target=self.receive)
#     #     # self.receive_thread.start()
#     #     # self.send_thread = threading.Thread(target=self.send)
#     #     # self.send_thread.start()

#     # def receive(self):
#     #     while True:
#     #         try:
#     #             message = self.client.recv(1024).decode('utf-8')
#     #             if message == 'NICK':
#     #                 self.client.send(username.encode('utf-8'))
#     #             else:
#     #                 print(message)
#     #         except:
#     #             print("Error al recibir mensajes.")
#     #             self.client.close()
#     #             break
                
#     # def send(self):
#     #     while True:
#     #         message = f'{username}: {input("")}'
    #         self.client.send(message.encode('utf-8'))


# get random username
def get_random_username():
    adjectives = ['happy', 'sad', 'angry', 'sleepy', 'hungry', 'thirsty', 'bored', 'excited', 'tired', 'silly']
    nouns = ['cat', 'dog', 'bird', 'fish', 'rabbit', 'hamster', 'turtle', 'parrot', 'snake', 'lizard']
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return f'{adjective.capitalize()} {noun.capitalize()}'


# def parse_arguments():
#     parser = argparse.ArgumentParser(description="Chat client")
#     parser.add_argument("address", type=str, help="Server address", default="127.0.0.1")
#     parser.add_argument("port", type=int, help="Server port", default=55555)
#     parser.add_argument("username", type=str, help="Username", default=get_random_username())
#     return parser.parse_args()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat client")
    parser.add_argument("address", nargs='?', type=str, help="Server address", default="127.0.0.1")
    parser.add_argument("port", nargs='?', type=int, help="Server port", default=55555)
    parser.add_argument("username", nargs='?', type=str, help="Username", default=get_random_username())
    return parser.parse_args()







# username = input("Nombre de usuario: ")

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(('127.0.0.1', 55555))

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