"""Enseña cómo está la base de datos AHORA MISMO: versión, columnas y filas.

Lánzalo después de cada `alembic upgrade` / `alembic downgrade` para ver qué
ha cambiado:

    python ver_bd.py
"""

from sqlalchemy import inspect, text

from app.database import DB_PATH, engine


def main():
    if not DB_PATH.exists():
        print(f"Todavía no existe {DB_PATH.name}. Ejecuta `alembic upgrade 0001`.")
        return

    inspector = inspect(engine)
    with engine.connect() as conn:
        # Alembic guarda en esta tabla de UNA fila la revisión en la que está la BD.
        # Así sabe qué migraciones faltan por aplicar.
        if inspector.has_table("alembic_version"):
            version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
        else:
            version = None
        print(f"Versión de la BD (tabla alembic_version): {version or 'ninguna (BD sin migrar)'}")

        if not inspector.has_table("users"):
            print("La tabla users no existe.")
            return

        print("\nColumnas de users:")
        for col in inspector.get_columns("users"):
            nulo = "NULL" if col["nullable"] else "NOT NULL"
            default = f"  default={col['default']}" if col["default"] is not None else ""
            print(f"  - {col['name']:<12} {str(col['type']):<10} {nulo}{default}")

        filas = conn.execute(text("SELECT * FROM users")).mappings().all()
        print(f"\nFilas ({len(filas)}):")
        for fila in filas:
            print(f"  {dict(fila)}")


if __name__ == "__main__":
    main()
