from fastapi import APIRouter

from ..db import DbSession
from ..inventory import summarise
from ..schemas import StatsOut

router = APIRouter(tags=["stats"])


@router.get("/api/stats", response_model=StatsOut)
def inventory_stats(db: DbSession) -> StatsOut:
    return StatsOut(**summarise(db))
