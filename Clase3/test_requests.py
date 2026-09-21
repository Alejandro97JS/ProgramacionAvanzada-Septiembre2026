import requests

# url = "http://127.0.0.1:8000/"
# response = requests.get(url)
# print(
#     "Ejemplo de una línea muy larga que no he querido dividir para ver si Ruff lo detecta como un error visual y lo deja más bonito en mi código. Corrige pls!!"
# )
# print(f"Código de respuesta: {response.status_code}")
# print(f"Respuesta: {response.text}")


url = "http://127.0.0.1:8000/users/"

user_data = {
    "username": "jnjna"*10,
    "email": "juan@example.com",
    "age": 51
}

response = requests.post(url, json=user_data)
print(f"Código de respuesta: {response.status_code}")
print(f"Respuesta: {response.json()}")
if not response.ok:
    raise Exception("")
