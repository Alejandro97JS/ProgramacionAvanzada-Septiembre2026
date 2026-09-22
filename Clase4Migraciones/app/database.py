"""Conexión a la base de datos.

Este módulo lo usan DOS actores distintos:
  * La API (main.py) para abrir sesiones y leer/escribir usuarios.
  * Alembic (alembic/env.py) para saber a qué base de datos aplicar las migraciones.

Por eso DATABASE_URL se define aquí y sólo aquí.
"""

from pathlib import Path

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Ruta absoluta al fichero .db, para que dé igual desde qué carpeta lancemos
# uvicorn, alembic o los scripts: siempre se usa Clase4Migraciones/usuarios.db
DB_PATH = Path(__file__).resolve().parent.parent / "usuarios.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Convención de nombres para índices y restricciones.
# Sin ella, SQLAlchemy deja que la base de datos invente los nombres de algunas
# restricciones (o las deja sin nombre). Luego, para BORRARLAS o MODIFICARLAS en
# una migración, Alembic necesita saber cómo se llaman. Fijando la convención
# desde el principio todos los nombres son predecibles (pk_users, ix_users_email...).
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base = declarative_base(metadata=MetaData(naming_convention=NAMING_CONVENTION))

# OJO: aquí NO hacemos Base.metadata.create_all(bind=engine) como en clases
# anteriores. create_all sólo crea tablas que NO existen: si la tabla ya existe
# no le añade columnas, no le quita columnas, no cambia tipos... nada.
# A partir de ahora quien crea y modifica las tablas es Alembic.
