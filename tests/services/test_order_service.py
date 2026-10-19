"""Pure unit tests: every collaborator (Customer, Product, Order) is replaced
with a mock, so nothing outside the function under test is executed."""
from unittest.mock import MagicMock, patch

import pytest
from pynamodb.exceptions import DoesNotExist

from app.services import order_service
from app.utils.errors import BusinessRuleError, NotFoundError

P = "app.services.order_service."


@patch(P + "Order")
@patch(P + "Product")
@patch(P + "Customer")
def test_create_order_saves_and_computes_total(Customer, Product, Order):
    Product.get.return_value = MagicMock(product_name="Chai", list_price=20.0, discontinued=0)
    data = {"customer_id": "c1", "shipping_fee": 0,
            "items": [{"product_id": "p1", "quantity": 2, "discount": 0.5}]}

    order_service.create_order(data)

    Customer.get.assert_called_once_with("c1")
    assert Order.call_args.kwargs["total_amount"] == 20.0
    Order.return_value.save.assert_called_once()


@patch(P + "Customer")
def test_create_order_unknown_customer(Customer):
    Customer.get.side_effect = DoesNotExist()
    with pytest.raises(BusinessRuleError):
        order_service.create_order({"customer_id": "x", "items": []})


@patch(P + "Order")
def test_get_order_history_queries_index_descending(Order):
    Order.customer_index.query.return_value = MagicMock(__iter__=lambda s: iter(["a"]),
                                                        last_evaluated_key=None)
    with patch(P + "get_or_404") as check:
        items, token = order_service.get_order_history("c1", 10)
    check.assert_called_once()
    assert items == ["a"] and token is None
    Order.customer_index.query.assert_called_once_with(
        "c1", scan_index_forward=False, limit=10, last_evaluated_key=None)


@patch(P + "Customer")
def test_get_order_history_unknown_customer(Customer):
    Customer.get.side_effect = DoesNotExist()
    with pytest.raises(NotFoundError):
        order_service.get_order_history("nope", 10)
