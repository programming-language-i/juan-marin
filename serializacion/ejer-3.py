
import json

mensaje = {

    "emisor": "Juan",
    "emisor": "Juan",
    "emisor": "Juan",
    "emisor": "Juan",
    "contenido": "Hola, ¿cómo estás?",
    "etiquetas": ("a", "b"),
}



texto = json.dumps(mensaje, ensure_ascii=False)

copiado = json.loads(texto)

print(texto)
print(copiado)

print(f"son iguales: {mensaje == copiado}")