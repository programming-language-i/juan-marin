import json  # noqa: I001
import socket
import threading
import time

from datetime import datetime
from pathlib import Path
from typing import Any

from protocolo import recv_frame, send_frame


HOST = "0.0.0.0"
TCP_PORT = 8000
UDP_PORT = 8001

CHANNELS = {
    "#general",
    "#recepcion",
    "#alistamiento",
    "#despacho",
}

HEARTBEAT_TIMEOUT = 15
LOG_PATH = Path("bitacora.jsonl")


class ChatServer:
    def __init__(
        self,
        host: str = HOST,
        tcp_port: int = TCP_PORT,
        udp_port: int = UDP_PORT,
        log_path: Path = LOG_PATH,
    ) -> None:
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.log_path = log_path

        self.lock = threading.RLock()
        self.clients: dict[str, socket.socket] = {}
        self.client_channels: dict[str, set[str]] = {}
        self.last_seen: dict[str, float] = {}

        self.running = threading.Event()

    def start(self) -> None:
        """Inicia el servidor y sus procesos auxiliares."""
        self.running.set()

        threading.Thread(
            target=self._udp_loop,
            daemon=True
        ).start()

        threading.Thread(
            target=self._availability_loop,
            daemon=True
        ).start()

        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        ) as server:
            server.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            server.bind((self.host, self.tcp_port))
            server.listen()

            print(
                f"Servidor TCP: {self.host}:{self.tcp_port}"
            )
            print(f"Servidor UDP: puerto {self.udp_port}")

            while self.running.is_set():
                try:
                    conn, address = server.accept()
                    print(f"Conexión recibida: {address}")

                    threading.Thread(
                        target=self._client_loop,
                        args=(conn,),
                        daemon=True
                    ).start()

                except OSError:
                    if self.running.is_set():
                        raise

    def _udp_loop(self) -> None:
        """Recibe señales de actividad por UDP."""
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        ) as udp:
            udp.bind((self.host, self.udp_port))
            udp.settimeout(1.0)

            while self.running.is_set():
                try:
                    data, _ = udp.recvfrom(4096)

                    packet = json.loads(
                        data.decode("utf-8")
                    )

                    name = packet.get("name")

                    if (
                        packet.get("type") == "heartbeat"
                        and isinstance(name, str)
                    ):
                        with self.lock:
                            if name in self.clients:
                                self.last_seen[name] = (
                                    time.monotonic()
                                )

                except socket.timeout:  # noqa: UP041
                    continue

                except (
                    ValueError,
                    UnicodeDecodeError,
                    AttributeError,
                ):
                    continue

    def _availability_loop(self) -> None:
        """Publica el estado activo o inactivo de cada usuario."""
        while self.running.is_set():
            time.sleep(2)

            now = time.monotonic()

            with self.lock:
                statuses = {
                    name: (
                        "activo"
                        if now - self.last_seen.get(name, 0)
                        <= HEARTBEAT_TIMEOUT
                        else "inactivo"
                    )
                    for name in self.clients
                }

            self._broadcast({
                "type": "presence",
                "users": statuses,
            })

    def _append_log(
        self,
        record: dict[str, Any]
    ) -> None:
        """Guarda un evento en formato JSONL."""
        with self.log_path.open(
            "a",
            encoding="utf-8"
        ) as file:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )
            file.flush()

    def _send_safe(
        self,
        conn: socket.socket,
        data: dict[str, Any]
    ) -> bool:
        """Evita que un error de envío detenga el servidor."""
        try:
            send_frame(conn, data)
            return True

        except (OSError, ValueError):
            return False

    def _broadcast(
        self,
        data: dict[str, Any],
        recipients: list[str] | None = None,
    ) -> None:
        """Envía datos a todos los conectados o a una lista."""
        with self.lock:
            targets = (
                recipients
                if recipients is not None
                else list(self.clients)
            )

            connections = [
                self.clients[name]
                for name in targets
                if name in self.clients
            ]

        for conn in connections:
            self._send_safe(conn, data)

    def _client_loop(
        self,
        conn: socket.socket
    ) -> None:
        """Gestiona una conexión individual."""
        name: str | None = None

        try:
            first = recv_frame(conn)
            requested = first.get("name")

            if (
                first.get("type") != "login"
                or not isinstance(requested, str)
            ):
                send_frame(conn, {
                    "type": "error",
                    "message": "Inicio de sesión inválido",
                })
                return

            requested = requested.strip()

            if (
                not requested
                or len(requested) > 40
                or any(ord(char) < 32 for char in requested)
            ):
                send_frame(conn, {
                    "type": "error",
                    "message": "Nombre inválido",
                })
                return

            with self.lock:
                if requested in self.clients:
                    send_frame(conn, {
                        "type": "error",
                        "message": "Ese nombre ya está conectado",
                    })
                    return

                name = requested
                self.clients[name] = conn
                self.client_channels[name] = {"#general"}
                self.last_seen[name] = time.monotonic()

            # Imprime el nombre del usuario en cuanto se conecta con éxito
            print(f"Usuario conectado: {name}")

            send_frame(conn, {
                "type": "login_ok",
                "name": name,
                "channels": sorted(CHANNELS),
            })

            self._broadcast({
                "type": "system",
                "message": f"{name} se conectó",
            })

            while True:
                request = recv_frame(conn)
                self._handle_request(name, request)

        except (
            ConnectionError,
            OSError,
            ValueError,
            UnicodeDecodeError,
        ):
            pass

        finally:
            if name is not None:
                with self.lock:
                    if self.clients.get(name) is conn:
                        del self.clients[name]
                        self.client_channels.pop(name, None)
                        self.last_seen.pop(name, None)

                self._broadcast({
                    "type": "system",
                    "message": f"{name} se desconectó",
                })

            try:
                conn.close()
            except OSError:
                pass

    def _handle_request(
        self,
        sender: str,
        req: dict[str, Any]
    ) -> None:
        """Procesa mensajes, canales y consultas de usuarios."""
        kind = req.get("type")

        with self.lock:
            self.last_seen[sender] = time.monotonic()

        if kind == "message":
            self._handle_message(sender, req)

        elif kind in ("join", "leave"):
            channel = req.get("channel")

            if (
                not isinstance(channel, str)
                or channel not in CHANNELS
                or channel == "#general"
            ):
                self._send_to_name(sender, {
                    "type": "error",
                    "message": "Canal inválido",
                })
                return

            with self.lock:
                joined = self.client_channels.get(sender)

                if joined is None:
                    return

                if kind == "join":
                    joined.add(channel)
                else:
                    joined.discard(channel)

                current_channels = sorted(joined)

            self._send_to_name(sender, {
                "type": "channels",
                "channels": current_channels,
            })

        elif kind == "who":
            now = time.monotonic()

            with self.lock:
                users = {
                    user: {
                        "status": (
                            "activo"
                            if now - self.last_seen.get(user, 0)
                            <= HEARTBEAT_TIMEOUT
                            else "inactivo"
                        ),
                        "channels": sorted(
                            self.client_channels.get(user, set())
                        ),
                    }
                    for user in self.clients
                }

            self._send_to_name(sender, {
                "type": "users",
                "users": users,
            })

        else:
            self._send_to_name(sender, {
                "type": "error",
                "message": "Solicitud desconocida",
            })

    def _handle_message(
        self,
        sender: str,
        req: dict[str, Any]
    ) -> None:
        """Valida, registra y distribuye mensajes."""
        text = req.get("text")
        target = req.get("to")
        channel = req.get("channel", "#general")

        if (
            not isinstance(text, str)
            or not text.strip()
            or len(text) > 4000
        ):
            self._send_to_name(sender, {
                "type": "error",
                "message": "Mensaje vacío o demasiado largo",
            })
            return

        # La hora y la autoría las establece el servidor.
        timestamp = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

        if target is not None:
            if (
                not isinstance(target, str)
                or target == sender
            ):
                self._send_to_name(sender, {
                    "type": "error",
                    "message": "Destinatario inválido",
                })
                return

            with self.lock:
                exists = target in self.clients

            if not exists:
                self._send_to_name(sender, {
                    "type": "error",
                    "message": "Destinatario no conectado",
                })
                return

            record = {
                "type": "message",
                "timestamp": timestamp,
                "sender": sender,
                "destination": target,
                "text": text.strip(),
                "private": True,
            }

            self._append_log(record)
            self._send_to_name(target, record)
            self._send_to_name(sender, {
                "type": "sent",
                "message": "Mensaje privado enviado",
            })
            return

        if not isinstance(channel, str) or channel not in CHANNELS:
            self._send_to_name(sender, {
                "type": "error",
                "message": "Canal inexistente",
            })
            return

        with self.lock:
            if sender not in self.client_channels:
                return

            if channel not in self.client_channels[sender]:
                members: list[str] = []
            else:
                members = [
                    user
                    for user, joined in self.client_channels.items()
                    if channel in joined
                ]

        if not members:
            self._send_to_name(sender, {
                "type": "error",
                "message": "No perteneces a ese canal",
            })
            return

        record = {
            "type": "message",
            "timestamp": timestamp,
            "sender": sender,
            "channel": channel,
            "text": text.strip(),
            "private": False,
        }

        self._append_log(record)
        self._broadcast(record, members)

    def _send_to_name(
        self,
        name: str,
        data: dict[str, Any]
    ) -> None:
        with self.lock:
            conn = self.clients.get(name)

        if conn is not None:
            self._send_safe(conn, data)


def main() -> None:
    server = ChatServer()
    server.start()


if __name__ == "__main__":
    main()