# SOLUCIÓN COLABORATIVA HECHA EN CLASE

def update_store(product: dict, units: int) -> dict:
    if units <= 0:
        raise ValueError("Unidades debe ser positivo")
    product['current_stock'] -= units
    return product

def check_stock(product: dict, requested_units: int) -> tuple[bool, int]:
    units_to_provide = requested_units
    has_enough_stock = product["current_stock"] >= requested_units
    if not has_enough_stock:
        # Do not include any unit of this product in the order.
        # This is a business decision: another option could be to include the available stock.
        print(f"Error: Insufficient stock for {product['name']}. Available: {product['current_stock']}, Requested: {quantity}")
        units_to_provide = product["current_stock"]
         
    return (has_enough_stock, units_to_provide)

def process_orders(orders: list[dict], inventory: dict) -> None:
    for order in orders:
        order_id = order["order_id"]
        items = order["items"]
        total = 0
        for sku, quantity in items.items():
            product = inventory.get(sku)
            if not product:
                print(f"Error: Product with SKU {sku} not found.")
                continue
            has_stock, _ = check_stock(product, quantity)
            if not has_stock:
                continue
            # Update stock
            update_store(product, quantity)
            total += product["price"] * quantity
        print(f"Order ID: {order_id} - Total: ${total:.2f} - Purchase Completed")

def show_inventory_report(inventory) -> None:
    print("\nInventory Report:\n")
    for product in inventory.values():
        category_names = ", ".join([cat["name"] for cat in product["categories"]]) or "None"
        tag_names = ", ".join([tag["name"] for tag in product["tags"]]) or "None"
        print(f"Product: {product['name']} (SKU: {product['sku']}) - Price: ${product['price']:.2f}, Stock: {product['current_stock']}, Categories: [{category_names}], Tags: [{tag_names}]")


# SCRIPT PRINCIPAL, YA CON FUNCIONES:

# Categories management:
categories = [
    {"name": "Electronics", "description": "Devices and gadgets"},
    {"name": "Office", "description": "Office supplies and equipment"}
]

# Tags management:
tags = [
    {"name": "On Sale"},
    {"name": "New Arrival"},
    {"name": "Best Seller"}
]

# Products management:
products = [
    {"name": "Laptop", "sku": "SKU123", "price": 1200, "current_stock": 10, "categories": [categories[0]], "tags": [tags[1], tags[2]]},
    {"name": "Mouse", "sku": "SKU456", "price": 25, "current_stock": 100, "categories": [categories[0]], "tags": [tags[0]]},
    {"name": "Keyboard", "sku": "SKU789", "price": 50, "current_stock": 50, "categories": [categories[1]], "tags": [tags[2]]},
    {"name": "Monitor", "sku": "SKU101", "price": 300, "current_stock": 20, "categories": [categories[0]], "tags": []}
]

# Inventory management
inventory = {product["sku"]: product for product in products}

# Incoming orders:
orders = [
    {"order_id": "ORDER001", "items": {"SKU123": 2, "SKU456": 5}},
    {"order_id": "ORDER002", "items": {"SKU789": 3, "SKU101": 1}},
    {"order_id": "ORDER003", "items": {"SKU456": 10, "SKU101": 2}}
]

process_orders(orders, inventory)
# Show inventory report after processing orders:
show_inventory_report(inventory)
