# Acceso a claves
# my_dictionary = {
#     "a": 1,
#     "b": 2
# }
# print(my_dictionary.get("c"))
# print("c" in my_dictionary)

# if "c" in my_dictionary:
#     print("Está!")
# else:
#     print("No está!!")

# print(
#     "Está!" if "c" in my_dictionary
#     else "No está!!"
# )

my_list = []
for i in range(5):
    my_list.append(2*i)
print(my_list)

my_list = [2*x for x in range(0,5)]
print(my_list)