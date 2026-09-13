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

# Process orders:
for order in orders:
    order_id = order["order_id"]
    items = order["items"]
    total = 0
    for sku, quantity in items.items():
        product = inventory.get(sku)
        if not product:
            print(f"Error: Product with SKU {sku} not found.")
            continue
        if product["current_stock"] < quantity:
            # Do not include any unit of this product in the order.
            # This is a business decision: another option could be to include the available stock.
            print(f"Error: Insufficient stock for {product['name']}. Available: {product['current_stock']}, Requested: {quantity}")
            continue
        # Update stock
        product["current_stock"] -= quantity
        total += product["price"] * quantity
    print(f"Order ID: {order_id} - Total: ${total:.2f} - Purchase Completed")

# Show inventory report after processing orders:
print("\nInventory Report:\n")
for product in inventory.values():
    category_names = ", ".join([cat["name"] for cat in product["categories"]]) or "None"
    tag_names = ", ".join([tag["name"] for tag in product["tags"]]) or "None"
    print(f"Product: {product['name']} (SKU: {product['sku']}) - Price: ${product['price']:.2f}, Stock: {product['current_stock']}, Categories: [{category_names}], Tags: [{tag_names}]")
