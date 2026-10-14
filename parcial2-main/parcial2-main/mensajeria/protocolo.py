"""
PARCIAL 2 - Nivel 1 (20 pts) · Framing

TCP es un flujo de bytes, no de mensajes. Cada mensaje viaja así:

    4 bytes con la longitud del cuerpo (big-endian)  +  el cuerpo en UTF-8

Complete los TODO. No cambie los nombres ni las firmas: las pruebas, el
servidor y los clientes importan estas tres funciones.

Requisitos:
  1. El prefijo es struct.pack("!I", n), donde n es la longitud EN BYTES del
     cuerpo ya codificado.
  2. recibir_exacto llama a recv() EN BUCLE hasta completar los n bytes.
  3. UTF-8 explícito al codificar y al decodificar.
  4. Si recv() devuelve bytes vacíos, la conexión se cerró: se devuelve None.

Se comprueba con:   python3 prueba_n1.py   (desde la carpeta parcial2/)
"""

import socket
import struct


def recibir_exacto(sock: socket.socket, n: int) -> bytes | None:
    """Lee exactamente n bytes. Devuelve None si la conexión se cerró antes."""
    datos = bytearray()
    while len(datos) < n:
        paquete = sock.recv(n - len(datos))
        if not paquete:
            return None
        datos.extend(paquete)
    return bytes(datos)


# Seirve para recibir los bytes n, devolviendo None si la conexión se cerró antes. Esto ya que no garantizamos que lleguen todos los bytes en una sola llamada a recv(). Por eso, se hace un bucle hasta recibir todos los bytes o hasta que la conexión se cierre.  (Resumiendo, este nos garantiza si tenemos algun error en la conexión o si se cerró antes de recibir todos los bytes, devolviendo None en ese caso.)


def enviar_mensaje(sock: socket.socket, texto: str) -> None:
    """Envía texto en UTF-8 precedido de su longitud en 4 bytes big-endian."""
    cuerpo = texto.encode("utf-8")
    prefijo = struct.pack("!I", len(cuerpo))
    sock.sendall(prefijo + cuerpo)

    # Este sirve para verificar la longitud del mensaje y enviarlo correctamente. Utilizando el UTF-8 para codificar el texto y luego empaquetando la longitud del cuerpo en 4 bytes big-endian. Finalmente, se envía todo junto con sendall() para asegurarse de que se envíe todo el mensaje completo.


def recibir_mensaje(sock: socket.socket) -> str | None:
    """Lee un mensaje completo. Devuelve None si el otro extremo cerró."""
    prefijo_bytes = recibir_exacto(sock, 4)
    if prefijo_bytes is None:
        return None
    
    largo = struct.unpack("!I", prefijo_bytes)[0]
    cuerpo_bytes = recibir_exacto(sock, largo)
    if cuerpo_bytes is None:
        return None
        
    return cuerpo_bytes.decode("utf-8")


#En este caso utilizamos prefijos_bytes para recibir los primeros 4 bytes que indica la longitud del mensaje. utilizando largo para desempaquetar la longitud de los bytes y luego recibir el cuerpo del mensaje con recibir_exacto.