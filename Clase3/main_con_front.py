import logging
from html import escape
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator

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
        if instance.age >= 50:
            if len(instance.username) < 20:
                raise ValueError("You must provide a username longer than 20 chars")
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

LANDING_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mi primera API con FastAPI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #f5f7fa;
            padding: 24px;
        }
        .card {
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 18px;
            padding: 48px 40px;
            max-width: 560px;
            width: 100%;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 45px rgba(0, 0, 0, 0.35);
        }
        .badge {
            display: inline-block;
            font-size: 13px;
            letter-spacing: 1px;
            text-transform: uppercase;
            background: #24d18d;
            color: #06281c;
            padding: 6px 14px;
            border-radius: 999px;
            font-weight: 600;
        }
        h1 { margin: 20px 0 12px; font-size: 34px; line-height: 1.2; }
        p { color: #cbd5e1; line-height: 1.6; }
        .links { margin-top: 32px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
        a {
            text-decoration: none;
            padding: 12px 22px;
            border-radius: 10px;
            font-weight: 600;
            transition: transform .15s ease, opacity .15s ease;
        }
        a:hover { transform: translateY(-2px); opacity: .9; }
        .primary { background: #24d18d; color: #06281c; }
        .ghost { border: 1px solid rgba(255,255,255,.3); color: #f5f7fa; }
        footer { margin-top: 28px; font-size: 13px; color: #94a3b8; }
    </style>
</head>
<body>
    <main class="card">
        <span class="badge">Servidor activo</span>
        <h1>Mi primera API con FastAPI</h1>
        <p>El servidor está levantado correctamente. Desde aquí puedes explorar
           la documentación interactiva o probar los endpoints de saludo.</p>
        <div class="links">
            <a class="primary" href="/docs">Ver documentación</a>
            <a class="ghost" href="/hello">Probar /hello</a>
        </div>
        <footer>Programación Avanzada · Clase 3</footer>
    </main>
</body>
</html>
"""

NOT_FOUND_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>404 · Ruta perdida en la galaxia</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: "Trebuchet MS", system-ui, sans-serif;
            min-height: 100vh;
            overflow: hidden;
            background: #000;
            color: #ffe81f;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 24px;
        }
        /* Campo de estrellas generado con sombras */
        .stars, .stars2 {
            position: fixed; inset: 0; pointer-events: none;
            background: transparent;
        }
        .stars::after, .stars2::after {
            content: ""; position: absolute; width: 2px; height: 2px; border-radius: 50%;
            background: #fff;
        }
        .stars::after {
            box-shadow: 12vw 8vh #fff, 25vw 40vh #fff, 40vw 15vh #fff, 55vw 70vh #fff,
                        70vw 25vh #fff, 85vw 55vh #fff, 92vw 10vh #fff, 5vw 85vh #fff,
                        33vw 90vh #fff, 60vw 45vh #fff, 78vw 88vh #fff, 18vw 60vh #fff,
                        48vw 5vh #fff, 88vw 35vh #fff, 8vw 30vh #fff, 66vw 95vh #fff;
            animation: twinkle 3s ease-in-out infinite alternate;
        }
        .stars2::after {
            width: 1px; height: 1px;
            box-shadow: 3vw 12vh #aaa, 22vw 22vh #aaa, 37vw 55vh #aaa, 51vw 30vh #aaa,
                        63vw 12vh #aaa, 74vw 62vh #aaa, 95vw 78vh #aaa, 15vw 45vh #aaa,
                        29vw 75vh #aaa, 44vw 82vh #aaa, 81vw 5vh #aaa, 58vw 58vh #aaa;
            animation: twinkle 2s ease-in-out infinite alternate-reverse;
        }
        @keyframes twinkle { from { opacity: .3; } to { opacity: 1; } }

        .intro { color: #4bd5ee; font-size: 18px; margin-bottom: 18px; opacity: .9; }
        h1 {
            font-size: clamp(90px, 22vw, 180px);
            line-height: 1;
            letter-spacing: 8px;
            text-shadow: 0 0 25px rgba(255, 232, 31, .6);
        }
        h2 { font-size: clamp(20px, 4vw, 30px); margin: 12px 0 8px; letter-spacing: 3px; text-transform: uppercase; }
        p { color: #d6d6d6; max-width: 520px; line-height: 1.6; margin: 0 auto; }
        code { color: #ffe81f; background: rgba(255,232,31,.1); padding: 2px 6px; border-radius: 4px; }

        /* Sable de luz */
        .saber { display: flex; align-items: center; justify-content: center; margin: 28px 0; }
        .hilt {
            width: 60px; height: 14px; border-radius: 3px;
            background: linear-gradient(90deg, #555, #ccc 30%, #333 50%, #aaa 70%, #444);
        }
        .blade {
            height: 8px; width: 0; border-radius: 0 6px 6px 0;
            background: #fff;
            box-shadow: 0 0 8px #ff2b2b, 0 0 18px #ff2b2b, 0 0 36px #ff0000;
            animation: ignite 1.2s .4s ease-out forwards, hum 0.12s 1.6s infinite alternate;
        }
        @keyframes ignite { to { width: min(260px, 55vw); } }
        @keyframes hum { to { box-shadow: 0 0 10px #ff2b2b, 0 0 22px #ff2b2b, 0 0 42px #ff0000; } }

        a {
            display: inline-block; margin-top: 30px;
            padding: 12px 26px; border: 2px solid #ffe81f; border-radius: 999px;
            color: #ffe81f; text-decoration: none; font-weight: 700; letter-spacing: 1px;
            transition: background .2s, color .2s;
        }
        a:hover { background: #ffe81f; color: #000; }
        footer { margin-top: 26px; font-size: 13px; color: #777; }
    </style>
</head>
<body>
    <div class="stars"></div>
    <div class="stars2"></div>
    <div class="intro">Hace mucho tiempo, en una API muy, muy lejana...</div>
    <h1>404</h1>
    <h2>Esta no es la ruta que buscas</h2>
    <div class="saber"><div class="hilt"></div><div class="blade"></div></div>
    <p>La ruta <code>{path}</code> se ha perdido en el hiperespacio.
       Puede que el Lado Oscuro la haya borrado de los archivos del Templo Jedi.</p>
    <a href="/">Volver a la base rebelde</a>
    <footer>Que la Fuerza te acompañe · Programación Avanzada · Clase 3</footer>
</body>
</html>
"""

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        logger.warning(f"404 - Ruta no encontrada: {request.url.path}")
        # Escapamos la ruta para evitar inyección de HTML (XSS)
        html = NOT_FOUND_HTML.replace("{path}", escape(request.url.path))
        return HTMLResponse(content=html, status_code=404)
    # Para el resto de errores HTTP, usamos el comportamiento por defecto de FastAPI
    return await http_exception_handler(request, exc)

@app.get("/", response_class=HTMLResponse)
def root_endpoint():
    logger.info("Alguien ha entrado a la página raíz")
    return LANDING_HTML

@app.get("/hello")
def initial_greeting():
    logger.info("Recibida petición al saludo genérico")
    return {"msg": "Hola mundo!!!"}

@app.get("/hello/{name}")
def custom_greeting(name:str):
    logger.info(f"Recibida petición al saludo personalizado para {name}")
    processed_name = name.capitalize()
    logger.info(f"Nombre tras .capitalize(): {processed_name}")
    if processed_name == "Pepe":
        logger.warning("Pepe ha entrado a la web!!")
    return {"msg": f"Hello, {processed_name}!!!"}

@app.post("/users/")
def create_user(user: User):
    logger.info(f"📥 Registro de usuario recibido: {user}")
    ... # Registrarlo en DB...
    return {
        "msg": "Usuario registrado correctamente",
        "usuario": user.username
    }
