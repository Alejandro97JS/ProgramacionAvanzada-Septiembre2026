class Category:
    def __init__(self, name, description=None):
        self.name = name
        self.description = description or ''

    def __eq__(self, other):
        return isinstance(other, Category) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Category(name='{self.name}', description='{self.description}')"


class Tag:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Tag) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Tag(name='{self.name}')"


class Product:
    def __init__(self, name, sku, price, current_stock=0, categories=None, tags=None):
        self.name = name
        self.sku = sku
        self.price = price
        self.current_stock = current_stock
        self.categories = categories or []
        self.tags = tags or []

    def check_stock(self, requested_units):
        if self.current_stock >= requested_units:
            return True, requested_units
        return False, self.current_stock

    def update_stock(self, amount):
        self.current_stock += amount

    def get_info(self):
        categories = ', '.join([cat.name for cat in self.categories]) or 'None'
        tags = ', '.join([tag.name for tag in self.tags]) or 'None'
        return f"Product: {self.name} (SKU: {self.sku}) - Price: ${self.price:.2f}, Stock: {self.current_stock}, Categories: [{categories}], Tags: [{tags}]"

    def can_buy(self):
        return True

    def __repr__(self):
        return f"Product(name='{self.name}', sku='{self.sku}', price={self.price}, current_stock={self.current_stock})"


class PremiumProduct(Product):

    def can_buy(self, person_name=""):
        if person_name == "Johnyy Depp":
            return True
        else:
            return super().can_buy() # Delego a lo que me diga la clase padre.

class Inventory:
    def __init__(self):
        self.products = {}

    def add_product(self, product):
        if product.sku not in self.products:
            self.products[product.sku] = product

    def get_product(self, sku):
        return self.products.get(sku)

    def generate_inventory_report(self):
        report = [p.get_info() for p in self.products.values()]
        return '\n'.join(report)

    def __repr__(self):
        return f"Inventory({len(self.products)} products)"


class Order:
    def __init__(self, order_id):
        self.order_id = order_id
        self.products = {}

    def add_product(self, product, quantity):
        if product.sku in self.products:
            self.products[product.sku]['quantity'] += quantity
        else:
            self.products[product.sku] = {'product': product, 'quantity': quantity}

    def buy(self):
        total = 0
        for sku, item in self.products.items():
            product = item['product']
            quantity = item['quantity']
            has_enough_stock, _ = product.check_stock(quantity)
            if not has_enough_stock:
                # Business decision: do not include any unit of this product in the order.
                print(
                    f"Error: Insufficient stock for {product.name}. "
                    f"Available: {product.current_stock}, Requested: {quantity}"
                )
                continue
            product.update_stock(-quantity)
            total += product.price * quantity
        return f"Order ID: {self.order_id} - Total: ${total:.2f} - Purchase Completed"

    def __repr__(self):
        return f"Order(order_id='{self.order_id}', total_items={len(self.products)})"


if __name__ == "__main__":
    # Create categories
    cat_electronics = Category("Electronics", "Devices and gadgets")
    cat_office = Category("Office", "Office supplies and equipment")

    # Create tags
    tag_on_sale = Tag("On Sale")
    tag_new_arrival = Tag("New Arrival")
    tag_best_seller = Tag("Best Seller")

    # Create inventory
    inventory = Inventory()

    # Create products with categories and tags
    p1 = Product("Laptop", "SKU123", 1200, 10, categories=[cat_electronics], tags=[tag_new_arrival, tag_best_seller])
    p2 = Product("Mouse", "SKU456", 25, 100, categories=[cat_electronics], tags=[tag_on_sale])
    p3 = Product("Keyboard", "SKU789", 50, 50, categories=[cat_office], tags=[tag_best_seller])
    p4 = Product("Monitor", "SKU101", 300, 20, categories=[cat_electronics], tags=[])

    # Add products to inventory
    inventory.add_product(p1)
    inventory.add_product(p2)
    inventory.add_product(p3)
    inventory.add_product(p4)

    # Create orders
    order1 = Order("ORDER001")
    order1.add_product(p1, 2)
    order1.add_product(p2, 5)

    order2 = Order("ORDER002")
    order2.add_product(p3, 3)
    order2.add_product(p4, 1)

    order3 = Order("ORDER003")
    order3.add_product(p2, 10)
    order3.add_product(p4, 2)

    # Process purchases
    print(order1.buy())
    print(order2.buy())
    print(order3.buy())

    # Show final inventory report
    print("\nInventory Report:\n")
    print(inventory.generate_inventory_report())
