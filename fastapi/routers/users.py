from ast import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

logging.basicConfig(
    filename="general.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]"
)

log = logging.getLogger(__name__)

# Add a handler to also print log to the terminal/console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s", 
    datefmt="[%Y-%m-%d %H:%M:%S]"
))
if not any(isinstance(handler, logging.StreamHandler) for handler in log.handlers):
    log.addHandler(console_handler)

router = APIRouter(tags=["users"])

# Entity User
class User(BaseModel):
    id:int
    name:str
    surname:str
    url:str
    age:int

# Simulating a data base with users
users_list = [
    User(
        id=1,
        name="David",
        surname="Dorado",
        url="http://localhost:8000/users/1",
        age=20
    ),
    User(
        id=2,
        name="Francisco",
        surname="Dorado",
        url="http://localhost:8000/users/2",
        age=25
    ),
    User(
        id=3,
        name="Maria",
        surname="Garcia",
        url="http://localhost:8000/users/3",
        age=30
    ),
    User(
        id=4,
        name="Carlos",
        surname="Martinez",
        url="http://localhost:8000/users/4",
        age=28
    ),
    User(
        id=5,
        name="Lucia",
        surname="Lopez",
        url="http://localhost:8000/users/5",
        age=22
    ),
]

def search_user(user:User):
    matches = list(filter(lambda u: u.id == user.id, users_list))
    return matches[0] if matches else None

@router.get("/users_json")
async def users_json():
    return [{"name":"david", "surname":"dorado","url":"http://localhost:8000/users/1","age":20},
            {"name":"francisco", "surname":"dorado","url":"http://localhost:8000/users/2","age":40},
            {"name":"Maria", "surname":"dorado","url":"http://localhost:8000/users/3","age":30}]

@router.get("/users")
async def users():
    return users_list[0]

@router.get("/user/{id}")
async def user(id:int):
    users = filter(lambda user: user.id == id, users_list)
    print(f"users type: {type(users)}")
    try:
        # the firs user on the list
        return list(users)[0]
    except:

        return {"error":"No se ha encontrado el usuario"}

#esta es la misma operación que el de arriba pero este funciona por query
@router.get("/user/")
async def user(id:int):
    users = filter(lambda user: user.id == id, users_list)
    print(f"users type: {type(users)}")
    try:
        # the firs user on the list
        return list(users)[0]
    except:

        return {"error":"No se ha encontrado el usuario"}


# Crear un usuario con POST
@router.post("/user/", response_model= User, status_code=201)
async def create_user(user:User):
    found = search_user(user)
    if found is None:
        users_list.append(user)
        log.info(f"user {user.id} successfully created ")
        return user
    error =f"user {user.id} already registered"
    log.error(error)
    raise HTTPException(status_code=400, detail=error)

# Actualizar usuario completo con PUT
@router.put("/user/")
async def update_user(user:User):
    found = False

    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            print (f"user {user.id}")
            found = True
            users_list[index] = user
            return user

    if not found:
        log.error(f"user {user.id} already registered")
        return {"error":"No se ha encontrado el usuario"}

# Eliminar usuario
@router.delete("/user/{id}", status_code=200)
async def delete_user(id:int):
    found = False
    for index, u in enumerate(users_list):
        if u.id == id:
            found = True
            log.info("delete ok")
            del users_list[index]
            break

    if not found:
        log.error("User not found")
        raise HTTPException(404, "User not found in the list")