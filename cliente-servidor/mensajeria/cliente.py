import socket
import threading

HOST = "127.0.0.1"
PORT = 8000


def recibir_mensaje(conexion):
    while True:
        try:
            datos = conexion.recv(1024)

            if not datos:
                print("\nCliente desconectado")
                break

            print(f"\nMensaje recibido: {datos.decode()}")
            print(">", end=" ", flush=True)

        except ConnectionResetError:
            print("Conexion cerrada")
            break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    cliente.connect((HOST, PORT))

    print(f"Conectado al servidor")
    print("Ingrese su mensaje (escriba '0' para desconectarse):")

    hilo = threading.Thread(target=recibir_mensaje, args=(cliente,), daemon=True)
    
    hilo.start()

    while True:
        mensaje = input("> ")

        if mensaje.lower() == "0":
            print("Desconectando del servidor...")
            break

        cliente.sendall(mensaje.encode())





