import threading
import socket
import argparse
from datetime import datetime
import base64
import os

# Firestore
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("../credentials.json")  # Adjust the path as necessary
firebase_admin.initialize_app(cred)

clients = []  # List of connected clients
usernames = []  # List of client usernames
messages = []  # List of chat messages

def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat server")
    parser.add_argument("host", nargs='?', type=str, help="Server host", default="0.0.0.0")
    parser.add_argument("port", nargs='?', type=int, help="Server port", default=55555)
    parser.add_argument("--usedb", type=lambda s: s.lower() in ['true', 't', 'yes', '1'], help="Bool to use db", default=True)
    return parser.parse_args()

def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read())

def get_author_and_message(message):
    parts = message.split(':', 1)  # Split into a maximum of two parts
    if len(parts) < 2:
        return "", message  # Return empty author if message does not contain ':'
    author = parts[0]
    message = parts[1].strip()  # Strip leading and trailing spaces
    return author, message

def get_message_data(message):
    author, message = get_author_and_message(message)
    return {
        "author": author,
        "message": message,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_messages_data(author, messages):
    only_messages = [get_author_and_message(message.decode('utf-8'))[1] for message in messages]
    img_base64 = img_to_base64('../received_images/received_image.jpg')
    if os.path.exists('../received_images/received_image.jpg'):
        only_messages.append(f'IMAGE: {img_base64}')
    data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": only_messages,
        "author": author
    }
    return data

def save_messages(author, messages):
    doc_ref = db.collection("chatCollection").document()
    doc_ref.set(get_messages_data(author, messages))

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                raise Exception("Received empty message")
            
            author, only_message = get_author_and_message(message.decode('utf-8'))
            print(f"Author: {author}, Message: {only_message}")
            if message.decode('utf-8').startswith('IMAGE:'):
                author = message.decode('utf-8').split(':')[1]
                image_path = '../received_images/received_image.jpg'  # Adjust the path as necessary
                os.makedirs(os.path.dirname(image_path), exist_ok=True)  # Create the directory if it doesn't exist
                with open(image_path, 'wb') as file:
                    while True:
                        image_data = client.recv(2048)
                        if b'ENDIMG' in image_data:
                            file.write(image_data.replace(b'ENDIMG', b''))
                            break
                        file.write(image_data)
                broadcast(f'{author} ha enviado una imagen.'.encode('utf-8'))
            else:
                messages.append(message)
                broadcast(message)
                
            if only_message == 'EXIT':
                raise Exception(f"{author} se ha desconectado.")
                
        except Exception as e:
            print(f"Server: {e}")
            index = clients.index(client)
            clients.remove(client)
            client.close()
            if index < len(usernames):
                username = usernames.pop(index)
                broadcast(f'{username} ha abandonado el chat.'.encode('utf-8'))
            if use_db:
                save_messages(author, messages)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Conexión establecida con {str(address)}")

        client.send('NICK'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
        clients.append(client)

        print(f"El nombre de usuario del cliente es {username}")
        broadcast(f'{username} se ha unido al chat.'.encode('utf-8'))

        client.send('Conectado al servidor.'.encode('utf-8'))

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == '__main__':
    args = parse_arguments()
    host = args.host
    port = args.port
    use_db = args.usedb
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(use_db)
    if use_db:
        try:
            print("Firestore client initialized.")
            db = firestore.client()
        except Exception as e:
            print(f"Error al inicializar el cliente de Firestore: {e}")
            use_db = False

    print(f"Servidor de chat iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")
    print("Servidor de chat iniciado. Esperando conexiones...")
    receive()
