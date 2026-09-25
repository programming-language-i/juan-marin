
# C2. Tres tareas "concurrentes"

#Cada fragmento falla o no hace lo que su autor cree. Para cada uno:
#**(1)** qué pasa al ejecutarlo
#**(2)** por qué
#**(3)** la corrección mínima.

# R/ se hace el cambio de start() a run(), porque al heredar de threading.Thread es obligatorio usar el método run() para definir la tarea que se ejecutará en el hilo. El método start() se encarga de iniciar el hilo y llamar al método run() en un nuevo hilo de ejecución.






import threading
import time


class Tarea(threading.Thread):
    def run(self):
        time.sleep(1)
        print(self.name, "lista")


inicio = time.perf_counter()
tareas = [Tarea(name=f"t{i}") for i in range(3)]
for t in tareas:
    t.start()
print(f"{time.perf_counter() - inicio:.1f} s")
for t in tareas:
    t.join()