def generate_inventory_report(inventory: dict[str, Product]) -> str:
    report = []

    for product in inventory.values():
        report.append(
            f"Product: {product.name} "
            f"(SKU: {product.sku}) - "
            f"Price: ${product.price:.2f}, "
            f"Stock: {product.current_stock}, "
            f"Categories: [{product.category}], "
            f"Tags: [{product.tags}]"
        )

    return "\n".join(report)

