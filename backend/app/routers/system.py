from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..config import settings
from ..db import DbSession

router = APIRouter(tags=["system"])


@router.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness: the process is up. Deliberately does not touch the database."""
    return {"status": "UP"}


@router.get("/ready")
def ready(db: DbSession):
    """Readiness: only take traffic when the database is reachable."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "NOT_READY", "reason": "database unavailable"},
        )
    return {"status": "READY"}


@router.get("/api/info")
def info() -> dict[str, str]:
    return {"service": settings.app_name, "version": settings.app_version}
