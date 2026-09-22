"""Prueba la API una vez aplicadas TODAS las migraciones (`alembic upgrade head`).

    uvicorn main:app --reload      # en una terminal
    python test_requests.py        # en otra
"""

import uuid

import requests

BASE_URL = "http://127.0.0.1:8000"


def mostrar(titulo, response):
    print()
    print("=" * 70)
    print(titulo)
    print("=" * 70)
    print(f"Petición: {response.request.method} {response.url}")
    print(f"Código de respuesta: {response.status_code}")
    print(f"Respuesta: {response.json()}")


# --- 1) Los usuarios de "producción" han sobrevivido a las migraciones ---
# Fíjate en que tienen birth_date (calculada desde su antigua edad), is_active y created_at
respuesta = requests.get(f"{BASE_URL}/users/")
mostrar("1) GET /users/  ->  usuarios antiguos, ya migrados", respuesta)

# --- 2) Crear un usuario nuevo con fecha de nacimiento ---
sufijo = uuid.uuid4().hex[:6]
nuevo = {"username": "carmen", "email": f"carmen_{sufijo}@example.com", "birth_date": "1999-05-17"}
respuesta = requests.post(f"{BASE_URL}/users/", json=nuevo)
mostrar("2) POST /users/  ->  la edad ya no se envía, se calcula", respuesta)
user_id = respuesta.json()["id"]

# --- 3) Desactivarlo (soft delete gracias a la columna is_active) ---
respuesta = requests.delete(f"{BASE_URL}/users/{user_id}")
mostrar("3) DELETE /users/{id}  ->  is_active pasa a false, la fila NO se borra", respuesta)

# --- 4) Ya no sale en el listado normal... ---
respuesta = requests.get(f"{BASE_URL}/users/")
print(f"\n4) Usuarios activos: {[u['username'] for u in respuesta.json()]}")

# --- 5) ...pero sigue en la base de datos ---
respuesta = requests.get(f"{BASE_URL}/users/", params={"incluir_inactivos": True})
print(f"5) Todos (incluidos inactivos): {[u['username'] for u in respuesta.json()]}")
