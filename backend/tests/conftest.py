"""Test fixtures.

Every test gets a freshly created schema in a throwaway SQLite database, so tests never touch
the real PostgreSQL database. Set TEST_DATABASE_URL to run the same suite against PostgreSQL.
"""

import os
import tempfile
from pathlib import Path

_TEST_DB_DIR = tempfile.mkdtemp(prefix="stockpilot-tests-")
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", f"sqlite:///{Path(_TEST_DB_DIR) / 'test.db'}"
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

DEFAULT_PRODUCT = {
    "sku": "ELEC-0001",
    "name": "USB-C Charging Cable",
    "category": "ELECTRONICS",
    "quantity": 25,
    "unit_price": 9.5,
    "reorder_level": 10,
    "supplier": "Acme Supplies",
}


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def make_product(client):
    def _make(**overrides):
        response = client.post("/api/products", json={**DEFAULT_PRODUCT, **overrides})
        assert response.status_code == 201, response.text
        return response.json()

    return _make
