import json
import socket
import sys
import threading

from protocolo import enviar_mensaje, recibir_mensaje

HOST = "127.0.0.1"
PUERTO = 8000


def mostrar(texto: str) -> str:
    """Convierte una respuesta JSON en texto para mostrar."""

    try:
        datos = json.loads(texto)

        if not isinstance(datos, dict):
            return f"[sin formato] {texto}"

        tipo = datos.get("tipo")

        if tipo == "mensaje":
            return (
                f"[#{datos.get('canal', 'general')}] "
                f"{datos.get('emisor', 'desconocido')}: "
                f"{datos.get('contenido', '')}"
            )

        if tipo == "privado":
            return (
                f"[privado] {datos.get('emisor', 'desconocido')}: "
                f"{datos.get('contenido', '')}"
            )

        if tipo == "error":
            return f"[error] {datos.get('detalle', 'Error desconocido')}"

    except (json.JSONDecodeError, TypeError):
        pass

    return f"[sin formato] {texto}"


def recibir_mensajes(conexion: socket.socket) -> None:
    """Escucha los mensajes recibidos del servidor."""

    while True:
        try:
            texto = recibir_mensaje(conexion)
        except (OSError, ValueError, UnicodeError):
            texto = None

        if texto is None:
            print("\nServidor desconectado.")
            break

        print(f"\n{mostrar(texto)}")
        print("> ", end="", flush=True)


def a_pedido(texto: str) -> dict[str, str] | None:
    """Convierte lo escrito en la consola en una solicitud JSON."""

    if texto.startswith("/privado"):
        partes = texto.split(maxsplit=2)

        if len(partes) < 3:
            print("Uso: /privado <destino> <texto>")
            return None

        return {
            "tipo": "privado",
            "destino": partes[1],
            "contenido": partes[2],
        }

    return {
        "tipo": "mensaje",
        "contenido": texto,
    }


def main() -> None:
    """Conecta el cliente con el servidor."""

    if len(sys.argv) < 2:
        print("Uso: python -m mensajeria.cliente_json <nombre> [puerto]")
        return

    nombre = sys.argv[1].strip()

    if not nombre or len(nombre) > 30:
        print("El nombre debe tener entre 1 y 30 caracteres.")
        return

    try:
        puerto = int(sys.argv[2]) if len(sys.argv) > 2 else PUERTO
    except ValueError:
        print("El puerto debe ser un número entero.")
        return

    if not 1 <= puerto <= 65535:
        print("El puerto debe estar entre 1 y 65535.")
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.connect((HOST, puerto))

            # El saludo inicial continúa siendo texto plano.
            enviar_mensaje(cliente, nombre)
            respuesta = recibir_mensaje(cliente)

            if respuesta != "OK":
                print(f"El servidor respondió: {respuesta}")
                return

            print(
                f"Conectado como {nombre}.\n"
                "Escribe un mensaje para el grupo.\n"
                "Para enviar un mensaje privado: "
                "/privado <destino> <texto>\n"
                "Escribe 0 para salir."
            )

            hilo = threading.Thread(
                target=recibir_mensajes,
                args=(cliente,),
                daemon=True,
            )
            hilo.start()

            while hilo.is_alive():
                try:
                    texto = input("> ")
                except (EOFError, KeyboardInterrupt):
                    break

                if texto.strip() == "0":
                    break

                if not texto.strip():
                    continue

                pedido = a_pedido(texto)

                if pedido is None:
                    continue

                try:
                    mensaje_json = json.dumps(
                        pedido,
                        ensure_ascii=False,
                    )
                    enviar_mensaje(cliente, mensaje_json)

                except (OSError, ValueError, TypeError) as error:
                    print(f"No se pudo enviar el mensaje: {error}")
                    break

    except ConnectionRefusedError:
        print("No se pudo conectar. Comprueba que el servidor esté activo.")
    except (OSError, ValueError) as error:
        print(f"Error en el cliente: {error}")


if __name__ == "_main_":
    main()