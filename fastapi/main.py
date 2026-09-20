from fastapi import FastAPI
from routers import products, users, basic_auth_users, jwt_auth_users
from fastapi.staticfiles import StaticFiles
from data.db import UserSqlModel, create_db_and_tables, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

# Esta función se ejecuta automáticamente durante el ciclo de vida de la aplicación FastAPI.
# Sirve para crear las tablas en la base de datos antes de que la app empiece a aceptar peticiones.
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

# Se pasa la función lifespan al router para asegurar que las tablas de la base de datos
# se creen automáticamente antes de que la aplicación empiece a aceptar peticiones.
app = FastAPI(lifespan=lifespan)

# Añadir routers
app.include_router(products.router)
app.include_router(users.router)
app.include_router(basic_auth_users.router)
app.include_router(jwt_auth_users.router)

# Montar la carpeta con los archivos estáticos
app.mount(
    "/static", # path para exponer el directorio en la url
    StaticFiles(directory="static"), # path de la carpeta en el proyecto
    name="static" # alias para url_for. Si no se usa url_for en el proyecto, no se necesita
)

@app.get("/")
async def root():
    return "hola fastapi"


@app.get("/url")
async def github_url():
    return {"url":"https://api.github.com/user"}