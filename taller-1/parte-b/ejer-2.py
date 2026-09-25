
# B2. ¿Qué pasa si se cambia el hilo a daemon?
# Si se cambia el hilo a daemon, el programa terminará antes de que el hilo haya terminado su ejecución. Esto se debe a que los hilos daemon se ejecutan en segundo plano y no bloquean la finalización del programa principal. Por lo tanto, si el hilo daemon no ha terminado su tarea antes de que el programa principal finalice, el hilo daemon será terminado abruptamente.

import threading
import time


def guardar():
    try:
        time.sleep(2)
        print("guardado")
    finally:
        print("archivo cerrado")


threading.Thread(target=guardar, daemon=True).start()
time.sleep(0.5)
print("fin")

