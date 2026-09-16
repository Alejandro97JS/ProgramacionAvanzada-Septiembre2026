import requests, time
from datetime import datetime, timedelta

# De forma imperativa:
response = requests.get("https://www.google.com")
print(response.status_code)
print(response.text)


# De forma modular, con funciones:
def get_google_info():
    response = requests.get("https://www.google.com")
    return response.text

def get_google_info_first_n_chars(n:int):
    response = requests.get("https://www.google.com")
    return response.text[:n]


class GoogleInfoManager:

    def __init__(self):
        self.url = "https://www.google.com"
        self.last_request_datetime = None
        self.response = None

    def __request_get_info(self):
        if (self.last_request_datetime is None or 
            (self.last_request_datetime + timedelta(days=1)) < datetime.now()):
            print("Tengo que hacer la llamada")
            self.response = requests.get(self.url, headers={})
            self.last_request_datetime = datetime.now()
        else:
            print("Actuó la caché de la respuesta")
        if self.response.status_code == 200:
            print("Tengo bien los datos")
            return self.response
        else:
            print("Datos con error")
            return None

    def get_google_info(self):
        return self.__request_get_info().text

    def get_google_info_first_n_chars(self, n:int):
        return self.__request_get_info().text[:n]


gim = GoogleInfoManager()
gim.get_google_info()
print("HOLA"*5)
time.sleep(5)
gim.get_google_info_first_n_chars(10)
