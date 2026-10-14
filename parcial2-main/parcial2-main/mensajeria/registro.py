import socket
import threading


class RegistroClientes:
    def __init__(self) -> None:
        self.clientes: dict[str, socket.socket] = {}
        self.lock = threading.Lock()

# Un diccionario donde la llave es el nombre del usuario y el valor es su conexión, usando un lock para evitar errores al momento de acceder a él.


    def insertar(self, nombre: str, conexion: socket.socket) -> bool:
        with self.lock:
            if nombre in self.clientes:
                return False
            self.clientes[nombre] = conexion
            return True

# Este metodo sirve para insertar un nuevo cliente en el registro. Si el nombre ya existe, devuelve False, de lo contrario, agrega la conexión al diccionario y devuelve True.

    def buscar(self, nombre: str) -> socket.socket | None:
        with self.lock:
            return self.clientes.get(nombre)

# Este metodo sirve para buscar un cliente en el registro por su nombre. Devuelve la conexión si se encuentra, o None si no existe.

    def borrar(self, nombre: str) -> None:
        with self.lock:
            self.clientes.pop(nombre, None)

# Este metodo sirve para borrar un cliente del registro por su nombre. Si el nombre no existe, no hace nada.

    def destinatarios(self, excepto: str) -> list[tuple[str, socket.socket]]:
        with self.lock:
            return [
                (nombre, conexion)
                for nombre, conexion in self.clientes.items()
                if nombre != excepto
            ]


#El metodo destinatario devuelve el mensaje a todos los clientes registrados, excepto al que lo envió. Devuelve una lista de tuplas con el nombre y la conexión de cada destinatario.