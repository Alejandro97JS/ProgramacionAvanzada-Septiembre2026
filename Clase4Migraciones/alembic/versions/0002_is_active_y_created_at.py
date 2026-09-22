"""Añadir is_active y created_at a users

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-23

NUEVO REQUISITO
---------------
  * Poder DESACTIVAR cuentas sin borrarlas ("soft delete") -> columna is_active.
  * Saber CUÁNDO se registró cada usuario                   -> columna created_at.

Ambas deben ser NOT NULL... pero la tabla ya tiene usuarios. Si hacemos
    ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL
¿qué valor ponemos en las filas que ya existen? La BD da error.

Aquí se ven las DOS formas típicas de resolverlo:

  A) is_active -> NOT NULL + server_default.
     La BD rellena las filas antiguas con el valor por defecto (true).
     Sirve cuando el mismo valor vale para todas las filas.

  B) created_at -> el patrón de 3 pasos, el más general:
       1. añadir la columna como NULLABLE
       2. rellenarla con un UPDATE (aquí podría ir cualquier lógica)
       3. cambiarla a NOT NULL
     (Además, SQLite no deja añadir con ALTER TABLE una columna cuyo default sea
      una función como CURRENT_TIMESTAMP, así que aquí el camino A ni siquiera
      funcionaría.)

¿Cómo se genera? Añadimos las dos columnas en app/models.py y lanzamos:

    alembic revision --autogenerate -m "is_active y created_at"

El autogenerate escribe SÓLO dos add_column con nullable=False. Nosotros
editamos a mano la parte de created_at para aplicar el patrón de 3 pasos.
¡Autogenerate genera un BORRADOR, siempre hay que revisarlo!
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"  # <- va después de la 0001
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- A) is_active: NOT NULL con valor por defecto en la BD ---
    # sa.true() se traduce a lo que entienda cada BD (1 en SQLite, true en PostgreSQL...)
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    # --- B) created_at: patrón de 3 pasos ---
    # Paso 1: añadir la columna permitiendo NULL (las filas antiguas quedan a NULL)
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))

    # Paso 2: rellenar las filas existentes. No sabemos cuándo se registraron los
    # usuarios antiguos, así que ponemos la fecha de la migración
    # (CURRENT_TIMESTAMP en SQLite es la hora UTC).
    op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    # Paso 3: ya no hay NULLs -> la hacemos NOT NULL y le ponemos default para
    # las filas nuevas. En SQLite esto necesita el modo batch (recrea la tabla).
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        )


def downgrade() -> None:
    # Volver atrás = quitar las dos columnas. Se pierde la información que
    # contenían (qué cuentas estaban desactivadas y las fechas de alta).
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("is_active")
