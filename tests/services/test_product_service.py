from unittest.mock import MagicMock, patch

import pytest
from pynamodb.exceptions import DoesNotExist

from app.services import product_service
from app.utils.errors import NotFoundError

P = "app.services.product_service.Product"


@patch(P)
def test_create_product(Product):
    product_service.create_product({"product_name": "Tea", "list_price": 3.0})
    Product.return_value.save.assert_called_once()


@patch(P)
def test_update_product(Product):
    existing = MagicMock()
    Product.get.return_value = existing
    product_service.update_product("1", {"list_price": 9.0})
    assert existing.list_price == 9.0
    existing.save.assert_called_once()


@patch(P)
def test_get_product_not_found(Product):
    Product.get.side_effect = DoesNotExist()
    with pytest.raises(NotFoundError):
        product_service.get_product("1")
