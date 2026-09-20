from fastapi import APIRouter, HTTPException

router = APIRouter()

products_list = [
    "Teclado Mecánico Xtreme",
    "Auriculares ThunderBeat",
    "Mouse ProGamer GX",
    "Silla Ergonómica Flexi",
    "Monitor UltraWide Vision"
]

@router.get("/products")
async def products():
    return products_list

@router.get("/products/{id}")
async def products(id:int):
    l = len(products_list)
    print(f"list len {l}")
    if id >= l or id <0:
        raise HTTPException(status_code=400)
    return products_list[id]