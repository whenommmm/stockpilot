def test_health_reports_up(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_the_database(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_info_reports_service_name_and_version(client):
    body = client.get("/api/info").json()

    assert body["service"] == "StockPilot API"
    assert body["version"]


def test_metrics_exposes_http_and_inventory_metrics(client, make_product):
    make_product(sku="OUT-1", quantity=0)
    make_product(sku="LOW-1", quantity=5)
    client.get("/api/products")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "stockpilot_out_of_stock_products 1.0" in response.text
    assert "stockpilot_low_stock_products 1.0" in response.text
    for reason in ("RESTOCK", "SALE", "ADJUSTMENT"):  # exported before any adjustment happens
        assert f'stockpilot_units_moved_total{{reason="{reason}"}}' in response.text
