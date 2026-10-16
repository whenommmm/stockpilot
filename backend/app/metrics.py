"""Custom Prometheus metrics, on top of the HTTP metrics from prometheus-fastapi-instrumentator."""

import logging
from collections.abc import Iterator
from typing import get_args

from prometheus_client import REGISTRY, Counter
from prometheus_client.core import GaugeMetricFamily, Metric
from prometheus_client.registry import Collector
from sqlalchemy.exc import SQLAlchemyError

from .db import SessionLocal
from .inventory import summarise
from .schemas import Reason

logger = logging.getLogger(__name__)

STOCK_ADJUSTMENTS = Counter(
    "stockpilot_stock_adjustments_total", "Stock adjustments recorded, by reason", ["reason"]
)
UNITS_MOVED = Counter(
    "stockpilot_units_moved_total", "Units moved in or out of stock, by reason", ["reason"]
)

# Export every reason at 0 from start-up, so dashboards and rate() see a series before the
# first adjustment instead of "No data".
for _reason in get_args(Reason):
    STOCK_ADJUSTMENTS.labels(reason=_reason)
    UNITS_MOVED.labels(reason=_reason)


def record_adjustment(reason: str, change: int) -> None:
    STOCK_ADJUSTMENTS.labels(reason=reason).inc()
    UNITS_MOVED.labels(reason=reason).inc(abs(change))


class InventoryCollector(Collector):
    """Reads inventory gauges from the database at scrape time.

    Every replica therefore reports the same numbers; dashboards should use max() across pods.
    """

    def describe(self) -> list[Metric]:
        # Returning nothing stops the registry calling collect() (a DB query) at registration.
        return []

    def collect(self) -> Iterator[Metric]:
        try:
            with SessionLocal() as db:
                summary = summarise(db)
        except SQLAlchemyError as exc:
            # One line per scrape, not a stack trace: Prometheus scrapes every 15 seconds.
            logger.warning("Inventory metrics skipped, DB unavailable: %s", type(exc).__name__)
            return
        gauges = {
            "stockpilot_products": ("Products in the catalogue", "total_products"),
            "stockpilot_low_stock_products": ("Products at or below reorder level", "low_stock"),
            "stockpilot_out_of_stock_products": ("Products with zero stock", "out_of_stock"),
            "stockpilot_inventory_value": ("Stock value (qty x unit price)", "inventory_value"),
        }
        for name, (documentation, key) in gauges.items():
            yield GaugeMetricFamily(name, documentation, value=summary[key])


def register_inventory_metrics() -> None:
    REGISTRY.register(InventoryCollector())
