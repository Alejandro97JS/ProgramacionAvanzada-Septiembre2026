import logging
import time
import uuid
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator, model_validator

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from fastapi import BackgroundTasks

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- DB setup ---
DATABASE_URL = "sqlite:///./usuarios.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    age = Column(Integer, nullable=True)

Base.metadata.create_all(bind=engine)

# --- Pydantic model ---
class User(BaseModel):
    username: str = Field(..., min_length=3, description="Nombre de usuario (mínimo 3 caracteres)")
    email: str = Field(..., description="Email del usuario")
    age: Optional[int] = Field(None, ge=0, description="Edad no negativa (opcional)")

    @field_validator("username")
    def username_with_values(cls, value):
        if not any(vowel in value for vowel in ["a", "e", "i", "o", "u"]):
            raise ValueError("You need vowels in your username!")
        return value

    @model_validator(mode="after")
    def long_username_if_age_ge_50(cls, instance):
        if instance.age is not None and instance.age >= 50:
            if len(instance.username) < 20:
                raise ValueError("You must provide a username longer than 20 chars")
        return instance

# --- Modelo para actualizar (todos los campos son opcionales) ---
class UserUpdate(BaseModel):
    """Body del PATCH: sólo se envían los campos que se quieren cambiar."""

    username: Optional[str] = Field(None, min_length=3, description="Nuevo nombre de usuario")
    email: Optional[str] = Field(None, description="Nuevo email")
    age: Optional[int] = Field(None, ge=0, description="Nueva edad, no negativa")

# --- FastAPI setup ---
app = FastAPI(
    title="Mi primera API con FastAPI",
    description="Una API de ejemplo con base de datos SQLite.",
    version="1.0.0"
)

# --- Middleware ---
# Un middleware se ejecuta ANTES y DESPUÉS de cada petición, sea cual sea la ruta.
# Aquí hacemos tres tareas típicas de middleware:
#   1. Trazabilidad: leer (o generar) la cabecera X-Request-ID y devolverla.
#   2. Medir cuánto tarda la petición y publicarlo en la cabecera X-Process-Time.
#   3. Autenticación sencilla: bloquear /admin/* si no llega la cabecera X-API-Key.
API_KEY = "clase4-secret"
RUTAS_PROTEGIDAS = ("/admin",)

@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    # Si el cliente manda su propio X-Request-ID lo reutilizamos (así se puede
    # seguir la misma petición entre varios servicios); si no, generamos uno.
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    inicio = time.perf_counter()
    logger.info(f"[{request_id}] --> {request.method} {request.url.path}")

    # Si no viene la API key cortamos aquí: al no llamar a call_next, la petición
    # no llega al endpoint y éste ni siquiera se ejecuta.
    if request.url.path.startswith(RUTAS_PROTEGIDAS) and request.headers.get("X-API-Key") != API_KEY:
        logger.warning(f"[{request_id}] Acceso denegado a {request.url.path}: falta o es incorrecta la cabecera X-API-Key")
        response = JSONResponse(
            status_code=401,
            content={"detail": "Cabecera X-API-Key ausente o incorrecta"},
        )
    else:
        response = await call_next(request)

    duracion = time.perf_counter() - inicio
    # Añadimos cabeceras a la respuesta de TODOS los endpoints
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duracion:.4f}"
    logger.info(f"[{request_id}] <-- {response.status_code} en {duracion:.4f}s")
    return response

@app.exception_handler(404)
def not_found_handler(request: Request, exc: HTTPException):
    logger.warning(f"Ruta no encontrada: {request.method} {request.url}")
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>404 - Not Found</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

            * { margin: 0; padding: 0; box-sizing: border-box; }

            body {
                background: #000;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                perspective: 400px;
            }

            .stars {
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: radial-gradient(2px 2px at 20px 30px, #fff, transparent),
                            radial-gradient(2px 2px at 40px 70px, #fff, transparent),
                            radial-gradient(1px 1px at 90px 40px, #fff, transparent),
                            radial-gradient(2px 2px at 160px 120px, #fff, transparent),
                            radial-gradient(1px 1px at 200px 60px, #fff, transparent),
                            radial-gradient(2px 2px at 300px 200px, #fff, transparent),
                            radial-gradient(1px 1px at 400px 100px, #fff, transparent),
                            radial-gradient(2px 2px at 500px 300px, #fff, transparent),
                            radial-gradient(1px 1px at 600px 180px, #fff, transparent),
                            radial-gradient(2px 2px at 700px 250px, #fff, transparent);
                background-repeat: repeat;
                background-size: 800px 400px;
                animation: twinkle 4s ease-in-out infinite alternate;
                z-index: 0;
            }

            @keyframes twinkle {
                0% { opacity: 0.5; }
                100% { opacity: 1; }
            }

            .error-code {
                font-family: 'Press Start 2P', monospace;
                font-size: 6rem;
                color: #FFE81F;
                text-shadow: 0 0 20px rgba(255, 232, 31, 0.5),
                             0 0 40px rgba(255, 232, 31, 0.3);
                z-index: 1;
                margin-bottom: 2rem;
                animation: pulse 2s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }

            .crawl-container {
                z-index: 1;
                transform: rotateX(25deg);
                animation: float 3s ease-in-out infinite;
            }

            @keyframes float {
                0%, 100% { transform: rotateX(25deg) translateY(0); }
                50% { transform: rotateX(25deg) translateY(-15px); }
            }

            .message {
                font-family: 'Press Start 2P', monospace;
                font-size: 1.6rem;
                color: #FFE81F;
                text-align: center;
                line-height: 2.2;
                text-shadow: 0 0 10px rgba(255, 232, 31, 0.4);
            }

            .home-btn {
                margin-top: 3rem;
                z-index: 1;
                font-family: 'Press Start 2P', monospace;
                font-size: 0.9rem;
                color: #FFE81F;
                background: transparent;
                border: 2px solid #FFE81F;
                padding: 1rem 2rem;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.3s ease;
            }

            .home-btn:hover {
                background: #FFE81F;
                color: #000;
                box-shadow: 0 0 20px rgba(255, 232, 31, 0.6);
            }
        </style>
    </head>
    <body>
        <div class="stars"></div>
        <div class="error-code">404</div>
        <div class="crawl-container">
            <p class="message">This is not the page<br>you were looking for.</p>
        </div>
        <a href="/docs" class="home-btn">Return to safety</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=404)

@app.get("/hello")
def initial_greeting():
    logger.info("Recibida petición al saludo genérico")
    return {"msg": "Hola mundo!!!"}

@app.get("/hello/{name}")
def custom_greeting(name: str):
    time_start = time.perf_counter()
    logger.info(f"Recibida petición al saludo personalizado para {name}")
    processed_name = name.capitalize()
    if processed_name == "Pepe":
        logger.warning("Pepe ha entrado a la web!!")
    time_end = time.perf_counter()
    logger.info(f"Ha tardado {time_end-time_start}")
    return {"msg": f"Hello, {processed_name}!!!"}

def enviar_email_bienvenida(email: str):
    logger.info(f"📧 Simulando envío de email a {email}...")
    time.sleep(10)  # Simular retardo para ver la asincronía
    logger.info(f"✅ Email de bienvenida enviado a {email}")

@app.post("/users/")
def create_user(user: User, background_tasks: BackgroundTasks):
    logger.info(f"📥 Registro de usuario recibido: {user}")
    
    db = SessionLocal()
    existing = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    user_db = UserDB(username=user.username, email=user.email, age=user.age)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    db.close()
    logger.info(f"✅ Usuario guardado en DB: {user_db.username}")
    # Tarea en segundo plano
    background_tasks.add_task(enviar_email_bienvenida, user.email)
    return {
        "msg": "Usuario registrado correctamente",
        "usuario": {
            "id": user_db.id,
            "username": user_db.username,
            "email": user_db.email,
            "age": user_db.age
        }
    }


def enviar_email_cambios(email: str, cambios: dict):
    logger.info(f"📧 Simulando aviso de cambios a {email}: {cambios}")
    time.sleep(5)  # Simular retardo para ver la asincronía
    logger.info(f"✅ Aviso de cambios enviado a {email}")

@app.post("/login") # Example of SQL Injection
def login(UserDataLogin):
    # db.execute("SELECT * FROM USUARIOS WHERE USUARIO = {} AND PASSWORD = {}")
    "SELECT * FROM USUARIOS"

@app.patch("/users/{user_id}")
def update_user(
    user_id: int,                     # PATH PARAM: va dentro de la ruta
    datos: UserUpdate,                # BODY: JSON con los campos a cambiar
    background_tasks: BackgroundTasks,
    # QUERY PARAMS: van detrás de la ? -> /users/3?notificar=true&dry-run=false&motivo=...
    notificar: bool = Query(False, description="Si es true, avisa al usuario por email (tarea en segundo plano)"),
    dry_run: bool = Query(False, alias="dry-run", description="Si es true, simula el cambio sin guardarlo en la DB"),
    motivo: str = Query("sin especificar", min_length=3, max_length=100, description="Motivo del cambio, queda en el log"),
):
    """Ejemplo que combina path param + query params + body en una misma petición."""
    logger.info(f"✏️ PATCH /users/{user_id} | motivo='{motivo}' | notificar={notificar} | dry_run={dry_run}")

    db = SessionLocal()
    user_db = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user_db is None:
        db.close()
        raise HTTPException(status_code=404, detail=f"No existe ningún usuario con id {user_id}")

    # exclude_unset -> sólo los campos que el cliente ha enviado realmente en el body
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if not cambios:
        db.close()
        raise HTTPException(status_code=400, detail="El body no contiene ningún campo que actualizar")

    if "email" in cambios:
        repetido = db.query(UserDB).filter(UserDB.email == cambios["email"], UserDB.id != user_id).first()
        if repetido:
            db.close()
            raise HTTPException(status_code=400, detail="Ese email ya pertenece a otro usuario")

    antes = {"username": user_db.username, "email": user_db.email, "age": user_db.age}
    for campo, valor in cambios.items():
        setattr(user_db, campo, valor)

    if dry_run:
        db.rollback()  # deshacemos los cambios: sólo era una simulación
        despues = {**antes, **cambios}
        logger.info(f"🧪 dry-run activado: los cambios de {user_id} NO se han guardado")
    else:
        db.commit()
        db.refresh(user_db)
        despues = {"username": user_db.username, "email": user_db.email, "age": user_db.age}
        logger.info(f"✅ Usuario {user_id} actualizado: {cambios}")
    db.close()

    if notificar and not dry_run:
        background_tasks.add_task(enviar_email_cambios, despues["email"], cambios)

    return {
        "msg": "Simulación de actualización (dry-run), nada se ha guardado" if dry_run else "Usuario actualizado correctamente",
        "user_id": user_id,          # viene del path param
        "motivo": motivo,            # viene de un query param
        "avisado_por_email": notificar and not dry_run,
        "cambios_solicitados": cambios,  # viene del body
        "antes": antes,
        "despues": despues,
    }

@app.get("/info-headers")
def info_headers(
    request: Request,
    # FastAPI traduce user_agent -> "User-Agent" (los _ pasan a -) al leer la cabecera
    user_agent: Optional[str] = Header(None, description="Quién hace la petición: navegador, script..."),
    accept_language: Optional[str] = Header(None, description="Idiomas que acepta el cliente"),
    # Con alias indicamos el nombre exacto de una cabecera personalizada
    x_client_version: Optional[str] = Header(None, alias="X-Client-Version", description="Versión del cliente"),
):
    """Ejemplo de endpoint que trabaja con las cabeceras que llegan en la petición."""
    logger.info(f"🔎 Cabeceras recibidas: {dict(request.headers)}")

    if user_agent is None:
        tipo_cliente = "desconocido"
    elif "python-requests" in user_agent.lower():
        tipo_cliente = "script de Python"
    elif "mozilla" in user_agent.lower():
        tipo_cliente = "navegador"
    else:
        tipo_cliente = "otro"

    # "es-ES,es;q=0.9,en;q=0.8" -> nos quedamos con el idioma preferido
    idioma = accept_language.split(",")[0] if accept_language else "no indicado"
    saludo = "¡Hola!" if idioma.startswith("es") else "Hello!"

    return {
        "saludo": saludo,
        "tipo_cliente": tipo_cliente,
        "user_agent": user_agent,
        "idioma_preferido": idioma,
        "x_client_version": x_client_version or "no enviada",
        "total_cabeceras": len(request.headers),
        # request.headers permite ver TODAS las cabeceras sin declararlas una a una
        "todas_las_cabeceras": dict(request.headers),
    }

@app.get("/admin/stats")
def admin_stats():
    """Ruta protegida: el middleware la corta si no llega la cabecera X-API-Key."""
    db = SessionLocal()
    total = db.query(UserDB).count()
    db.close()
    logger.info("🔐 Acceso concedido a las estadísticas de administración")
    return {"msg": "Has superado el control del middleware", "usuarios_registrados": total}
