from fastapi import FastAPI
from routers import products, users, basic_auth_users, jwt_auth_users
from fastapi.staticfiles import StaticFiles

app = FastAPI()

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