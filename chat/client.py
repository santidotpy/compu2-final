import threading
import socket

username = input("Nombre de usuario: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

stop_receive = False  # Variable para controlar si se debe detener la recepción de mensajes

def receive():
    global stop_receive
    while not stop_receive:
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

def send():
    global stop_receive
    while True:
        message = input("")  # Recibir mensaje del usuario
        if message == "EXIT":  # Si el mensaje es "exit", enviarlo y detener la recepción de mensajes
            client.send(message.encode('utf-8'))
            stop_receive = True
            break
        else:
            client.send(f'{username}: {message}'.encode('utf-8'))  # Enviar mensaje al servidor

receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()

send_thread.join()  # Esperar a que el hilo de envío termine antes de cerrar el cliente
receive_thread.join()  # Esperar a que el hilo de recepción termine antes de cerrar el cliente
client.close()  # Cerrar el socket del cliente después de enviar "exit"



