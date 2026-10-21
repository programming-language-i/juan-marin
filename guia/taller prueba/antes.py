eventos = []


def registrar(usuario, accion):
    eventos.append((usuario, accion))
    with open("antes.log", "a", encoding="utf-8") as archivo:
        for usuario_guardado, accion_guardada in eventos:
            archivo.write(f"{usuario_guardado}|{accion_guardada}\n")
    print(f"Registrado: {usuario} {accion}")
    return len(eventos)


print(registrar("ana", "entrar"))
print(registrar("ana", "entrar"))

with open("antes.log", encoding="utf-8") as archivo:
    print("líneas en antes.log:", sum(1 for _ in archivo))


    