from datetime import datetime

from marshmallow import Schema, ValidationError, fields, validate

ORDER_STATUSES = ["New", "Invoiced", "Shipped", "Closed"]


def _iso_datetime(value: str):
    try:
        datetime.fromisoformat(value)
    except ValueError:
        raise ValidationError("Must be ISO-8601, e.g. 2006-01-15 or 2006-01-15T10:30:00")


class _ShippingFields:
    payment_type = fields.Str(allow_none=True, validate=validate.Length(max=50))
    ship_name = fields.Str(allow_none=True, validate=validate.Length(max=100))
    ship_address = fields.Str(allow_none=True, validate=validate.Length(max=255))
    ship_city = fields.Str(allow_none=True, validate=validate.Length(max=100))
    ship_country_region = fields.Str(allow_none=True, validate=validate.Length(max=100))
    notes = fields.Str(allow_none=True)


class OrderItemInputSchema(Schema):
    product_id = fields.Str(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    discount = fields.Float(load_default=0, validate=validate.Range(min=0, max=1))


class OrderCreateSchema(_ShippingFields, Schema):
    """What the client may send when placing an order. Prices are NOT accepted
    from the client - the server copies them from the product."""
    customer_id = fields.Str(required=True)
    order_date = fields.Str(validate=_iso_datetime)
    shipping_fee = fields.Float(load_default=0, validate=validate.Range(min=0))
    items = fields.List(fields.Nested(OrderItemInputSchema), required=True,
                        validate=validate.Length(min=1))


class OrderUpdateSchema(_ShippingFields, Schema):
    """Only these fields can change after an order exists."""
    status = fields.Str(validate=validate.OneOf(ORDER_STATUSES))
    shipped_date = fields.Str(allow_none=True, validate=_iso_datetime)
    shipping_fee = fields.Float(validate=validate.Range(min=0))


class OrderItemSchema(Schema):
    product_id = fields.Str()
    product_name = fields.Str()
    quantity = fields.Int()
    unit_price = fields.Float()
    discount = fields.Float()


class OrderSchema(_ShippingFields, Schema):
    """How an order looks in responses."""
    id = fields.Str()
    customer_id = fields.Str()
    order_date = fields.Str()
    shipped_date = fields.Str(allow_none=True)
    status = fields.Str()
    shipping_fee = fields.Float()
    total_amount = fields.Float()
    items = fields.List(fields.Nested(OrderItemSchema))
