# Biblioteca para hacer peticiones HTTP (GET, POST, etc.) a APIs o páginas web.
import requests
from datetime import datetime, timedelta
# GET a la raíz de la API de GitHub. Devuelve un objeto Response con status, headers y cuerpo.
response = requests.get("https://api.github.com")

# Código HTTP: 200 = OK, 404 = no encontrado, 500 = error del servidor, etc.
print(response.status_code)

# Cuerpo de la respuesta como texto (aquí es JSON, pero aún no parseado).
# Para un dict de Python usarías: response.json()
print(response.text)

class GoogleInfoManager:
    def __init__(self):
        self.url = "https://www.google.com/search"
        self.last_request_datetime = None
        self.response = None

    def __request_get_info(self, query: str):
        if (self.last_request_datetime is not None or (self.last_request_datetime + timedelta(days=1) < datetime.now())):
            response = requests.get(self.url, params={"q": query})
            self.response = response
        self.last_request_datetime = datetime.now()

    def get_info(self, query: str) -> dict:
        response = requests.get(self.url, params={"q": query})
        return response.json()

    def get_google_info(self, query: str) -> dict:
        response = self.__request_get_info(query)
        return response.json()

gim = GoogleInfoManager()
print(gim.get_google_info("Python"))
print ("_____"*5)
