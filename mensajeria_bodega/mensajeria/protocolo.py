import json
import socket
import struct
from typing import Any

MAX_FRAME = 1_000_000


## define como se envian y se reciben los mensajes en la comunicación entre cliente y servidor, usando JSON y una cabecera de longitud de 4 bytes.

## El json es un formato de texto ligero y estandarizado para el intercambio de datos, y la cabecera de longitud permite al receptor saber cuántos bytes debe leer para obtener el mensaje completo.

def send_frame(
    sock: socket.socket,
    data: dict[str, Any]
) -> None:
    """Envía un objeto JSON precedido por su longitud."""
    payload = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":")
    ).encode("utf-8")

    if not payload or len(payload) > MAX_FRAME:
        raise ValueError("Trama vacía o demasiado grande")

    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


# Convierte un diccionario a JSON, lo codifica en UTF-8 y envía una cabecera de cuatro bytes con la longitud, seguida del contenido

def recv_exact(sock: socket.socket, size: int) -> bytes:
    """Lee exactamente la cantidad de bytes solicitada."""
    chunks = bytearray()

    while len(chunks) < size:
        part = sock.recv(size - len(chunks))

        if not part:
            raise ConnectionError(
                "Conexión cerrada a mitad de trama"
            )

        chunks.extend(part)

    return bytes(chunks)


# Lee exactamente la cantidad de bytes solicitada, aunque lleguen en varios fragmentos.


def recv_frame(sock: socket.socket) -> dict[str, Any]:
    """Recibe una trama completa y la convierte desde JSON."""
    header = recv_exact(sock, 4)
    (length,) = struct.unpack("!I", header)

    if length <= 0 or length > MAX_FRAME:
        raise ValueError("Longitud de trama inválida")

    payload = recv_exact(sock, length)
    data = json.loads(payload.decode("utf-8"))

    if not isinstance(data, dict):
        raise ValueError("El mensaje JSON debe ser un objeto")  # noqa: TRY004

    return data

# Lee la longitud, recibe la trama completa, decodifica el JSON y comprueba que sea un diccionario.