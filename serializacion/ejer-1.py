import pickle


mensaje = {

    "emisor": "Juan",
    "emisor": "Juan",
    "emisor": "Juan",
    "emisor": "Juan",
    "contenido": "Hola, ¿cómo estás?",
    "etiquetas": ("a", "b"),
}



datos = pickle.dumps(mensaje)

print(datos)


copiado = pickle.loads(datos)
print(copiado)

