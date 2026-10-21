# #imperativo y declaritivo


print ("Programación sobre Imperativa y Declarativa")

numero = [1, 2, 3, 4, 5, 6, 7, 8]


##imperativo

# total = 0

# for n in numero:
#     if n % 2 == 0:
#         total += n * n


# print("El total de los cuadrados de los números pares es:", total)



## declarativo


# total = sum(n * n for n in numero if n % 2 == 0)
# print("El total de los cuadrados de los números pares es:", total)


## ============================== funciones puras y orden superior

# def es_par(n):
#     return n % 2 == 0

# def cuadrado(n):
#     return n * n

# total = sum(cuadrado(n) for n in numero if es_par(n))

# print("El total de los cuadrados de los números pares es:", total)


## uso de filter


# pares = filter(es_par, numero)

# print("Números pares:", list(pares))



## doble lista 


# numero = [1, 2, 3, 4, 5, 6, 7, 8]

# doble = map(lambda x: x * 2, numero)

# dobles_list= list(doble)

# print("Dobles de la lista:", dobles_list)





estudiantes = ["juan", "maria", "pedro", "luis", "ana"]


apellidos_largos = filter (lambda apellido: len(apellido) > 4, estudiantes)

apellidos = len(list(apellidos_largos)) > 5


resultado = "Hay más de 5 apellidos largos" if apellidos else "No hay más de 5 apellidos largos"

print(resultado)    

