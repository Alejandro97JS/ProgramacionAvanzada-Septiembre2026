"""Simula que la API lleva tiempo en producción y ya tiene usuarios REALES.

Se ejecuta justo después de `alembic upgrade 0001`, cuando la tabla todavía
tiene la columna `age`. Así, al aplicar la 0002 y la 0003, se ve que las
migraciones transforman la tabla SIN perder estos datos.

Usamos SQL directo (y no el modelo UserDB) porque el modelo ya está en la
versión final (sin `age`) y la tabla todavía está en la versión 0001.

    python seed_datos.py
"""

from sqlalchemy import inspect, text

from app.database import engine

USUARIOS_EN_PRODUCCION = [
    {"username": "juan", "email": "juan@example.com", "age": 20},
    {"username": "maria", "email": "maria@example.com", "age": 34},
    {"username": "ramon_el_veterano_del_club", "email": "ramon@example.com", "age": 61},
    {"username": "lucia", "email": "lucia@example.com", "age": None},  # no dio su edad
]


def main():
    columnas = {c["name"] for c in inspect(engine).get_columns("users")} if inspect(engine).has_table("users") else set()
    if "age" not in columnas:
        raise SystemExit(
            "La tabla users no existe o ya no tiene la columna 'age'.\n"
            "Este script es para la versión 0001: ejecuta antes `alembic upgrade 0001`."
        )

    # engine.begin() abre una transacción y hace commit al salir del with
    with engine.begin() as conn:
        for usuario in USUARIOS_EN_PRODUCCION:
            conn.execute(
                text("INSERT OR IGNORE INTO users (username, email, age) VALUES (:username, :email, :age)"),
                usuario,
            )
    print(f"Insertados {len(USUARIOS_EN_PRODUCCION)} usuarios de 'producción' (los repetidos se ignoran).")


if __name__ == "__main__":
    main()
