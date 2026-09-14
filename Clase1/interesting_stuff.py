# Acceso a claves de diccionarios
my_dictionary = {
    "a": 1,
    "b": 2
}
print(my_dictionary.get("c"))
# print(my_dictionary["c"]) # Exception!!
print("c" in my_dictionary)

# OK, but NO Pythonic
if "c" in my_dictionary:
    print("Está!")
else:
    print("No está!!")

# More Pythonic:
print(
    "Está!" if "c" in my_dictionary
    else "No está!!"
)

# Ok, but no Pythonic:
my_list = []
for i in range(5):
    my_list.append(2*i)
print(my_list)

# More Pythonic:
my_list = [2*x for x in range(5)]
print(my_list)


# Cuidado con los type hints (tipado): es solo
# informativo. Python trabaja con la variable que le
# hayas pasado aunque no cumpla el tipo que dijiste.
def suma_uno(valor:int):
    print(type(valor))
    print(valor)
    return valor + 1

print(suma_uno(5))
print(suma_uno("Pepe"))
print(suma_uno("5"))

# En programación web, al obtener los datos de la DB, ¿cómo
# les doy el formato que quiero, Json (diccionario) por ejemplo?
# --> Lo veremos, con FastAPI. El proceso es serialización /
# deserialización.

# En Python, cómo es la documentación? -->
# docstrings, con triples comillas. Dentro de ello,
# hay estándares para documentar parámetros, tipos devueltos...

# __repr__, __str__, __eq__
# Métodos dunder, D (double) UNDERscore, "internos" de Python.