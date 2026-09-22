"""Crear tabla users (esquema inicial, el que ya estaba en producción)

Revision ID: 0001
Revises:
Create Date: 2026-09-23

MIGRACIÓN BASE ("baseline")
---------------------------
Recoge la tabla tal y como la creaba Base.metadata.create_all() en
Clase4Peticiones: id, username, email, age.

¿Cómo se genera? Con el modelo antiguo en app/models.py y la BD vacía:

    alembic revision --autogenerate -m "crear tabla users"

Alembic ve que en los modelos hay una tabla `users` que en la BD no existe y
escribe el op.create_table(...) de abajo. Nosotros sólo lo revisamos y le
cambiamos el identificador aleatorio (p. ej. 'a3f9c1e2b7d4') por '0001' para que
se lea mejor en clase. En un proyecto real puedes dejar el aleatorio.

NOTA PARA UNA BD QUE YA EXISTÍA:
Si la base de datos de producción ya tenía la tabla (creada con create_all),
NO se ejecuta esta migración (fallaría: "table users already exists"). Se le
dice a Alembic "esta BD ya está en la 0001" con:

    alembic stamp 0001

stamp sólo escribe la versión en la tabla alembic_version, no toca nada más.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Identificadores que usa Alembic para encadenar las migraciones.
# down_revision = None significa "soy la primera de la cadena".
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Qué hacer para AVANZAR a esta versión."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        # op.f() indica "este nombre ya es definitivo, no le apliques la convención otra vez"
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    """Qué hacer para VOLVER a la versión anterior (aquí: a no tener nada).

    Se deshace en orden inverso al upgrade: primero índices, luego la tabla.
    """
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
