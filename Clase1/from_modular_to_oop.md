# 🏗️ Ejercicio por Grupos: De Programación Modular a Orientación a Objetos

## 📋 Descripción General

En este ejercicio vamos a **refactorizar** el script `with_methods.py` para transformarlo de un enfoque modular basado en funciones a uno basado en **Programación Orientada a Objetos (POO)**.

El script actual resuelve el mismo problema que `imperative_programming.py` — gestión de inventario, productos y pedidos — pero usando funciones independientes que operan sobre **diccionarios**. Ahora daremos el siguiente paso: **modelar el dominio con clases**, encapsulando datos y comportamiento en objetos.

Cada grupo se encargará de diseñar e implementar una clase concreta. Al final, juntaremos todas las piezas para tener un script orientado a objetos limpio y funcional.

---


### ¿Qué cambia con POO?

| Antes (funciones + diccionarios) | Después (clases + objetos) |
|---|---|
| `{"name": "Electronics", "description": "..."}` | `Category("Electronics", "...")` |
| `{"name": "On Sale"}` | `Tag("On Sale")` |
| `{"name": "Laptop", "sku": "SKU123", ...}` | `Product("Laptop", "SKU123", ...)` |
| `inventory = {sku: product_dict, ...}` | `inventory = Inventory()` con métodos propios |
| `{"order_id": "ORDER001", "items": {...}}` | `Order("ORDER001")` con métodos propios |
| `check_stock(product, units)` | `product.current_stock >= units` (dato accesible como atributo) |
| `update_stock(product, units)` | `product.update_stock(-units)` (método del propio objeto) |
| `show_inventory_report(inventory)` | `inventory.generate_inventory_report()` (método de la clase) |
| `process_orders(orders, inventory)` | `order.buy()` (cada pedido sabe procesarse a sí mismo) |

---

## 📐 Conceptos de POO que Vais a Aplicar

Antes de empezar, aseguraos de entender estos conceptos clave:

- **Clase**: Plantilla que define atributos (datos) y métodos (comportamiento) de un tipo de objeto.
- **`__init__`**: Constructor, inicializa los atributos del objeto al crearlo.
- **`__repr__`**: Representación en texto del objeto, útil para depuración (se invoca con `repr(obj)` o al mostrarlo en consola interactiva).
- **`__eq__` y `__hash__`**: Permiten comparar objetos por valor (no por referencia en memoria) y usarlos como claves de diccionarios o en conjuntos.
- **Encapsulación**: Cada objeto es responsable de sus propios datos y operaciones.

---

> 💡 **Consejo:** Cada grupo puede probar su clase de forma aislada con datos de prueba antes de la integración final. ¡Comunicaos entre grupos para asegurar que las piezas encajan!


---

## 👥 Asignación por Grupos

---

### 🟢 Grupo 1 — Clases `Category` y `Tag`

**Objetivo:** Crear dos clases que representen las entidades más sencillas del dominio: categorías y etiquetas de productos. Sustituyen los diccionarios `{"name": "...", "description": "..."}` y `{"name": "..."}`.

---

#### Clase `Category`

##### Definición de la clase

```python
class Category:
    def __init__(self, name: str, description: str = ""):
        ...

    def __eq__(self, other) -> bool:
        ...

    def __hash__(self) -> int:
        ...

    def __repr__(self) -> str:
        ...
```

##### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `name` | `str` | Nombre de la categoría (ej: `"Electronics"`). |
| `description` | `str` | Descripción de la categoría. Valor por defecto: cadena vacía `""`. |


##### Ejemplo de uso

```python
cat1 = Category("Electronics", "Devices and gadgets")
cat2 = Category("Electronics", "Different description")
cat3 = Category("Office")

print(cat1)            # Category(name='Electronics', description='Devices and gadgets')
print(cat1 == cat2)    # True  (mismo name)
print(cat1 == cat3)    # False (distinto name)
print(cat3.description)  # ""
```

---

#### Clase `Tag`

##### Definición de la clase

```python
class Tag:
    def __init__(self, name: str):
        ...

    def __eq__(self, other) -> bool:
        ...

    def __hash__(self) -> int:
        ...

    def __repr__(self) -> str:
        ...
```

##### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `name` | `str` | Nombre de la etiqueta (ej: `"On Sale"`, `"New Arrival"`, `"Best Seller"`). |

##### Ejemplo de uso

```python
tag1 = Tag("On Sale")
tag2 = Tag("On Sale")
tag3 = Tag("New Arrival")

print(tag1)           # Tag(name='On Sale')
print(tag1 == tag2)   # True
print(tag1 == tag3)   # False
```


---

### 🔵 Grupo 2 — Clase `Product`

**Objetivo:** Crear una clase que represente un producto del inventario, sustituyendo el diccionario de producto. Debe encapsular la lógica que antes estaba en las funciones `check_stock` y `update_stock`.

#### Definición de la clase

```python
class Product:
    def __init__(self, name: str, sku: str, price: float, current_stock: int = 0,
                 categories: list = None, tags: list = None):
        ...

    def check_stock(self, requested_units: int) -> tuple[bool, int]:
        ...

    def update_stock(self, amount: int) -> None:
        ...

    def get_info(self) -> str:
        ...

    def __repr__(self) -> str:
        ...
```

#### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `name` | `str` | Nombre del producto. |
| `sku` | `str` | Código único del producto. |
| `price` | `float` | Precio unitario. |
| `current_stock` | `int` | Unidades en stock. Valor por defecto: `0`. |
| `categories` | `list[Category]` | Lista de categorías del producto. Si se recibe `None`, se inicializa como lista vacía `[]`. |
| `tags` | `list[Tag]` | Lista de etiquetas del producto. Si se recibe `None`, se inicializa como lista vacía `[]`. |


#### Ejemplo de uso

```python
cat = Category("Electronics", "Devices and gadgets")
tag1 = Tag("New Arrival")
tag2 = Tag("Best Seller")

product = Product("Laptop", "SKU123", 1200, 10, categories=[cat], tags=[tag1, tag2])

product.check_stock(5)   # -> (True, 5)
product.check_stock(15)  # -> (False, 10)

product.update_stock(-3)
print(product.current_stock)  # -> 7

print(product.get_info())
# -> Product: Laptop (SKU: SKU123) - Price: $1200.00, Stock: 7, Categories: [Electronics], Tags: [New Arrival, Best Seller]
```

> **Nota:** Observad cómo `check_stock` ahora es un **método del producto** en vez de una función externa. El producto ya tiene acceso a su propio stock mediante `self`, por lo que no necesita recibirse a sí mismo como parámetro.

---

### 🟡 Grupo 3 — Clase `Inventory`

**Objetivo:** Crear una clase que gestione la colección de productos, sustituyendo el diccionario `inventory = {sku: product, ...}`. Debe encapsular la lógica que antes estaba en la función `show_inventory_report`.

#### Definición de la clase

```python
class Inventory:
    def __init__(self):
        ...

    def add_product(self, product: Product) -> None:
        ...

    def get_product(self, sku: str) -> Product | None:
        ...

    def generate_inventory_report(self) -> str:
        ...

    def __repr__(self) -> str:
        ...
```

#### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `products` | `dict[str, Product]` | Diccionario interno que almacena productos indexados por SKU. Se inicializa vacío. |

#### Ejemplo de uso

```python
inventory = Inventory()

p1 = Product("Laptop", "SKU123", 1200, 10)
p2 = Product("Mouse", "SKU456", 25, 100)

inventory.add_product(p1)
inventory.add_product(p2)

print(inventory.get_product("SKU123"))  # -> Product(name='Laptop', sku='SKU123', price=1200, current_stock=10)
print(inventory.get_product("SKU999"))  # -> None

print(inventory.generate_inventory_report())
# -> Product: Laptop (SKU: SKU123) - Price: $1200.00, Stock: 10, Categories: [None], Tags: [None]
#    Product: Mouse (SKU: SKU456) - Price: $25.00, Stock: 100, Categories: [None], Tags: [None]

print(inventory)  # -> Inventory(2 products)
```

---

### 🟠 Grupo 4 — Clase `Order`

**Objetivo:** Crear una clase que encapsule la lógica de un pedido, sustituyendo el diccionario `{"order_id": "...", "items": {...}}`. Debe absorber la lógica que antes estaba en la función `process_orders`, pero a nivel de un pedido individual. Se debe apoyar en los métodos de `Product` (Grupo 2) para comprobar y actualizar el stock.

#### Definición de la clase

```python
class Order:
    def __init__(self, order_id: str):
        ...

    def add_product(self, product: Product, quantity: int) -> None:
        ...

    def buy(self) -> str:
        ...

    def __repr__(self) -> str:
        ...
```

#### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `order_id` | `str` | Identificador único del pedido (ej: `"ORDER001"`). |
| `products` | `dict` | Diccionario que almacena los ítems del pedido. La clave es el `sku` (str) y el valor es un diccionario `{'product': Product, 'quantity': int}`. Se inicializa vacío. |

#### Ejemplo de uso

```python
p1 = Product("Laptop", "SKU123", 1200, 10)
p2 = Product("Mouse", "SKU456", 25, 100)

order = Order("ORDER001")
order.add_product(p1, 2)
order.add_product(p2, 5)

print(order.buy())
# -> Order ID: ORDER001 - Total: $2525.00 - Purchase Completed

print(p1.current_stock)  # -> 8
print(p2.current_stock)  # -> 95
```

---

### 🔴 Grupo 5 — Script Principal (Integración)

**Objetivo:** Escribir el script principal que use **todas las clases de los otros grupos** para replicar exactamente el mismo comportamiento que `with_methods.py`.

#### Lo que debéis hacer

1. **Crear las categorías** como objetos `Category`.
2. **Crear las etiquetas** como objetos `Tag`.
3. **Crear los productos** como objetos `Product`, asignándoles categorías y etiquetas.
4. **Crear el inventario** como objeto `Inventory` y añadir los productos.
5. **Crear los pedidos** como objetos `Order` y añadir los productos a cada uno.
6. **Procesar los pedidos** llamando a `order.buy()` e imprimiendo el resultado.
7. **Mostrar el informe de inventario** llamando a `inventory.generate_inventory_report()`.
