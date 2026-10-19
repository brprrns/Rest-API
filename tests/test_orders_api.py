from unittest.mock import patch

from pynamodb.exceptions import DoesNotExist

from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from tests.helpers import FakeResults

CUSTOMER = Customer(id="c1", company="Company A")
PRODUCT = Product(id="p1", product_name="Chai", list_price=10, discontinued=0)
NEW_ORDER = {"customer_id": "c1", "items": [{"product_id": "p1", "quantity": 3, "discount": 0.1}]}


def _order(**kw):
    base = dict(id="o1", customer_id="c1", order_date="2006-03-24T00:00:00", status="New",
                total_amount=27, shipping_fee=0,
                items=[OrderItem(product_id="p1", product_name="Chai", quantity=3, unit_price=10, discount=0.1)])
    base.update(kw)
    return Order(**base)


def test_create_order_calculates_total_on_server(client):
    with patch.object(Customer, "get", return_value=CUSTOMER), \
            patch.object(Product, "get", return_value=PRODUCT), \
            patch.object(Order, "save") as save:
        resp = client.post("/orders", json=NEW_ORDER)
    body = resp.get_json()
    assert resp.status_code == 201
    assert body["total_amount"] == 27.0          # 3 * 10 * (1 - 0.1)
    assert body["status"] == "New"
    assert body["items"][0]["unit_price"] == 10  # copied from product, not from client
    save.assert_called_once()


def test_create_order_unknown_customer(client):
    with patch.object(Customer, "get", side_effect=DoesNotExist()):
        resp = client.post("/orders", json=NEW_ORDER)
    assert resp.status_code == 422


def test_create_order_discontinued_product(client):
    gone = Product(id="p1", product_name="Chai", list_price=10, discontinued=1)
    with patch.object(Customer, "get", return_value=CUSTOMER), patch.object(Product, "get", return_value=gone):
        resp = client.post("/orders", json=NEW_ORDER)
    assert resp.status_code == 422


def test_create_order_validation(client):
    assert client.post("/orders", json={"customer_id": "c1", "items": []}).status_code == 400
    bad_qty = {"customer_id": "c1", "items": [{"product_id": "p1", "quantity": 0}]}
    assert client.post("/orders", json=bad_qty).status_code == 400
    bad_date = {**NEW_ORDER, "order_date": "yesterday"}
    assert client.post("/orders", json=bad_date).status_code == 400


def test_get_order(client):
    with patch.object(Order, "get", return_value=_order()):
        resp = client.get("/orders/o1")
    assert resp.status_code == 200 and resp.get_json()["items"][0]["product_name"] == "Chai"


def test_get_order_not_found(client):
    with patch.object(Order, "get", side_effect=DoesNotExist()):
        assert client.get("/orders/zzz").status_code == 404


def test_update_order_status(client):
    with patch.object(Order, "get", return_value=_order()), patch.object(Order, "save") as save:
        resp = client.put("/orders/o1", json={"status": "Shipped", "shipped_date": "2006-03-25"})
    assert resp.status_code == 200 and resp.get_json()["status"] == "Shipped"
    save.assert_called_once()


def test_update_order_invalid_status(client):
    assert client.put("/orders/o1", json={"status": "Teleported"}).status_code == 400


def test_update_order_cannot_change_items(client):
    assert client.put("/orders/o1", json={"items": []}).status_code == 400


def test_order_history_newest_first(client):
    orders = FakeResults([_order(id="o2"), _order(id="o1")])
    with patch.object(Customer, "get", return_value=CUSTOMER), \
            patch.object(Order.customer_index, "query", return_value=orders) as query:
        resp = client.get("/customers/c1/orders")
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["count"] == 2 and [o["id"] for o in body["items"]] == ["o2", "o1"]
    assert query.call_args.kwargs["scan_index_forward"] is False


def test_order_history_unknown_customer(client):
    with patch.object(Customer, "get", side_effect=DoesNotExist()):
        assert client.get("/customers/nope/orders").status_code == 404


def test_list_orders(client):
    with patch.object(Order, "scan", return_value=FakeResults([_order()])):
        resp = client.get("/orders")
    assert resp.status_code == 200 and resp.get_json()["count"] == 1


def test_update_order_empty_body(client):
    assert client.put("/orders/o1", json={}).status_code == 400
