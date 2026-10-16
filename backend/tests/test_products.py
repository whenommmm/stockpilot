def test_create_product_returns_201_with_computed_status(client):
    response = client.post(
        "/api/products",
        json={"sku": "home-0042", "name": "Desk Lamp", "category": "HOME", "quantity": 40},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["sku"] == "HOME-0042"  # normalised to upper case
    assert body["status"] == "IN_STOCK"
    assert body["reorder_level"] == 10


def test_create_product_rejects_duplicate_sku(client, make_product):
    make_product(sku="ELEC-0001")

    response = client.post("/api/products", json={"sku": "elec-0001", "name": "Duplicate"})

    assert response.status_code == 409
    assert "ELEC-0001" in response.json()["detail"]


def test_create_product_validates_payload(client):
    response = client.post(
        "/api/products",
        json={"sku": "BAD SKU!", "name": "", "unit_price": -1, "category": "WEAPONS"},
    )

    assert response.status_code == 422
    invalid_fields = {error["loc"][-1] for error in response.json()["detail"]}
    assert {"sku", "name", "unit_price", "category"} <= invalid_fields


def test_get_product_by_id(client, make_product):
    product = make_product()

    response = client.get(f"/api/products/{product['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "USB-C Charging Cable"


def test_get_missing_product_returns_404(client):
    response = client.get("/api/products/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_list_products_filters_by_search_category_and_status(client, make_product):
    make_product(sku="ELEC-0001", name="USB-C Cable", category="ELECTRONICS", quantity=50)
    make_product(sku="ELEC-0002", name="HDMI Cable", category="ELECTRONICS", quantity=3)
    make_product(sku="OFF-0001", name="A4 Paper", category="OFFICE", quantity=0)

    def skus(**params):
        return [p["sku"] for p in client.get("/api/products", params=params).json()]

    assert skus() == ["ELEC-0001", "ELEC-0002", "OFF-0001"]
    assert skus(q="cable") == ["ELEC-0001", "ELEC-0002"]
    assert skus(q="off-00") == ["OFF-0001"]
    assert skus(category="OFFICE") == ["OFF-0001"]
    assert skus(status="LOW_STOCK") == ["ELEC-0002"]
    assert skus(status="OUT_OF_STOCK") == ["OFF-0001"]
    assert skus(status="IN_STOCK", category="ELECTRONICS") == ["ELEC-0001"]


def test_update_product_changes_only_sent_fields(client, make_product):
    product = make_product()

    response = client.put(
        f"/api/products/{product['id']}", json={"unit_price": 12.25, "reorder_level": 30}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["unit_price"] == 12.25
    assert body["reorder_level"] == 30
    assert body["name"] == product["name"]
    assert body["status"] == "LOW_STOCK"  # 25 units is now below the reorder level of 30


def test_update_cannot_change_quantity_directly(client, make_product):
    product = make_product()

    response = client.put(f"/api/products/{product['id']}", json={"quantity": 999})

    assert response.status_code == 422
    assert client.get(f"/api/products/{product['id']}").json()["quantity"] == 25


def test_update_missing_product_returns_404(client):
    response = client.put("/api/products/9999", json={"name": "Ghost"})

    assert response.status_code == 404


def test_delete_product_returns_204_then_404(client, make_product):
    product = make_product()

    assert client.delete(f"/api/products/{product['id']}").status_code == 204
    assert client.get(f"/api/products/{product['id']}").status_code == 404
    assert client.delete(f"/api/products/{product['id']}").status_code == 404
