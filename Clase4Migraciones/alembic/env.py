"""Punto de entrada de Alembic: se ejecuta en CADA comando (upgrade, downgrade, revision...).

Lo genera `alembic init alembic` y sólo hemos cambiado tres cosas (marcadas con [CAMBIO]):
  1. La URL de la base de datos sale de app/database.py.
  2. target_metadata apunta a los metadatos de NUESTROS modelos (necesario para --autogenerate).
  3. render_as_batch=True, imprescindible con SQLite (explicado abajo).
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# [CAMBIO 1 y 2] Importamos la URL y los modelos de la aplicación.
# Importar app.models es lo que "registra" la tabla users dentro de Base.metadata;
# si añades un modelo nuevo en otro fichero, impórtalo también aquí.
from app.database import DATABASE_URL, Base
import app.models  # noqa: F401  (se importa sólo por su efecto: registrar los modelos)

# Objeto con la configuración leída de alembic.ini
config = context.config

# [CAMBIO 1] alembic.ini tiene sqlalchemy.url vacía: la rellenamos aquí.
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configura los logs según la sección [loggers] de alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# [CAMBIO 2] Con esto `alembic revision --autogenerate` puede comparar
# "cómo dicen los modelos que debería ser la BD" contra "cómo es la BD de verdad"
# y escribir él solo el borrador de la migración.
target_metadata = Base.metadata

# [CAMBIO 3] SQLite casi no soporta ALTER TABLE (no puede cambiar el tipo de una
# columna, ni hacerla NOT NULL, ni borrar restricciones...). El "modo batch" de
# Alembic lo resuelve así: crea una tabla nueva con el esquema correcto, copia
# los datos, borra la vieja y renombra la nueva. Con render_as_batch=True el
# autogenerate ya escribe las migraciones usando `with op.batch_alter_table(...)`.
RENDER_AS_BATCH = True


def run_migrations_offline() -> None:
    """Modo 'offline' (`alembic upgrade head --sql`).

    No se conecta a la BD: sólo imprime el SQL que se ejecutaría. Útil cuando
    un DBA quiere revisar el script antes de lanzarlo en producción.
    """
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=RENDER_AS_BATCH,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo normal: se conecta a la BD y aplica las migraciones de verdad."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=RENDER_AS_BATCH,
        )

        # Cada migración se ejecuta dentro de una transacción: si algo falla a
        # mitad, se deshace y la tabla alembic_version no avanza.
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
