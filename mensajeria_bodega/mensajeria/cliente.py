import argparse
import json
import socket
import threading
import time

from protocolo import recv_frame, send_frame

_ultimo_estado_presencia = None


def receiver(sock: socket.socket) -> None:
    """Escucha mensajes del servidor en un hilo independiente."""
    global _ultimo_estado_presencia
    while True:
        try:
            data = recv_frame(sock)
            kind = data.get("type")

            if kind == "message":
                if data.get("private"):
                    destination = "[mensaje privado]"
                else:
                    destination = data.get("channel", "#general")

                print(
                    f"\n[{data.get('timestamp')}] "
                    f"{data.get('sender')} "
                    f"{destination}: {data.get('text')}"
                )

            elif kind == "presence":
                users = data.get("users", {})
                active_users = sorted([name for name, status in users.items() if status == "activo"])
                estado_actual = f"[Usuarios activos: {', '.join(active_users)}]"

                if estado_actual != _ultimo_estado_presencia:
                    _ultimo_estado_presencia = estado_actual
                    print(f"\n{estado_actual}")

            else:
                print(f"\n{data}")

        except (
            OSError,
            ConnectionError,
            ValueError,
            json.JSONDecodeError,
        ):
            print("\nConexión cerrada.")
            break


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cliente de mensajería de bodega"
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Dirección IP del servidor",
    )

    args = parser.parse_args()
    name = input("Nombre de usuario: ").strip()

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        sock.connect((args.host, 8000))

        send_frame(sock, {
            "type": "login",
            "name": name,
        })

        response = recv_frame(sock)
        print(response)

        if response.get("type") != "login_ok":
            sock.close()
            return

        threading.Thread(
            target=receiver,
            args=(sock,),
            daemon=True,
        ).start()

        def heartbeat() -> None:
            """Envía una señal UDP cada cinco segundos."""
            udp = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )

            packet = json.dumps({
                "type": "heartbeat",
                "name": name,
            }).encode("utf-8")

            try:
                while True:
                    udp.sendto(
                        packet,
                        (args.host, 8001)
                    )
                    time.sleep(5)

            except OSError:
                pass

            finally:
                udp.close()

        threading.Thread(
            target=heartbeat,
            daemon=True,
        ).start()

        print("\nSistema de mensajería conectado.")
        print("Comandos disponibles:")
        print("  /join #recepcion")
        print("  /join #alistamiento")
        print("  /join #despacho")
        print("  /leave #recepcion")
        print("  /msg NOMBRE texto")
        print("  /who")
        print("  /quit")
        print("Escribe cualquier otro texto para #general.\n")

        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if line == "/quit":
                break

            elif line == "/who":
                send_frame(sock, {"type": "who"})

            elif line.startswith("/join "):
                channel = line.split(maxsplit=1)[1]

                send_frame(sock, {
                    "type": "join",
                    "channel": channel,
                })

            elif line.startswith("/leave "):
                channel = line.split(maxsplit=1)[1]

                send_frame(sock, {
                    "type": "leave",
                    "channel": channel,
                })

            elif line.startswith("/msg "):
                parts = line.split(maxsplit=2)

                if len(parts) == 3:
                    send_frame(sock, {
                        "type": "message",
                        "to": parts[1],
                        "text": parts[2],
                    })
                else:
                    print("Uso: /msg NOMBRE texto")

            elif line:
                send_frame(sock, {
                    "type": "message",
                    "channel": "#general",
                    "text": line,
                })

    except (OSError, ValueError) as error:
        print(f"Error de conexión: {error}")

    finally:
        sock.close()
        print("Cliente desconectado.")


if __name__ == "__main__":
    main()