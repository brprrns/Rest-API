from marshmallow import Schema, fields, validate


class ProductSchema(Schema):
    id = fields.Str(dump_only=True)
    product_code = fields.Str(allow_none=True, validate=validate.Length(max=25))
    product_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    category = fields.Str(allow_none=True, validate=validate.Length(max=50))
    quantity_per_unit = fields.Str(allow_none=True, validate=validate.Length(max=50))
    standard_cost = fields.Float(allow_none=True, validate=validate.Range(min=0))
    list_price = fields.Float(required=True, validate=validate.Range(min=0))
    reorder_level = fields.Int(allow_none=True, validate=validate.Range(min=0))
    target_level = fields.Int(allow_none=True, validate=validate.Range(min=0))
    discontinued = fields.Int(validate=validate.OneOf([0, 1]))
