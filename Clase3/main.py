import logging
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from pydantic import field_validator, model_validator

class User(BaseModel):
    username: str = Field(..., min_length=3, description="Nombre de usuario (mínimo 3 caracteres)")
    email: str = Field(..., description="Email del usuario")
    age: Optional[int] = Field(None, ge=0, description="Edad no negativa (opcional)")

    @field_validator("username")
    def username_with_vowels(cls, value):
        if not any(vowel in value for vowel in 
                   ["a", "e", "i", "o", "u"]):
            raise ValueError("You need vowels in your username!")
        return value

    @model_validator(mode="after")
    def long_username_if_age_ge_50(cls, instance):
        if instance.age is None or instance.age >= 50:
            if instance.age is None:
                hint = "No has indicado la edad."
            else:
                hint = "Eres mayor de 50."
            if len(instance.username) < 20:
                raise ValueError(f"{hint} Por tanto, debes indicar un username de más de 20 chars")
        return instance

logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mi primera API con FastAPI",
    description="Una API de ejemplo.",
    version="1.0.0"
)

@app.get("/")
def root_endpoint():
    logger.info("Alguien ha entrado a la página raíz")
    return {"msg": "El servidor está levantado bien!"}

@app.get("/hello")
def initial_greeting():
    logger.info("Recibida petición al saludo genérico")
    return {"msg": "Hola mundo!!!"}

class NameProcessor:

    def __init__(self, name):
        self.name = name

    def get_name_upper(self):
        return self.name.upper()

    def get_reversed_name(self):
        return self.name[::-1] # juan --> nauj

@app.get("/hello/{name}")
def custom_greeting(name:str):
    logger.info(f"Recibida petición al saludo personalizado para {name}")
    processed_name = NameProcessor(name).get_name_upper()
    logger.info(f"Nombre tras procesamiento: {processed_name}")
    if processed_name == name:
        logger.warning("Alguien que ya tenía el nombre entero en mayús ha entrado a la web!!")
    return {"msg": f"Hello, {processed_name}!!!"}

@app.post("/users/")
def create_user(user: User):
    logger.info(f"📥 Registro de usuario recibido: {user}")
    ... # Registrarlo en DB...
    return {
        "msg": "Usuario registrado correctamente",
        "usuario": user
    }
