import threading
import socket

host = '127.0.0.1' # Dirección IP del servidor
port = 55555 # Puerto del servidor

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crear un objeto socket para el servidor
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Configurar el socket para reutilizar la dirección
server.bind((host, port)) # Enlazar el servidor al host y puerto especificado
server.listen() # Escuchar conexiones entrantes

clients = [] # Lista de clientes conectados
usernames = [] # Lista de nombres de usuario de los clientes
rooms = [] # Lista de salas de chat

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
            # Transmitir mensaje a todos los clientes
            broadcast(message)
        except:
            # Eliminar y cerrar la conexión con el cliente
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} ha abandonado el chat.'.encode('utf-8'))
            usernames.remove(username)
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

        client.send('ROOM'.encode('utf-8'))
        room = client.recv(1024).decode('utf-8')
        rooms.append(room)
        # clients.append(client)

        # Anunciar la conexión del cliente a todos los clientes
        print(f"El nombre de usuario del cliente es {username}")
        broadcast(f'{username.upper()} se ha unido al chat.'.encode('utf-8'))

        client.send('Conectado al servidor.'.encode('utf-8'))

        # Iniciar un hilo para manejar la conexión del cliente
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print("Servidor de chat iniciado. Esperando conexiones...")
receive()