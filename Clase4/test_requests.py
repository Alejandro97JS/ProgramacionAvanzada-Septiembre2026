import requests

url = "http://127.0.0.1:8000/users/"

# user_data = {
#     "username": "Pepe",
#     "email": "email2_example11@example.com",
#     "age": 20
# }

# response = requests.post(url, json=user_data)
# print(f"Código de respuesta: {response.status_code}")
# print(f"Respuesta: {response.json()}")

# # --- Crear pedidos ---
# orders_url = "http://127.0.0.1:8000/orders/"
# user_id = 2

# orders_data = [
#     {"user_id": user_id, "product": "Ordenador gamer", "quantity": 1, "price": 549.99}
# ]

# for order_data in orders_data:
#     response = requests.post(orders_url, json=order_data)
#     print(f"Código de respuesta: {response.status_code}")
#     print(f"Respuesta: {response.json()}")

# --- Consultar pedidos de un usuario ---
response = requests.get(f"http://127.0.0.1:8000/users/2/orders")
print(f"Código de respuesta: {response.status_code}")
print(f"Respuesta: {response.json()}")
