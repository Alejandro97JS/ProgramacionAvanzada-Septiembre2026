# 🔧 Ejercicio por Grupos: De Programación Imperativa a Modular

## 📋 Descripción General

En este ejercicio vamos a **refactorizar** el script `imperative_programming.py` para transformarlo de un enfoque puramente imperativo a uno **modular basado en funciones**.

El script original gestiona un pequeño sistema de inventario con categorías, etiquetas, productos y pedidos. Todo el código está escrito de forma secuencial, sin funciones. Vuestro objetivo será **dividir la lógica en métodos reutilizables** que mantengan exactamente el mismo comportamiento funcional.

Cada grupo se encargará de implementar una parte concreta. Al final, juntaremos todas las piezas para tener un script limpio y modular.

---

## 📦 Estructuras de Datos de Referencia

Antes de empezar, revisad las estructuras de datos que maneja el script original para entender los tipos de parámetros que recibirán vuestras funciones:

### Categoría (diccionario)

```python
{"name": "Electronics", "description": "Devices and gadgets"}
```

### Etiqueta / Tag (diccionario)

```python
{"name": "On Sale"}
```

### Producto (diccionario)

```python
{
    "name": "Laptop",
    "sku": "SKU123",
    "price": 1200,
    "current_stock": 10,
    "categories": [{"name": "Electronics", "description": "Devices and gadgets"}],
    "tags": [{"name": "New Arrival"}, {"name": "Best Seller"}]
}
```

### Inventario (diccionario de productos indexado por SKU)

```python
{
    "SKU123": {"name": "Laptop", "sku": "SKU123", "price": 1200, "current_stock": 10, "categories": [...], "tags": [...]},
    "SKU456": {"name": "Mouse", "sku": "SKU456", "price": 25, "current_stock": 100, "categories": [...], "tags": [...]},
    ...
}
```

### Pedido (diccionario)

```python
{"order_id": "ORDER001", "items": {"SKU123": 2, "SKU456": 5}}
```

> `items` es un diccionario donde la **clave** es el SKU del producto y el **valor** es la cantidad solicitada.

### Lista de pedidos

```python
[
    {"order_id": "ORDER001", "items": {"SKU123": 2, "SKU456": 5}},
    {"order_id": "ORDER002", "items": {"SKU789": 3, "SKU101": 1}},
    ...
]
```

---

> 💡 **Consejo:** Cada grupo puede probar su función de forma aislada con datos de prueba antes de la integración final.


---

## 👥 Asignación por Grupos

---

### 🟢 Grupo 1 — Comprobación de Stock

**Objetivo:** Crear un método que compruebe si un producto tiene suficiente stock para satisfacer una cantidad solicitada.

#### Firma del método

```python
def check_stock(product: dict, requested_units: int) -> tuple[bool, int]:
```

#### Parámetros

| Parámetro | Tipo | Descripción |
|---|---|---|
| `product` | `dict` | Diccionario del producto (ver estructura de referencia arriba). |
| `requested_units` | `int` | Número de unidades que el cliente quiere comprar. |

#### Valor de retorno

Devuelve una **tupla** `(has_enough_stock, units_to_provide)`:

| Campo | Tipo | Descripción |
|---|---|---|
| `has_enough_stock` | `bool` | `True` si el stock actual del producto es **mayor o igual** que las unidades solicitadas. `False` en caso contrario. |
| `units_to_provide` | `int` | Si `has_enough_stock` es `True`, será igual a `requested_units`. Si es `False`, será el stock actual del producto (`current_stock`), es decir, el máximo que se le puede proporcionar al cliente. |

#### Ejemplo de uso

```python
product = {"name": "Mouse", "sku": "SKU456", "price": 25, "current_stock": 100, "categories": [...], "tags": [...]}

check_stock(product, 50)   # -> (True, 50)
check_stock(product, 100)  # -> (True, 100)
check_stock(product, 150)  # -> (False, 100)
```

---

### 🔵 Grupo 2 — Actualización de Stock

**Objetivo:** Crear un método que actualice el stock de un producto tras una venta, restando las unidades vendidas.

#### Firma del método

```python
def update_stock(product: dict, sold_units: int) -> dict:
```

#### Parámetros

| Parámetro | Tipo | Descripción |
|---|---|---|
| `product` | `dict` | Diccionario del producto (ver estructura de referencia arriba). |
| `sold_units` | `int` | Número de unidades vendidas que se deben descontar del stock. |

#### Valor de retorno

| Tipo | Descripción |
|---|---|
| `dict` | El mismo diccionario del producto con el campo `current_stock` actualizado (restando las `sold_units`). |

#### Ejemplo de uso

```python
product = {"name": "Mouse", "sku": "SKU456", "price": 25, "current_stock": 100, "categories": [...], "tags": [...]}

updated = update_stock(product, 30)
print(updated["current_stock"])  # -> 70
```

---

### 🟡 Grupo 3 — Informe de Inventario

**Objetivo:** Crear un método que reciba el inventario completo y lo muestre por pantalla de forma ordenada y legible.

#### Firma del método

```python
def show_inventory_report(inventory: dict) -> None:
```

#### Parámetros

| Parámetro | Tipo | Descripción |
|---|---|---|
| `inventory` | `dict` | Diccionario de inventario indexado por SKU (ver estructura de referencia arriba). |

#### Valor de retorno

No devuelve nada (`None`). Imprime directamente por pantalla.

#### Formato de salida esperado

La salida debe ser similar a la del script original:

```
Inventory Report:

Product: Laptop (SKU: SKU123) - Price: $1200.00, Stock: 8, Categories: [Electronics], Tags: [New Arrival, Best Seller]
Product: Mouse (SKU: SKU456) - Price: $25.00, Stock: 85, Categories: [Electronics], Tags: [On Sale]
Product: Keyboard (SKU: SKU789) - Price: $50.00, Stock: 47, Categories: [Office], Tags: [Best Seller]
Product: Monitor (SKU: SKU101) - Price: $300.00, Stock: 17, Categories: [Electronics], Tags: [None]
```

> **Nota:** Si un producto no tiene categorías o etiquetas, se debe mostrar `None` en su lugar.

---

### 🟠 Grupo 4 — Procesamiento de Pedidos

**Objetivo:** Crear un método que procese una lista de pedidos, actualizando el inventario y mostrando el resultado de cada pedido por pantalla. Debe **apoyarse en las funciones de los otros grupos** cuando las necesite.

#### Firma del método

```python
def process_orders(orders: list[dict], inventory: dict) -> None:
```

#### Parámetros

| Parámetro | Tipo | Descripción |
|---|---|---|
| `orders` | `list[dict]` | Lista de pedidos (ver estructura de referencia arriba). |
| `inventory` | `dict` | Diccionario de inventario indexado por SKU. |

#### Valor de retorno

No devuelve nada (`None`). Imprime el resultado de cada pedido por pantalla.

#### Comportamiento esperado

Para cada pedido de la lista:

1. **Recorrer** los ítems del pedido (`sku` y `quantity`).
2. **Buscar** el producto en el inventario por su SKU. Si no existe, imprimir un error y continuar con el siguiente ítem.
3. **Comprobar el stock**.
   - Si **no hay stock suficiente**: imprimir un mensaje de error indicando el stock disponible y las unidades solicitadas. **No incluir ninguna unidad** de ese producto en el pedido (decisión de negocio).
   - Si **hay stock suficiente**: continuar.
4. **Actualizar el stock** que quedaría del producto.
5. **Acumular el total** del pedido (`precio × cantidad` para cada ítem procesado correctamente).
6. **Imprimir** el resultado del pedido con el formato:
   ```
   Order ID: ORDER001 - Total: $2525.00 - Purchase Completed
   ```

#### Ejemplo de mensajes de error

```
Error: Product with SKU SKUXXX not found.
Error: Insufficient stock for Mouse. Available: 100, Requested: 150
```

---

### 🔴 Grupo 5 — Script Principal (Integración)

**Objetivo:** Reescribir el script `imperative_programming.py` completo utilizando las funciones creadas por los demás grupos. El **comportamiento funcional debe ser idéntico** al del script original, pero el código debe estar refactorizado usando funciones.

#### Lo que debéis hacer

1. Mantener la **definición de datos** tal cual está en el script original (categorías, etiquetas, productos, inventario y pedidos).
2. Refactorizar el **bucle de procesamiento de pedidos**, de forma que quede un código más legible y limpio.
3. Reemplazar el **bloque de impresión del informe de inventario**, de forma que quede un código más legible y limpio.
4. La **salida del programa** debería ser la misma que la del script original.
