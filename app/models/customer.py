from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

from app.config import Config


class Customer(Model):
    class Meta:
        table_name = Config.CUSTOMERS_TABLE
        region = Config.AWS_REGION
        host = Config.DYNAMODB_HOST
        billing_mode = "PAY_PER_REQUEST"

    id = UnicodeAttribute(hash_key=True)
    company = UnicodeAttribute()
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    email_address = UnicodeAttribute(null=True)
    job_title = UnicodeAttribute(null=True)
    business_phone = UnicodeAttribute(null=True)
    address = UnicodeAttribute(null=True)
    city = UnicodeAttribute(null=True)
    state_province = UnicodeAttribute(null=True)
    zip_postal_code = UnicodeAttribute(null=True)
    country_region = UnicodeAttribute(null=True)
