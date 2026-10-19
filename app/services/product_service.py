import logging
import uuid

from app.models.product import Product
from app.services.common import apply_update, get_or_404, list_page

logger = logging.getLogger(__name__)


def list_products(limit, last_key=None):
    return list_page(Product, limit, last_key)


def get_product(product_id):
    return get_or_404(Product, product_id, "Product")


def create_product(data):
    product = Product(id=uuid.uuid4().hex, **data)
    product.save()
    logger.info("Created product %s", product.id)
    return product


def update_product(product_id, data):
    product = get_product(product_id)
    apply_update(product, data)
    logger.info("Updated product %s fields=%s", product_id, sorted(data))
    return product
