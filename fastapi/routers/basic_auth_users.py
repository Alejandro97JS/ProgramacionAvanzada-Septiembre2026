from re import search
from fastapi import Depends, APIRouter, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, oauth2

router = APIRouter(prefix="/b_auth")

#Instancia del sistema de autenticación
oauth2 = OAuth2PasswordBearer(
    tokenUrl="login" # Es la url que se encargará de gestionar la autenticación
    )

class User(BaseModel):
    username:str
    full_name:str
    email:str
    disabled:bool

class UserDB(User):
    password:str

users_db = {
    "davdoors":
        {
            "username": "davdoors",
            "full_name": "David Dorado",
            "email": "david.dorado@gmail.con",
            "disabled": False,
            "password": "123456"
        },
    "andrear":
        {
            "username": "andrear",
            "full_name": "Andrea Ramirez",
            "email": "andrea.ramirez@gmail.com",
            "disabled": True,
            "password": "qwerty789"
        }
}

def search_user_db(username:str):
    if username in users_db:
        return UserDB(**users_db[username])

def search_user(username:str):
    if username in users_db:
        return User(**users_db[username])

async def current_user(token:str = Depends(oauth2)):
    user = search_user(token) # esto es por que en el login que hice el access_token que devolví es el username
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate":"Bearer"}) # Añade cabecera que indica que se requiere autenticación Bearer
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive User"
        )
    return user



@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()): # epends() vacío no significa “no dependas de nada”. Significa: usa como dependencia la clase del type hint, es decir, OAuth2PasswordRequestForm 
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="User not found")

    user = search_user_db(form.username)
    if not form.password == user.password:
        raise HTTPException(status_code=400, detail="Invalid password")

    #este token debe guardarlo el que intenta iniciar sesión, porque sera lo que use para ser autorizado
    return {"access_token": user.username, "token_type": "bearer"}

@router.get("/users/me")
async def me(user:User = Depends(current_user)):
    return user
