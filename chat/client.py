# client.py
import threading
import socket
import argparse
import logging
import sys

from utils.utils import get_random_username

def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat client")
    parser.add_argument("-a", "--address", type=str, help="Server address", default="127.0.0.1")
    parser.add_argument("-ip6", "--ipv6", action="store_true", help="Use IPv6", default=False)
    parser.add_argument("-p", "--port", type=int, help="Server port", default=55555)
    parser.add_argument("-u", "--username", type=str, help="Username", default=get_random_username())
    return parser.parse_args()

class ChatClient:
    def __init__(self, address, port, ipv6, username):
        self.address = address
        self.port = port
        self.ipv6 = ipv6
        self.username = username
        self.client = None
        self.shutdown_event = threading.Event()

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self.client = socket.socket(socket.AF_INET6 if self.ipv6 else socket.AF_INET, socket.SOCK_STREAM) #automatizar
            self.client.connect((self.address, self.port))
            self.logger.info(f"Connected to server at {self.address}:{self.port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {e}")
            raise

    def receive(self):
        while not self.shutdown_event.is_set():
            try:
                message = self.client.recv(1024).decode('utf-8')
                if not message:
                    self.logger.info("Server closed the connection.")
                    self.shutdown_event.set()
                    break
                
                if message == 'AUTH':  # request de Autenticacion del server
                    # simple autenticacion
                    username = input("Enter username: ")
                    self.username = username
                    password = input("Enter password: ")
                    self.client.send(f"{username}:{password}".encode('utf-8'))
                else:
                    print(message)
            except Exception as e:
                if not self.shutdown_event.is_set():
                    self.logger.error(f"Error receiving message: {e}")
                self.shutdown_event.set()
                break

    def send(self):
        while not self.shutdown_event.is_set():
            try:
                message = input()
                if message.strip().upper() == "EXIT":
                    self.logger.info("Sending EXIT command to server.")
                    self.client.send("EXIT".encode('utf-8'))
                    self.shutdown_event.set()
                    self.shutdown()  # Cierra el cliente de inmediato
                    break
                elif message.strip():
                    self.client.send(f'{self.username}: {message}'.encode('utf-8'))
            except Exception as e:
                if not self.shutdown_event.is_set():
                    self.logger.error(f"Error sending message: {e}")
                self.shutdown_event.set()
                break

    def shutdown(self):
        self.logger.info("Shutting down client...")
        self.shutdown_event.set()
        if self.client:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except Exception as e:
                self.logger.error(f"Error closing socket: {e}")
        self.logger.info("Client shut down successfully.")

    def run(self):
        try:
            self.connect()
            receive_thread = threading.Thread(target=self.receive)
            send_thread = threading.Thread(target=self.send)

            receive_thread.start()
            send_thread.start()

            receive_thread.join()
            send_thread.join()
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received. Shutting down...")
        finally:
            self.shutdown()
            self.logger.info("Exiting program.")
            sys.exit(0)

if __name__ == '__main__':
    args = parse_arguments()
    client = ChatClient(args.address, args.port, args.ipv6, args.username)
    client.run()