import socket
import sys
import threading

from mensajeria.protocolo import enviar_mensaje, recibir_mensaje
from mensajeria.registro import RegistroClientes

HOST = "127.0.0.1"
PUERTO = 8000


def retransmitir(registro: RegistroClientes, emisor: str, texto: str) -> None:
    """Envía "emisor: texto" a todos los conectados menos al emisor."""
    mensaje = f"{emisor}: {texto}"
    # Requisito 4: Se copia la lista de destinatarios bajo el lock, envío FUERA del lock.
    destinatarios = registro.destinatarios(excepto=emisor)
    
    for nombre, conexion in destinatarios:
        try:
            enviar_mensaje(conexion, mensaje)
        except (socket.error, BrokenPipeError, ConnectionResetError):
            # Requisito 5: Si falla el envío (destinatario al que ya no se puede enviar), se retira.
            registro.borrar(nombre)
            try:
                conexion.close()
            except Exception:
                pass

# El metodo retransmitir se encarga de enviar el mensaje a todos los clientes conectados, excepto al emisor.


def atender(
    conexion: socket.socket, direccion: tuple[str, int], registro: RegistroClientes
) -> None:
    """Atiende a UN cliente, en su propio hilo, hasta que se desconecta."""
    nombre = None
    registrado = False  # Bandera para saber si logró registrarse
    try:
        # Requisito 2: La primera trama del cliente es su nombre.
        nombre = recibir_mensaje(conexion)
        if not nombre:
            conexion.close()
            return

        # Intenta registrar el nombre
        if not registro.insertar(nombre, conexion):
            enviar_mensaje(conexion, "ERROR: nombre en uso")
            conexion.close()
            return

        registrado = True 
        enviar_mensaje(conexion, "OK")

        while True:
            texto = recibir_mensaje(conexion)
            if texto is None:  # Desconexión del cliente
                break
            # Requisito 3: Cada trama siguiente se retransmite a todos los demás
            retransmitir(registro, nombre, texto)

    except (socket.error, ConnectionResetError, BrokenPipeError):
        pass
    finally:
        # Requisito 5: Solo se borra del registro si llegó a registrarse
        if registrado and nombre:
            registro.borrar(nombre)
        try:
            conexion.close()
        except Exception:
            pass

# El metodo atender se encarga de recibir el nombre del cliente, registrarlo y luego recibir los mensaje que envía para retransmitirlos a los demás clientes. Si el cliente se desconecta o hay un error en la conexión, se borra del registro y se cierra la conexión.






def main() -> None:

    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else PUERTO
    registro = RegistroClientes()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, puerto))
        servidor.listen()
        print(f"escuchando en {HOST}:{puerto}")
        
        while True:
            conexion, direccion = servidor.accept()
            hilo = threading.Thread(target=atender, args=(conexion, direccion, registro), daemon=True)
            hilo.start()

# Lo que hace el main es crear un hilo para cada cliente que se conecta, y en ese hilo se llama la función de atender, que se encarga de recibir el nombre del cliente, registrarlo y luego recibir los mensajes que envía para retransmitirlos a los demás clientes. Si el cliente se desconecta o hay un error en la conexión, se borra del registro y se cierra la conexión. 


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nservidor detenido")