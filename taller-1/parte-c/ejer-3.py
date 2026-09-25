
# C3. Un pool de procesos sin guarda
#Cada fragmento falla o no hace lo que su autor cree. Para cada uno:
#**(1)** qué pasa al ejecutarlo
#**(2)** por qué
#**(3)** la corrección mínima.


from concurrent.futures import ProcessPoolExecutor


def cuadrado(n):
    return n * n


if __name__ == "__main__": 
    with ProcessPoolExecutor(max_workers=2) as pool:
     print(list(pool.map(cuadrado, range(4))))

