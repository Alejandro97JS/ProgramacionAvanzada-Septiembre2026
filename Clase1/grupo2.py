def update_store (product: dict, unit: int) -> dict: 
    product.set('current_stock') = product.get('current_stock') - unit
    return product