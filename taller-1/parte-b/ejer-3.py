

# B3. ¿Qué pasa si se ejecuta el programa con ThreadPoolExecutor?

# Si se ejecuta el programa con ThreadPoolExecutor, el programa lanzará una excepción ZeroDivisionError. Esto se debe a que el hilo que ejecuta la función dividir intenta dividir 1 entre 0, lo cual no es posible. La excepción se propagará al hilo principal y el programa terminará abruptamente.




from concurrent.futures import ThreadPoolExecutor


def dividir(a, b):
    return a / b


with ThreadPoolExecutor() as pool:
    futuro = pool.submit(dividir, 1, 0)
print("listo")