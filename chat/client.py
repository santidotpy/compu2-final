import threading
import socket


username = input("Nombre de usuario: ")
room = int(input("Nombre de la sala de chat o nada para continuar: "))
print(room)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(username.encode('utf-8'))

            elif message == 'ROOM':
                client.send(str(room).encode('utf-8'))
            else:  
                print(message)
        except:
            print("Error al recibir mensajes.")
            client.close()
            break


def send():
    while True:
        message = f'{username.upper()}: {input("")}'
        client.send(message.encode('utf-8'))


receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()