from unittest.mock import MagicMock, patch

import pytest
from pynamodb.exceptions import DoesNotExist

from app.services import customer_service
from app.utils.errors import NotFoundError

P = "app.services.customer_service.Customer"


@patch(P)
def test_create_customer_generates_id_and_saves(Customer):
    customer_service.create_customer({"company": "ACME"})
    kwargs = Customer.call_args.kwargs
    assert kwargs["company"] == "ACME" and len(kwargs["id"]) == 32
    Customer.return_value.save.assert_called_once()


@patch(P)
def test_get_customer_not_found(Customer):
    Customer.get.side_effect = DoesNotExist()
    with pytest.raises(NotFoundError):
        customer_service.get_customer("1")


@patch(P)
def test_update_customer_sets_fields_and_saves(Customer):
    existing = MagicMock()
    Customer.get.return_value = existing
    customer_service.update_customer("1", {"city": "Pune"})
    assert existing.city == "Pune"
    existing.save.assert_called_once()


@patch(P)
def test_list_customers_returns_token(Customer):
    Customer.scan.return_value = MagicMock(__iter__=lambda s: iter([1, 2]),
                                           last_evaluated_key={"id": {"S": "2"}})
    items, token = customer_service.list_customers(2)
    assert items == [1, 2] and token
