from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return "hola fastapi"


@app.get("/url3")
async def github_url():
    return {"url":"https://api.github.com/user"}