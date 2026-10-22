import json
import socket
import struct
from typing import Any

MAX_FRAME = 1_000_000


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