from fastapi import Depends, APIRouter, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, oauth2
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

# definir el algoritmo de encriptación
ALGORITHM = "HS256" # este es el mas usado
# definir la duración de token (minutes)
TOKEN_DURATION = 1
# definir un secret para hacer el token aun mas seguro, con una semilla que solo sepa el backend
# Se puede usar openssl en la terminal (openssl rand -hex 32)
SECRET = "ac4e4397a4258350442050cb109872887bd72812b30d276cc1c1111e7a8253e2"

router = APIRouter(prefix="/auth")

#Instancia del sistema de autenticación
oauth2 = OAuth2PasswordBearer(
    tokenUrl="login" # Es la url que se encargará de gestionar la autenticación
    )

#definir contexto de encriptación
crypt = CryptContext(
    schemes=["bcrypt"], # define el algoritmo de encriptación
    )

class User(BaseModel):
    username:str
    full_name:str
    email:str
    disabled:bool

class UserDB(User):
    password:str

# las contraseñas se ha generado usando una herramienta generadora de hash bcrypt
users_db = {
    "davdoors":
        {
            "username": "davdoors",
            "full_name": "David Dorado",
            "email": "david.dorado@gmail.con",
            "disabled": False,
            "password": "$2a$12$uBw1QbprsTKlwXb5QXCz7uMgkwJPNr5SdJLBS3isP7xfWTURfBYpu" # 123456
        },
    "andrear":
        {
            "username": "andrear",
            "full_name": "Andrea Ramirez",
            "email": "andrea.ramirez@gmail.com",
            "disabled": True,
            "password": "$2a$12$PobDO9cDwr0GQa6mknbhUO17gJNGlHYrJpPELULbYMLHqIfX/K1v2" # qwerty789
        }
}

def search_user(username:str)->User:
    if username in users_db:
        return User(**users_db[username])

async def auth_user(token:str = Depends(oauth2)):
    exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate":"Bearer"})

    try:
        username = jwt.decode(token, key=SECRET, algorithms=ALGORITHM).get("sub") # ver access_token en /login
        if username is None:
            raise exception
    except JWTError:
        raise exception

    return search_user(username)


async def current_user(user:User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive User"
        )
    return user



def search_user_db(username:str):
    if username in users_db:
        return UserDB(**users_db[username])

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="User not found")

    user = search_user_db(form.username)

    # verificar contraseña recibida en el Form vs la guardada en la base de datos
    print("verify password")
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # fecha y hora actual, más un delta de 1 minuto
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_DURATION)
    access_token = {
        "sub": user.username, 
        "exp":expire}

    return {"access_token": jwt.encode(access_token, key=SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.get("/users/me")
async def me(user:User = Depends(current_user)):
    return user
