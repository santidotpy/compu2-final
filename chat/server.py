# server.py
import threading
import socket
import argparse
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import logging

import multiprocessing
import time

from utils.utils import authenticate


class ChatServer:
    def __init__(self, host="::", port=55555, use_db=True):
        self.host = host
        self.port = port
        self.use_db = use_db
        self.clients = []
        self.usernames = {}
        self.messages = []
        self.lock = threading.Lock()

        # información de la dirección, para IPv4 como para IPv6
        addr_info = socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM)

        # uso la primera dirección encontrada que funcione
        for res in addr_info:
            af, socktype, proto, canonname, sa = res # address family, socket type, protocol, canonical name, socket address
            try:
                self.server = socket.socket(af, socktype, proto)
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server.bind(sa)
                self.server.listen()
                break  # salgo del bucle si esta todo ok
            except socket.error as msg:
                self.server = None
                continue

        if self.server is None:
            raise Exception(f"Could not open socket for {host}:{port}")

        self.auth_queue = multiprocessing.Queue()
        self.auth_response_queue = multiprocessing.Queue()

        # Inicia el proceso de autenticación
        self.auth_process = multiprocessing.Process(target=authenticate, args=(self.auth_queue, self.auth_response_queue))
        self.auth_process.start()

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        if self.use_db:
            self._initialize_firestore()

    def _initialize_firestore(self):
        try:
            cred = credentials.Certificate("../credentials.json")
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.logger.info("Firestore initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Firestore: {e}")
            self.use_db = False

    @staticmethod
    def get_author_and_message(message):
        parts = message.split(':', 1)
        return (parts[0], parts[1].strip()) if len(parts) > 1 else ("", message)
    
    def authenticate_client(self, client):
        """Handle authentication of the client."""
        try:
            client.send('AUTH'.encode('utf-8'))  # request authentication info from the client
            auth_data = client.recv(1024).decode('utf-8').split(':')
            print("AUTH DATA", auth_data)
            if len(auth_data) == 2:
                username, password = auth_data
                self.auth_queue.put((username, password))
                result = self.auth_response_queue.get()  # wait auth result

                if result[1]:  # authentication ok
                    self.logger.info(f"Client {username} authenticated successfully")
                    return username
                else:
                    client.send('Authentication failed.'.encode('utf-8'))
                    client.close()
            else:
                client.send('Invalid authentication data.'.encode('utf-8'))
                client.close()
        except Exception as e:
            self.logger.error(f"Error during authentication: {e}")
            client.close()
        return None

    def get_messages_data(self, author):
        only_messages = [self.get_author_and_message(m.decode('utf-8'))[1] for m in self.messages]
        return {
            "date": datetime.now().isoformat(),
            "messages": only_messages,
            "author": author
        }

    def save_messages(self, author):
        if not self.use_db:
            return

        try:
            @firestore.transactional
            def save_transaction(transaction):
                doc_ref = self.db.collection("nuevaWea").document()
                transaction.set(doc_ref, self.get_messages_data(author))
            
            transaction = self.db.transaction()
            save_transaction(transaction)
            self.logger.info(f"Messages saved for {author}")
        except Exception as e:
            self.logger.error(f"Error saving messages to Firestore: {e}")

    def broadcast(self, message, exclude_client=None):
        with self.lock:
            for client in self.clients:
                if client != exclude_client:
                    try:
                        client.send(message)
                    except Exception as e:
                        self.logger.error(f"Error broadcasting message: {e}")
                        self.remove_client(client)

    def handle_client(self, client):
        try:
            while True:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    self.logger.debug("Empty message received, client disconnected.")
                    break
                
                self.logger.debug(f"Received message: {message}")
                
                author, only_message = self.get_author_and_message(message)

                if only_message.strip().upper() == "EXIT":
                    self.logger.info(f"EXIT command received from {self.usernames.get(client, 'Unknown User')}")
                    # avisar a los demas clientes que alguien se fue
                    self.broadcast(f"{self.usernames.get(client, 'Unknown User')} ha abandonado el chat.".encode('utf-8'), exclude_client=client)
                    break
                else:
                    self.messages.append(message.encode('utf-8'))
                    self.broadcast(message.encode('utf-8'))
                    if self.use_db:
                        self.save_messages(author)
        except Exception as e:
            self.logger.error(f"Error handling client: {e}")
        finally:
            self.remove_client(client)

    def remove_client(self, client):
        with self.lock:
            if client in self.clients:
                self.clients.remove(client)
                username = self.usernames.pop(client, "Unknown User")
                self.logger.info(f"Removed client: {username}")
                self.broadcast(f'{username} ha abandonado el chat.'.encode('utf-8'), exclude_client=client)
                if self.use_db:
                    self.save_messages(username)
            else:
                self.logger.warning("Attempted to remove a client that was not in the list")
            
            try:
                client.close()
            except Exception as e:
                self.logger.error(f"Error closing client socket: {e}")

    def receive(self):
        while True:
            try:
                client, address = self.server.accept()
                self.logger.info(f"Connection established with {address}")
                
                username = self.authenticate_client(client)
                if not username:
                    continue  # skip cliente si la auth falla

                with self.lock:
                    self.usernames[client] = username
                    self.clients.append(client)

                self.logger.info(f"Client username: {username}")
                self.broadcast(f'{username} se ha unido al chat.'.encode('utf-8'))
                client.send('Conectado al servidor.'.encode('utf-8'))

                threading.Thread(target=self.handle_client, args=(client,)).start()
            except Exception as e:
                self.logger.error(f"Error accepting client connection: {e}")

    def shutdown(self):
        """Ensure the authentication process is terminated."""
        self.auth_queue.put('STOP')  # Stop the authentication process
        self.auth_process.join()  # Wait for the process to finish

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chat server")
    parser.add_argument("host", nargs='?', type=str, help="Server host", default="0.0.0.0")
    parser.add_argument("port", nargs='?', type=int, help="Server port", default=55555)
    parser.add_argument("--usedb", type=lambda s: s.lower() in ['true', 't', 'yes', '1'], help="Bool to use db", default=True)
    args = parser.parse_args()

    chat_server = ChatServer(host=args.host, port=args.port, use_db=args.usedb)
    chat_server.logger.info(f"Server running on {args.host}:{args.port}")
    chat_server.logger.info(f"Using Firestore: {args.usedb}")
    chat_server.receive()

