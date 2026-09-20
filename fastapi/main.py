from fastapi import FastAPI
from routers import products, users

app = FastAPI()

# Añadir routers
app.include_router(products.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return "hola fastapi"


@app.get("/url")
async def github_url():
    return {"url":"https://api.github.com/user"}