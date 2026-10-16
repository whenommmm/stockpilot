from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..db import DbSession
from ..models import StockMovement
from ..schemas import MovementOut

router = APIRouter(prefix="/api/movements", tags=["stock movements"])


@router.get("", response_model=list[MovementOut])
def recent_movements(db: DbSession, limit: Annotated[int, Query(ge=1, le=100)] = 20):
    query = (
        select(StockMovement)
        .options(joinedload(StockMovement.product))
        .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
        .limit(limit)
    )
    return db.scalars(query).all()
