from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.models import Model

from app.config import Config


class Product(Model):
    class Meta:
        table_name = Config.PRODUCTS_TABLE
        region = Config.AWS_REGION
        host = Config.DYNAMODB_HOST
        billing_mode = "PAY_PER_REQUEST"

    id = UnicodeAttribute(hash_key=True)
    product_code = UnicodeAttribute(null=True)
    product_name = UnicodeAttribute()
    description = UnicodeAttribute(null=True)
    category = UnicodeAttribute(null=True)
    quantity_per_unit = UnicodeAttribute(null=True)
    standard_cost = NumberAttribute(null=True)
    list_price = NumberAttribute()
    reorder_level = NumberAttribute(null=True)
    target_level = NumberAttribute(null=True)
    discontinued = NumberAttribute(default=0)  # 0 / 1, same as Northwind
