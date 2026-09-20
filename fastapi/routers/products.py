from fastapi import APIRouter, HTTPException

router = APIRouter(prefix='/products',
                    tags=["products"]   # Esto es para agrupar este router en la documentation de swager
                    )

products_list = [
    "Teclado Mecánico Xtreme",
    "Auriculares ThunderBeat",
    "Mouse ProGamer GX",
    "Silla Ergonómica Flexi",
    "Monitor UltraWide Vision"
]

@router.get("/")
async def products():
    return products_list

@router.get("/{id}")
async def products(id:int):
    l = len(products_list)
    print(f"list len {l}")
    if id >= l or id <0:
        raise HTTPException(status_code=400)
    return products_list[id]