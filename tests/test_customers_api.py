"""API-level tests. The only thing mocked is DynamoDB (the model's get/save/scan),
so routing, validation, services and JSON output are all exercised for real."""
from unittest.mock import patch

from pynamodb.exceptions import DoesNotExist

from app.models.customer import Customer
from tests.helpers import FakeResults

VALID = {"company": "Company A", "first_name": "Anna", "last_name": "Bedecs",
         "email_address": "anna@northwind.com"}


def test_create_customer(client):
    with patch.object(Customer, "save") as save:
        resp = client.post("/customers", json=VALID)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["company"] == "Company A" and body["id"]
    save.assert_called_once()


def test_create_customer_missing_company(client):
    resp = client.post("/customers", json={"first_name": "Anna"})
    assert resp.status_code == 400
    assert "company" in resp.get_json()["details"]


def test_create_customer_bad_email(client):
    resp = client.post("/customers", json={**VALID, "email_address": "not-an-email"})
    assert resp.status_code == 400
    assert "email_address" in resp.get_json()["details"]


def test_create_customer_unknown_field_rejected(client):
    resp = client.post("/customers", json={**VALID, "hacker": "x"})
    assert resp.status_code == 400


def test_get_customer(client):
    with patch.object(Customer, "get", return_value=Customer(id="1", company="Company A")):
        resp = client.get("/customers/1")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == "1"


def test_get_customer_not_found(client):
    with patch.object(Customer, "get", side_effect=DoesNotExist()):
        resp = client.get("/customers/999")
    assert resp.status_code == 404
    assert "999" in resp.get_json()["error"]


def test_update_customer(client):
    with patch.object(Customer, "get", return_value=Customer(id="1", company="Company A")), \
            patch.object(Customer, "save") as save:
        resp = client.put("/customers/1", json={"city": "Pune"})
    assert resp.status_code == 200
    assert resp.get_json()["city"] == "Pune"
    save.assert_called_once()


def test_update_customer_empty_body(client):
    resp = client.put("/customers/1", json={})
    assert resp.status_code == 400


def test_list_customers_with_next_token(client):
    rows = [Customer(id="1", company="A"), Customer(id="2", company="B")]
    with patch.object(Customer, "scan", return_value=FakeResults(rows, {"id": {"S": "2"}})):
        resp = client.get("/customers?limit=2")
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["count"] == 2 and body["next_token"]


def test_list_customers_bad_limit(client):
    assert client.get("/customers?limit=abc").status_code == 400
    assert client.get("/customers?limit=0").status_code == 400


def test_list_customers_bad_token(client):
    assert client.get("/customers?next_token=%%%").status_code == 400


def test_unknown_route_returns_json_404(client):
    resp = client.get("/nope")
    assert resp.status_code == 404 and "error" in resp.get_json()


def test_unexpected_error_returns_500_json(client):
    with patch.object(Customer, "get", side_effect=RuntimeError("boom")):
        resp = client.get("/customers/1")
    assert resp.status_code == 500
    assert resp.get_json() == {"error": "Internal server error"}
