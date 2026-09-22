import uuid

import requests

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "clase4-secret"  # la misma que comprueba el middleware de main.py


def mostrar(titulo, response):
    print()
    print("=" * 70)
    print(titulo)
    print("=" * 70)
    print(f"Petición: {response.request.method} {response.url}")
    print(f"Código de respuesta: {response.status_code}")
    # Estas dos cabeceras las añade nuestro middleware a TODAS las respuestas
    print(f"X-Request-ID:   {response.headers.get('X-Request-ID')}")
    print(f"X-Process-Time: {response.headers.get('X-Process-Time')} s")
    try:
        print(f"Respuesta: {response.json()}")
    except ValueError:
        print(f"Respuesta (no es JSON): {response.text[:120]}...")


# --- 1) POST con BODY: crear un usuario ---
sufijo = uuid.uuid4().hex[:6]  # email distinto en cada ejecución (es único en la DB)
user_data = {
    "username": "juan",
    "email": f"juan_{sufijo}@example.com",
    "age": 20
}

respuesta_creacion = requests.post(f"{BASE_URL}/users/", json=user_data)
mostrar("1) POST /users/  ->  sólo BODY", respuesta_creacion)

if not respuesta_creacion.ok:
    print("No se ha podido crear el usuario, se cancela el resto de pruebas.")
    raise SystemExit(1)

user_id = respuesta_creacion.json()["usuario"]["id"]

# --- 2) PATCH con PATH PARAM + QUERY PARAMS + BODY (simulación) ---
# El path param va en la URL, los query params en params= y el body en json=
params = {
    "motivo": "el usuario ha cambiado de correo",
    "notificar": False,
    "dry-run": True,  # ojo: el alias del query param lleva guión
}
cambios = {"email": f"juan_nuevo_{sufijo}@example.com", "age": 21}

respuesta = requests.patch(f"{BASE_URL}/users/{user_id}", params=params, json=cambios)
mostrar("2) PATCH /users/{id}  ->  PATH PARAM + QUERY PARAMS + BODY (dry-run)", respuesta)

# --- 3) El mismo PATCH pero guardando de verdad y avisando por email ---
params = {
    "motivo": "cambio confirmado por el usuario",
    "notificar": True,   # lanza la tarea en segundo plano del servidor
    "dry-run": False,
}

respuesta = requests.patch(f"{BASE_URL}/users/{user_id}", params=params, json=cambios)
mostrar("3) PATCH /users/{id}  ->  mismos datos, esta vez se guarda", respuesta)

# --- 4) GET que trabaja con las CABECERAS de la petición ---
headers = {
    "X-Client-Version": "1.2.3",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "X-Request-ID": "peticion-de-clase-123",  # el middleware lo reutiliza y lo devuelve
}

respuesta = requests.get(f"{BASE_URL}/info-headers", headers=headers)
mostrar("4) GET /info-headers  ->  cabeceras enviadas por el cliente", respuesta)

# --- 5) Ruta protegida SIN la cabecera X-API-Key: el middleware corta la petición ---
respuesta = requests.get(f"{BASE_URL}/admin/stats")
mostrar("5) GET /admin/stats  ->  sin X-API-Key (el middleware responde 401)", respuesta)

# --- 6) La misma ruta CON la cabecera correcta: el middleware deja pasar ---
respuesta = requests.get(f"{BASE_URL}/admin/stats", headers={"X-API-Key": API_KEY})
mostrar("6) GET /admin/stats  ->  con X-API-Key correcta", respuesta)
