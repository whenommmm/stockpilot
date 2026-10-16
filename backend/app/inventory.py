"""Stock-status rules shared by the API responses, list filters, stats and metrics."""

from typing import Literal

from sqlalchemy import ColumnElement, and_, case, func, select
from sqlalchemy.orm import Session

from .models import Product

StockStatus = Literal["IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"]


def stock_status(quantity: int, reorder_level: int) -> StockStatus:
    if quantity == 0:
        return "OUT_OF_STOCK"
    if quantity <= reorder_level:
        return "LOW_STOCK"
    return "IN_STOCK"


def status_condition(status: StockStatus) -> ColumnElement[bool]:
    """The SQL equivalent of stock_status(), for filtering and counting in the database."""
    if status == "OUT_OF_STOCK":
        return Product.quantity == 0
    if status == "LOW_STOCK":
        return and_(Product.quantity > 0, Product.quantity <= Product.reorder_level)
    return Product.quantity > Product.reorder_level


def _count_where(condition: ColumnElement[bool]):
    return func.coalesce(func.sum(case((condition, 1), else_=0)), 0)


def summarise(db: Session) -> dict[str, int | float]:
    row = db.execute(
        select(
            func.count(Product.id),
            func.coalesce(func.sum(Product.quantity), 0),
            _count_where(status_condition("LOW_STOCK")),
            _count_where(status_condition("OUT_OF_STOCK")),
            func.coalesce(func.sum(Product.quantity * Product.unit_price), 0),
        )
    ).one()
    total_products, total_units, low_stock, out_of_stock, inventory_value = row
    return {
        "total_products": int(total_products),
        "total_units": int(total_units),
        "low_stock": int(low_stock),
        "out_of_stock": int(out_of_stock),
        "inventory_value": round(float(inventory_value), 2),
    }
