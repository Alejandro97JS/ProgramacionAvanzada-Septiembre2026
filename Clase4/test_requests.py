import requests

url = "http://127.0.0.1:8000/users/"

user_data = {
    "username": "juan",
    "email": "email_example3@example.com",
    "age": 20
}

response = requests.post(url, json=user_data)
print(f"Código de respuesta: {response.status_code}")
print(f"Respuesta: {response.json()}")
