from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import DbSession
from ..inventory import StockStatus, status_condition
from ..metrics import record_adjustment
from ..models import Product, StockMovement
from ..schemas import Category, ProductCreate, ProductOut, ProductUpdate, StockAdjustment

router = APIRouter(prefix="/api/products", tags=["products"])


def _get_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product


def _duplicate_sku(sku: str) -> HTTPException:
    return HTTPException(status.HTTP_409_CONFLICT, f"A product with SKU {sku} already exists")


@router.get("", response_model=list[ProductOut])
def list_products(
    db: DbSession,
    q: Annotated[str | None, Query(max_length=100, description="Search name or SKU")] = None,
    category: Category | None = None,
    status_filter: Annotated[StockStatus | None, Query(alias="status")] = None,
):
    query = select(Product).order_by(Product.sku)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
    if category:
        query = query.where(Product.category == category)
    if status_filter:
        query = query.where(status_condition(status_filter))
    return db.scalars(query).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: DbSession):
    return _get_or_404(db, product_id)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: DbSession):
    if db.scalar(select(Product.id).where(Product.sku == payload.sku)) is not None:
        raise _duplicate_sku(payload.sku)
    product = Product(**payload.model_dump())
    if product.quantity > 0:
        product.movements.append(
            StockMovement(change=product.quantity, reason="RESTOCK", note="Initial stock")
        )
    db.add(product)
    try:
        db.commit()
    except IntegrityError:  # another request created the same SKU in the meantime
        db.rollback()
        raise _duplicate_sku(payload.sku) from None
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: DbSession):
    product = _get_or_404(db, product_id)
    for field, value in payload.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: DbSession) -> None:
    db.delete(_get_or_404(db, product_id))
    db.commit()


@router.post("/{product_id}/adjust", response_model=ProductOut)
def adjust_stock(product_id: int, payload: StockAdjustment, db: DbSession):
    # Row lock (PostgreSQL) so two replicas can't both sell the last unit.
    product = db.scalar(select(Product).where(Product.id == product_id).with_for_update())
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    new_quantity = product.quantity + payload.change
    if new_quantity < 0:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"Insufficient stock: only {product.quantity} units of {product.sku} available",
        )
    product.quantity = new_quantity
    db.add(
        StockMovement(
            product_id=product.id,
            change=payload.change,
            reason=payload.reason,
            note=payload.note,
        )
    )
    db.commit()
    db.refresh(product)
    record_adjustment(payload.reason, payload.change)
    return product
