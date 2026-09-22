"""API de usuarios DESPUÉS de las migraciones (esquema en la versión 0003).

Comparada con Clase4Peticiones:
  * Ya no hay Base.metadata.create_all(): las tablas las gestiona Alembic.
  * Al arrancar comprueba que la BD está en la última migración (`head`).
    Si alguien despliega el código nuevo sin migrar la BD, la API no arranca
    en vez de fallar más tarde con errores raros tipo "no such column: birth_date".
  * Usa las columnas nuevas: birth_date (la edad se calcula), is_active y created_at.

    uvicorn main:app --reload
"""

import logging
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.database import SessionLocal, engine
from app.models import UserDB

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ALEMBIC_INI = Path(__file__).resolve().parent / "alembic.ini"


def comprobar_migraciones():
    """Compara la versión de la BD con la última migración que hay en alembic/versions/."""
    ultima = ScriptDirectory.from_config(Config(str(ALEMBIC_INI))).get_current_head()
    with engine.connect() as conn:
        actual = MigrationContext.configure(conn).get_current_revision()

    if actual != ultima:
        raise RuntimeError(
            f"La BD está en la versión {actual!r} pero el código espera {ultima!r}. "
            "Ejecuta `alembic upgrade head` antes de arrancar la API."
        )
    logger.info(f"✅ Base de datos al día (revisión {actual})")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lo que va antes del yield se ejecuta una vez, al arrancar la API
    comprobar_migraciones()
    yield


app = FastAPI(
    title="Usuarios con migraciones",
    description="La API de usuarios, con el esquema gestionado por Alembic.",
    version="3.0.0",
    lifespan=lifespan,
)


# --- Modelos Pydantic ---
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, description="Nombre de usuario (mínimo 3 caracteres)")
    email: str = Field(..., description="Email del usuario")
    birth_date: Optional[date] = Field(None, description="Fecha de nacimiento (AAAA-MM-DD), opcional")


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    birth_date: Optional[date]
    age: Optional[int]  # ya no se guarda: se calcula al vuelo desde birth_date
    is_active: bool
    created_at: datetime


def calcular_edad(nacimiento: Optional[date]) -> Optional[int]:
    if nacimiento is None:
        return None
    hoy = date.today()
    return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))


def to_out(user: UserDB) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        birth_date=user.birth_date,
        age=calcular_edad(user.birth_date),
        is_active=user.is_active,
        created_at=user.created_at,
    )


# --- Endpoints ---
@app.post("/users/", response_model=UserOut, status_code=201)
def create_user(user: UserCreate):
    with SessionLocal() as db:
        if db.query(UserDB).filter(UserDB.email == user.email).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        # No pasamos is_active ni created_at: los rellena la BD con su server_default
        user_db = UserDB(username=user.username, email=user.email, birth_date=user.birth_date)
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
        logger.info(f"✅ Usuario creado: {user_db.username}")
        return to_out(user_db)


@app.get("/users/", response_model=list[UserOut])
def list_users(
    incluir_inactivos: bool = Query(False, description="Si es true, lista también las cuentas desactivadas"),
):
    with SessionLocal() as db:
        consulta = db.query(UserDB)
        if not incluir_inactivos:
            consulta = consulta.filter(UserDB.is_active.is_(True))
        return [to_out(u) for u in consulta.order_by(UserDB.id).all()]


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    with SessionLocal() as db:
        user_db = db.get(UserDB, user_id)
        if user_db is None:
            raise HTTPException(status_code=404, detail=f"No existe ningún usuario con id {user_id}")
        return to_out(user_db)


@app.delete("/users/{user_id}", response_model=UserOut)
def deactivate_user(user_id: int):
    """'Soft delete': no borra la fila, sólo marca is_active = False (columna de la 0002)."""
    with SessionLocal() as db:
        user_db = db.get(UserDB, user_id)
        if user_db is None:
            raise HTTPException(status_code=404, detail=f"No existe ningún usuario con id {user_id}")
        user_db.is_active = False
        db.commit()
        db.refresh(user_db)
        logger.info(f"🚫 Usuario {user_id} desactivado")
        return to_out(user_db)
