from pynamodb.attributes import ListAttribute, MapAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

from app.config import Config


class OrderItem(MapAttribute):
    """One line of an order (Northwind's `order_details` row). We store the
    lines *inside* the order - in DynamoDB that is the natural way to model it."""
    product_id = UnicodeAttribute()
    product_name = UnicodeAttribute(null=True)
    quantity = NumberAttribute()
    unit_price = NumberAttribute()
    discount = NumberAttribute(default=0)


class CustomerIndex(GlobalSecondaryIndex):
    """Lets us ask 'give me all orders of customer X, newest first' without a scan."""
    class Meta:
        index_name = "customer-index"
        projection = AllProjection()

    customer_id = UnicodeAttribute(hash_key=True)
    order_date = UnicodeAttribute(range_key=True)


class Order(Model):
    class Meta:
        table_name = Config.ORDERS_TABLE
        region = Config.AWS_REGION
        host = Config.DYNAMODB_HOST
        billing_mode = "PAY_PER_REQUEST"

    id = UnicodeAttribute(hash_key=True)
    customer_id = UnicodeAttribute()
    order_date = UnicodeAttribute()  # ISO-8601 string, sorts correctly
    shipped_date = UnicodeAttribute(null=True)
    status = UnicodeAttribute(default="New")
    payment_type = UnicodeAttribute(null=True)
    shipping_fee = NumberAttribute(default=0)
    ship_name = UnicodeAttribute(null=True)
    ship_address = UnicodeAttribute(null=True)
    ship_city = UnicodeAttribute(null=True)
    ship_country_region = UnicodeAttribute(null=True)
    notes = UnicodeAttribute(null=True)
    total_amount = NumberAttribute(default=0)
    items = ListAttribute(of=OrderItem, default=list)

    customer_index = CustomerIndex()
