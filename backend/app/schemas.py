from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from .inventory import StockStatus, stock_status

Category = Literal["ELECTRONICS", "GROCERY", "APPAREL", "HOME", "OFFICE", "OTHER"]
Reason = Literal["RESTOCK", "SALE", "ADJUSTMENT"]

MAX_UNITS = 1_000_000


class ProductFields(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: Category = "OTHER"
    unit_price: float = Field(default=0, ge=0, le=10_000_000)
    reorder_level: int = Field(default=10, ge=0, le=MAX_UNITS)
    supplier: str = Field(default="", max_length=120)


class ProductCreate(ProductFields):
    sku: str = Field(min_length=2, max_length=40, pattern=r"^[A-Z0-9][A-Z0-9-]*$")
    quantity: int = Field(default=0, ge=0, le=MAX_UNITS)

    @field_validator("sku", mode="before")
    @classmethod
    def normalise_sku(cls, value: object) -> object:
        return value.strip().upper() if isinstance(value, str) else value


class ProductUpdate(BaseModel):
    """Partial update. SKU is the product's identity and quantity changes go through /adjust."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: Category | None = None
    unit_price: float | None = Field(default=None, ge=0, le=10_000_000)
    reorder_level: int | None = Field(default=None, ge=0, le=MAX_UNITS)
    supplier: str | None = Field(default=None, max_length=120)


class ProductOut(ProductFields):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    quantity: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def status(self) -> StockStatus:
        return stock_status(self.quantity, self.reorder_level)


class StockAdjustment(BaseModel):
    change: int = Field(ge=-MAX_UNITS, le=MAX_UNITS)
    reason: Reason
    note: str = Field(default="", max_length=200)

    @model_validator(mode="after")
    def direction_matches_reason(self) -> Self:
        if self.change == 0:
            raise ValueError("change must not be zero")
        if self.reason == "RESTOCK" and self.change < 0:
            raise ValueError("a RESTOCK must add stock (positive change)")
        if self.reason == "SALE" and self.change > 0:
            raise ValueError("a SALE must remove stock (negative change)")
        return self


class MovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_sku: str
    product_name: str
    change: int
    reason: Reason
    note: str
    created_at: datetime


class StatsOut(BaseModel):
    total_products: int
    total_units: int
    low_stock: int
    out_of_stock: int
    inventory_value: float
