

# B1. ¿Cuánto tarda? 
# El programa tarda 3 segundos en ejecutarse. Esto se debe a que cada hilo se inicia y luego se espera a que termine antes de iniciar el siguiente hilo. Por lo tanto, los hilos se ejecutan de manera secuencial. 



import threading
import time


def tarea(n):
    time.sleep(1)


inicio = time.perf_counter()
for i in range(3):
    hilo = threading.Thread(target=tarea, args=(i,))
    hilo.start()
    hilo.join()
print(f"{time.perf_counter() - inicio:.1f} s")
