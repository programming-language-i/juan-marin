# C1. Descarga por herencia
#Cada fragmento falla o no hace lo que su autor cree. Para cada uno:
#**(1)** qué pasa al ejecutarlo
#**(2)** por qué
#**(3)** la corrección mínima.

#R/ Se agrega super().__init__() dentro de __init__, porque al heredar de threading.Thread es obligatorio inicializar la clase padre antes de usar .start().



import threading


class Descarga(threading.Thread):
    def __init__(self, archivo):
        super().__init__()
        self.archivo = archivo

    def run(self):
        print("descargando", self.archivo)



Descarga("a.zip").start()
