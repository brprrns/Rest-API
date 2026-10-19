from unittest.mock import patch

from pynamodb.exceptions import DoesNotExist

from app.models.product import Product

VALID = {"product_name": "Northwind Traders Chai", "list_price": 18.0, "category": "Beverages"}


def test_create_product(client):
    with patch.object(Product, "save") as save:
        resp = client.post("/products", json=VALID)
    assert resp.status_code == 201
    assert resp.get_json()["list_price"] == 18.0
    save.assert_called_once()


def test_create_product_negative_price(client):
    resp = client.post("/products", json={**VALID, "list_price": -5})
    assert resp.status_code == 400
    assert "list_price" in resp.get_json()["details"]


def test_create_product_missing_name(client):
    resp = client.post("/products", json={"list_price": 5})
    assert resp.status_code == 400


def test_create_product_wrong_type(client):
    resp = client.post("/products", json={**VALID, "list_price": "cheap"})
    assert resp.status_code == 400


def test_get_product(client):
    with patch.object(Product, "get", return_value=Product(id="7", product_name="Tea", list_price=3)):
        resp = client.get("/products/7")
    assert resp.status_code == 200 and resp.get_json()["product_name"] == "Tea"


def test_get_product_not_found(client):
    with patch.object(Product, "get", side_effect=DoesNotExist()):
        assert client.get("/products/7").status_code == 404


def test_update_product_price(client):
    product = Product(id="7", product_name="Tea", list_price=3)
    with patch.object(Product, "get", return_value=product), patch.object(Product, "save"):
        resp = client.patch("/products/7", json={"list_price": 4.5})
    assert resp.status_code == 200 and resp.get_json()["list_price"] == 4.5


def test_list_products(client):
    from tests.helpers import FakeResults
    rows = [Product(id="1", product_name="Tea", list_price=3)]
    with patch.object(Product, "scan", return_value=FakeResults(rows)):
        resp = client.get("/products")
    assert resp.status_code == 200 and resp.get_json()["next_token"] is None


def test_update_product_empty_body(client):
    assert client.put("/products/1", json={}).status_code == 400
