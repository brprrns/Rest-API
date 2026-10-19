import logging
import uuid
from datetime import datetime, timezone

from pynamodb.exceptions import DoesNotExist

from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.services.common import apply_update, get_or_404, list_page
from app.utils.errors import BusinessRuleError
from app.utils.pagination import encode_token

logger = logging.getLogger(__name__)


def list_orders(limit, last_key=None):
    return list_page(Order, limit, last_key)


def get_order(order_id):
    return get_or_404(Order, order_id, "Order")


def _must_exist(model, item_id, label):
    try:
        return model.get(item_id)
    except DoesNotExist:
        raise BusinessRuleError(f"{label} '{item_id}' does not exist")


def create_order(data):
    _must_exist(Customer, data["customer_id"], "Customer")

    items = []
    for line in data["items"]:
        product = _must_exist(Product, line["product_id"], "Product")
        if product.discontinued:
            raise BusinessRuleError(f"Product '{line['product_id']}' is discontinued")
        items.append(OrderItem(
            product_id=line["product_id"],
            product_name=product.product_name,
            quantity=line["quantity"],
            unit_price=product.list_price,  # price always comes from the server
            discount=line["discount"],
        ))

    total = round(sum(i.quantity * i.unit_price * (1 - i.discount) for i in items), 2)
    order_date = data.get("order_date")
    order_date = datetime.fromisoformat(order_date) if order_date else datetime.now(timezone.utc)

    fields = {k: v for k, v in data.items() if k not in ("items", "order_date")}
    order = Order(id=uuid.uuid4().hex, order_date=order_date.isoformat(),
                  items=items, total_amount=total, status="New", **fields)
    order.save()
    logger.info("Created order %s for customer %s total=%s", order.id, order.customer_id, total)
    return order


def update_order(order_id, data):
    order = get_order(order_id)
    apply_update(order, data)
    logger.info("Updated order %s fields=%s", order_id, sorted(data))
    return order


def get_order_history(customer_id, limit, last_key=None):
    """All orders of one customer, newest first (uses the customer-index GSI)."""
    get_or_404(Customer, customer_id, "Customer")
    results = Order.customer_index.query(
        customer_id, scan_index_forward=False, limit=limit, last_evaluated_key=last_key)
    items = list(results)
    return items, encode_token(results.last_evaluated_key)
