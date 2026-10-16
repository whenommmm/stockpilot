def adjust(client, product_id, change, reason, note=""):
    return client.post(
        f"/api/products/{product_id}/adjust",
        json={"change": change, "reason": reason, "note": note},
    )


def test_creating_a_product_with_stock_records_an_initial_movement(client, make_product):
    product = make_product(quantity=25)

    movements = client.get("/api/movements").json()

    assert len(movements) == 1
    assert movements[0]["product_id"] == product["id"]
    assert movements[0]["product_sku"] == "ELEC-0001"
    assert movements[0]["change"] == 25
    assert movements[0]["reason"] == "RESTOCK"


def test_restock_increases_quantity(client, make_product):
    product = make_product(quantity=5)

    response = adjust(client, product["id"], 20, "RESTOCK", "Weekly delivery")

    assert response.status_code == 200
    assert response.json()["quantity"] == 25
    assert response.json()["status"] == "IN_STOCK"


def test_sale_decreases_quantity_and_can_reach_out_of_stock(client, make_product):
    product = make_product(quantity=4)

    response = adjust(client, product["id"], -4, "SALE")

    assert response.status_code == 200
    assert response.json()["quantity"] == 0
    assert response.json()["status"] == "OUT_OF_STOCK"


def test_sale_cannot_take_stock_below_zero(client, make_product):
    product = make_product(quantity=3)

    response = adjust(client, product["id"], -5, "SALE")

    assert response.status_code == 422
    assert "only 3" in response.json()["detail"]
    assert client.get(f"/api/products/{product['id']}").json()["quantity"] == 3


def test_adjustment_direction_must_match_reason(client, make_product):
    product = make_product()

    assert adjust(client, product["id"], -1, "RESTOCK").status_code == 422
    assert adjust(client, product["id"], 1, "SALE").status_code == 422
    assert adjust(client, product["id"], 0, "ADJUSTMENT").status_code == 422
    assert adjust(client, product["id"], -2, "ADJUSTMENT").status_code == 200


def test_adjusting_a_missing_product_returns_404(client):
    assert adjust(client, 9999, 5, "RESTOCK").status_code == 404


def test_low_stock_when_quantity_reaches_reorder_level(client, make_product):
    product = make_product(quantity=12, reorder_level=10)

    response = adjust(client, product["id"], -2, "SALE")

    assert response.json()["status"] == "LOW_STOCK"


def test_movements_feed_is_newest_first_and_respects_limit(client, make_product):
    product = make_product(quantity=10)
    adjust(client, product["id"], -1, "SALE", "first sale")
    adjust(client, product["id"], -2, "SALE", "second sale")

    movements = client.get("/api/movements", params={"limit": 2}).json()

    assert [m["note"] for m in movements] == ["second sale", "first sale"]


def test_deleting_a_product_removes_its_movements(client, make_product):
    product = make_product(quantity=10)
    adjust(client, product["id"], -1, "SALE")

    client.delete(f"/api/products/{product['id']}")

    assert client.get("/api/movements").json() == []


def test_stats_summarise_the_inventory(client, make_product):
    make_product(sku="A-1", quantity=50, unit_price=2.0, reorder_level=10)  # in stock, value 100
    make_product(sku="A-2", quantity=5, unit_price=10.0, reorder_level=10)  # low, value 50
    make_product(sku="A-3", quantity=0, unit_price=99.0, reorder_level=10)  # out, value 0

    stats = client.get("/api/stats").json()

    assert stats == {
        "total_products": 3,
        "total_units": 55,
        "low_stock": 1,
        "out_of_stock": 1,
        "inventory_value": 150.0,
    }


def test_stats_on_an_empty_inventory(client):
    assert client.get("/api/stats").json() == {
        "total_products": 0,
        "total_units": 0,
        "low_stock": 0,
        "out_of_stock": 0,
        "inventory_value": 0.0,
    }
