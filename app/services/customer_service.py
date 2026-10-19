import logging
import uuid

from app.models.customer import Customer
from app.services.common import apply_update, get_or_404, list_page

logger = logging.getLogger(__name__)


def list_customers(limit, last_key=None):
    return list_page(Customer, limit, last_key)


def get_customer(customer_id):
    return get_or_404(Customer, customer_id, "Customer")


def create_customer(data):
    customer = Customer(id=uuid.uuid4().hex, **data)
    customer.save()
    logger.info("Created customer %s", customer.id)
    return customer


def update_customer(customer_id, data):
    customer = get_customer(customer_id)
    apply_update(customer, data)
    logger.info("Updated customer %s fields=%s", customer_id, sorted(data))
    return customer
