import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator, metrics

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

# Per-endpoint latency buckets fine enough for a meaningful p95 (the default is 0.1/0.5/1 s).
LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5)

# Probes and scrapes are excluded so they don't drown out real traffic in the dashboards.
(
    Instrumentator(excluded_handlers=["/metrics", "/health", "/ready"])
    .add(metrics.default(latency_lowr_buckets=LATENCY_BUCKETS))
    .instrument(app)
    .expose(app, endpoint="/metrics", include_in_schema=False)
)
register_inventory_metrics()

# Note: the database schema is managed by Alembic (run as a separate step), never created here.
