import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
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

# --- FastAPI setup ---
app = FastAPI(
    title="Mi primera API con FastAPI",
    description="Una API de ejemplo con base de datos SQLite.",
    version="1.0.0"
)

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
    logger.info(f"Recibida petición al saludo personalizado para {name}")
    processed_name = name.capitalize()
    if processed_name == "Pepe":
        logger.warning("Pepe ha entrado a la web!!")
    return {"msg": f"Hello, {processed_name}!!!"}

def enviar_email_bienvenida(email: str):
    logger.info(f"📧 Simulando envío de email a {email}...")
    import time
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
