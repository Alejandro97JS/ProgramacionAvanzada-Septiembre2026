"""Modelos ORM: cómo queremos que sea la base de datos AHORA (versión más reciente).

Alembic compara estos modelos con la base de datos real para detectar
diferencias (`alembic revision --autogenerate`). Por eso env.py importa este
módulo: si un modelo no se importa, Alembic no se entera de que existe.

Historia de la tabla `users` (cada paso es una migración en alembic/versions/):

    0001  id, username, email, age                  <- la API tal y como estaba en producción
    0002  + is_active, + created_at                 <- desactivar cuentas sin borrarlas
    0003  - age, + birth_date (convirtiendo datos)   <- la edad guardada se queda desfasada

Si quieres ver cómo era el modelo en la versión 0001, era exactamente el
UserDB de Clase4Peticiones/main.py.
"""

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, func, true

from app.database import Base


class UserDB(Base):
    __tablename__ = "users"

    # --- Columnas desde la 0001 (sin cambios) ---
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # --- Añadidas en la 0002 ---
    # server_default: el valor por defecto lo pone la BASE DE DATOS, no Python.
    # Es lo que permite añadir una columna NOT NULL a una tabla que ya tiene
    # filas: la BD rellena las filas antiguas con ese valor.
    is_active = Column(Boolean, nullable=False, server_default=true())
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # --- Añadida en la 0003 (sustituye a la antigua columna `age`) ---
    birth_date = Column(Date, nullable=True)
