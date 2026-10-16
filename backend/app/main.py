import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .config import settings
from .metrics import register_inventory_metrics
from .routers import movements, products, stats, system

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Inventory management API for the StockPilot DevOps capstone.",
)

for router in (system.router, products.router, movements.router, stats.router):
    app.include_router(router)

# Database schema is managed by Alembic (run as a separate step), never created here.
Instrumentator(excluded_handlers=["/metrics", "/health", "/ready"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)
register_inventory_metrics()
