import threading
import socket
import argparse
from datetime import datetime
import sys

# Firestore
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("../credentials.json")
firebase_admin.initialize_app(cred)

clients = [] # Lista de clientes conectados
usernames = [] # Lista de nombres de usuario de los clientes
messages = [] # Lista de mensajes de chat


def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat server")
    parser.add_argument("host", nargs='?', type=str, help="Server host", default="127.0.0.1")
    parser.add_argument("port", nargs='?', type=int, help="Server port", default=55555)
    parser.add_argument("usedb", nargs='?', type=bool, help="Bool to use db", default=True)
    return parser.parse_args()


def get_author_and_message(message):
    parts = message.split(':', 1)  # Dividir en dos partes máximo
    author = parts[0]
    message = parts[1].strip()  # Eliminar espacios al principio y al final
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
    data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # "messages": [get_message_data(message) for message in messages],
        # "messages":[ message.decode('utf-8') for message in messages],
        "messages": only_messages,
        "author": author
    }
    return data

    # return [get_message_data(message) for message in messages]

# def otraManeraDeLoDeArriba(author, messages):
#     data = []
#     data.append({
#         "author": author,
#         "messages": messages,
#         "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     })
#     return data

def save_messages(author, messages):
    doc_ref = db.collection("chatCollection").document()
    doc_ref.set(get_messages_data(author, messages))


def save_message(message):
    doc_ref = db.collection("chatCollection").document()
    doc_ref.set(get_message_data(message))


# Función para transmitir mensajes a todos los clientes
def broadcast(message):
    for client in clients:
        client.send(message)

# Función para manejar las conexiones de los clientes
def handle_client(client):
    while True:
        try:
            # Recibir mensaje del cliente
            message = client.recv(1024)
            author, only_message = get_author_and_message(message.decode('utf-8'))
            messages.append(message)
            # if use_db: save_message(message.decode('utf-8'))
            # Transmitir mensaje a todos los clientes
            broadcast(message)
            print(only_message)
            print(only_message == 'exit')
            if only_message == 'EXIT':
                raise Exception("Cliente desconectado.")
        except:
            # Eliminar y cerrar la conexión con el cliente
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            print(f"Mensajes enviados por {username} eliminados. {messages}")
            broadcast(f'{username} ha abandonado el chat.'.encode('utf-8'))
            usernames.remove(username)

            if only_message == 'EXIT':
                if use_db: save_messages(author, messages)
                broadcast(b'Server is shutting down.')
                server.close()
                sys.exit("Server closed by admin.")
            break


# Función principal para aceptar conexiones de clientes
def receive():
    while True:
        # Aceptar la conexión del cliente
        client, address = server.accept()
        print(f"Conexión establecida con {str(address)}")

        # Solicitar y almacenar el nombre de usuario del cliente
        client.send('NICK'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
        clients.append(client)

        # Anunciar la conexión del cliente a todos los clientes
        print(f"El nombre de usuario del cliente es {username}")
        broadcast(f'{username} se ha unido al chat.'.encode('utf-8'))

        client.send('Conectado al servidor.'.encode('utf-8'))

        # Iniciar un hilo para manejar la conexión del cliente
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == '__main__':
    args = parse_arguments()
    host = args.host
    port = args.port
    use_db = args.usedb
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crear un objeto socket para el servidor
    server.bind((host, port)) # Enlazar el servidor al host y puerto especificado
    server.listen() # Escuchar conexiones entrantes

    # Initialize Firestore client if the 'use_db' flag is set to True
    if use_db: 
        try:
            print("Firestore client initialized.")
            db = firestore.client()
        except:
            print("Error al inicializar el cliente de Firestore.")
            use_db = False

    print("Servidor de chat iniciado. Esperando conexiones...")
    receive()