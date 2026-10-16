"""Load demo inventory into an empty database.

Usage: python -m app.seed   (does nothing if any product already exists)
"""

from sqlalchemy import func, select

from .db import SessionLocal
from .models import Product, StockMovement

# sku, name, category, quantity, unit price (INR), reorder level, supplier
DEMO_PRODUCTS = [
    ("ELEC-1001", "Wireless Mouse", "ELECTRONICS", 48, 899.00, 15, "Nexa Distributors"),
    ("ELEC-1002", "Mechanical Keyboard", "ELECTRONICS", 12, 3499.00, 10, "Nexa Distributors"),
    ("ELEC-1003", "27-inch Monitor", "ELECTRONICS", 6, 15999.00, 5, "Vision Displays"),
    ("ELEC-1004", "USB-C Hub", "ELECTRONICS", 0, 1899.00, 8, "Nexa Distributors"),
    ("OFF-2001", "A4 Copier Paper (500)", "OFFICE", 120, 349.00, 40, "PaperTrail Co."),
    ("OFF-2002", "Gel Pens (Pack of 10)", "OFFICE", 25, 199.00, 30, "PaperTrail Co."),
    ("OFF-2003", "Ergonomic Office Chair", "OFFICE", 9, 8999.00, 4, "SitWell Furniture"),
    ("GROC-3001", "Arabica Coffee Beans 1kg", "GROCERY", 34, 1299.00, 12, "Bean Route"),
    ("GROC-3002", "Green Tea (100 bags)", "GROCERY", 7, 449.00, 10, "Leaf & Co."),
    ("APP-4001", "Company Hoodie (M)", "APPAREL", 40, 1199.00, 10, "ThreadWorks"),
    ("APP-4002", "Company Hoodie (L)", "APPAREL", 0, 1199.00, 10, "ThreadWorks"),
    ("HOME-5001", "LED Desk Lamp", "HOME", 18, 1499.00, 6, "Bright Living"),
]

# sku, change, note — a little history so the activity feed isn't empty
DEMO_SALES = [
    ("ELEC-1001", -6, "Order #1042"),
    ("OFF-2002", -10, "Team restock request"),
    ("GROC-3001", -4, "Pantry refill"),
    ("ELEC-1003", -2, "Order #1047"),
]


def seed() -> int:
    with SessionLocal() as db:
        if db.scalar(select(func.count(Product.id))):
            return 0
        products = {}
        for sku, name, category, quantity, price, reorder, supplier in DEMO_PRODUCTS:
            product = Product(
                sku=sku,
                name=name,
                category=category,
                quantity=quantity,
                unit_price=price,
                reorder_level=reorder,
                supplier=supplier,
            )
            if quantity:
                product.movements.append(
                    StockMovement(change=quantity, reason="RESTOCK", note="Opening stock")
                )
            products[sku] = product
            db.add(product)
        db.flush()
        for sku, change, note in DEMO_SALES:
            products[sku].quantity += change
            db.add(
                StockMovement(product_id=products[sku].id, change=change, reason="SALE", note=note)
            )
        db.commit()
        return len(DEMO_PRODUCTS)


if __name__ == "__main__":
    created = seed()
    print(f"Seeded {created} demo products." if created else "Database already has data; skipped.")
