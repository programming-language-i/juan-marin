import socket
import threading

HOST = "127.0.0.1"
PORT = 8000

clientes = {}
lock = threading.Lock()

nombres = ["Ana", "Luis", "Pedro", "Maria", "Carlos", "Sofia", "Diego", "Lucia"]

contador_clientes = 0


def enviar_mensaje(mensaje, cliente_actual=None):
    print("Función de atención de mensajes")
    with lock:
        for cliente in clientes:
            if cliente != cliente_actual:
                try:
                    cliente.sendall(mensaje)
                except OSError:
                    print("error al enviar")


def atender_clientes(conexion, direccion):
    global contador_clientes

    with lock:
        nombre = nombres[contador_clientes % len(nombres)]

        if any(n == nombre for n in clientes.values()):
            nombre = f"{nombre}{contador_clientes}"

        contador_clientes += 1
        clientes[conexion] = nombre

    print(f"Cliente conectado desde {direccion} -> {nombre}")

    try:
        conexion.sendall(f"Bienvenido, tu nombre es {nombre}\n".encode())
    except OSError:
        pass

    enviar_mensaje(f"[Servidor]: {nombre} se ha conectado.\n".encode(), conexion)

    try:
        while True:
            datos = conexion.recv(1024)

            if not datos:
                break

            mensaje = datos.decode().strip()
            print(f"[{nombre}]: {mensaje}")

            enviar_mensaje(f"[{nombre}]: {mensaje}\n".encode(), conexion)

    except ConnectionResetError:
        print(f"Cliente {nombre} ({direccion}) desconectado")
    finally:
        with lock:
            if conexion in clientes:
                del clientes[conexion]
        conexion.close()

        enviar_mensaje(f"[Servidor]: {nombre} se ha desconectado.\n".encode())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor.bind((HOST, PORT))
    servidor.listen()

    print(f"Servidor escuchando en {HOST}:{PORT}")

    while True:
        conexion, direccion = servidor.accept()
        hilo = threading.Thread(
            target=atender_clientes, args=(conexion, direccion), daemon=True
        )
        hilo.start()