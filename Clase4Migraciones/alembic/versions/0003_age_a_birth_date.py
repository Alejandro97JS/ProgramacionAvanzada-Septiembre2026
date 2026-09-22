"""Sustituir age por birth_date (migración de ESQUEMA + DATOS)

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-23

NUEVO REQUISITO
---------------
Guardar la edad fue mala idea: el usuario que se registró con 20 años sigue
teniendo 20 dentro de 5 años. Lo correcto es guardar la FECHA DE NACIMIENTO y
calcular la edad cuando haga falta.

Si nos limitáramos a borrar `age` y crear `birth_date` perderíamos la edad de
todos los usuarios que ya están registrados. Por eso esta migración, además de
cambiar el esquema, CONVIERTE LOS DATOS:

  1. Añadir birth_date (nullable).
  2. Para cada usuario con edad: birth_date = 1 de enero de (año actual - edad).
     Es una aproximación: con sólo la edad no se puede saber el día exacto.
  3. Borrar la columna age.

¿Cómo se genera? Cambiamos age por birth_date en app/models.py y:

    alembic revision --autogenerate -m "age a birth_date"

Autogenerate escribe add_column(birth_date) + drop_column(age), ¡y NADA MÁS!
No sabe que una columna "se convierte" en la otra. Si aplicásemos el borrador
tal cual, borraríamos las edades sin guardarlas en ningún sitio.
El paso 2 lo hemos escrito a mano. Esta es la razón principal de revisar
SIEMPRE lo que genera --autogenerate.
"""

from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# IMPORTANTE: en una migración NO se importa app.models.UserDB.
# El modelo describe la tabla en su versión MÁS NUEVA (ya sin `age`) y esta
# migración tiene que trabajar con la tabla tal y como está en ESTE punto de la
# historia. Por eso declaramos aquí una "foto" ligera sólo con las columnas que
# necesitamos. Así la migración seguirá funcionando aunque el modelo cambie en
# el futuro.
users = sa.table(
    "users",
    sa.column("id", sa.Integer),
    sa.column("age", sa.Integer),
    sa.column("birth_date", sa.Date),
)


def upgrade() -> None:
    # Paso 1: nueva columna, de momento vacía
    op.add_column("users", sa.Column("birth_date", sa.Date(), nullable=True))

    # Paso 2: migración de datos. op.get_bind() nos da la conexión que está
    # usando Alembic, dentro de la misma transacción que el resto de pasos.
    conn = op.get_bind()
    anio_actual = date.today().year
    filas = conn.execute(sa.select(users.c.id, users.c.age).where(users.c.age.is_not(None))).all()
    for user_id, edad in filas:
        conn.execute(
            users.update()
            .where(users.c.id == user_id)
            .values(birth_date=date(anio_actual - edad, 1, 1))
        )

    # Paso 3: ahora sí, fuera la columna vieja
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("age")


def downgrade() -> None:
    """Deshacer: volver a tener `age` calculada desde birth_date.

    Ojo: es una vuelta atrás "con pérdidas". La fecha exacta de nacimiento de
    los usuarios nuevos no cabe en una edad, así que si luego volvemos a hacer
    upgrade tendrán el 1 de enero como fecha. Muchas migraciones de datos no
    son 100 % reversibles; hay que decidir (y documentar) qué se hace.
    """
    op.add_column("users", sa.Column("age", sa.Integer(), nullable=True))

    conn = op.get_bind()
    hoy = date.today()
    filas = conn.execute(
        sa.select(users.c.id, users.c.birth_date).where(users.c.birth_date.is_not(None))
    ).all()
    for user_id, nacimiento in filas:
        # Restamos 1 si este año todavía no ha sido su cumpleaños
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        conn.execute(users.update().where(users.c.id == user_id).values(age=edad))

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("birth_date")
