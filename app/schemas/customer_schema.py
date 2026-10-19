from marshmallow import Schema, fields, validate

_text = validate.Length(max=255)


class CustomerSchema(Schema):
    id = fields.Str(dump_only=True)
    company = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    first_name = fields.Str(allow_none=True, validate=_text)
    last_name = fields.Str(allow_none=True, validate=_text)
    email_address = fields.Email(allow_none=True)
    job_title = fields.Str(allow_none=True, validate=_text)
    business_phone = fields.Str(allow_none=True, validate=validate.Length(max=25))
    address = fields.Str(allow_none=True, validate=_text)
    city = fields.Str(allow_none=True, validate=_text)
    state_province = fields.Str(allow_none=True, validate=_text)
    zip_postal_code = fields.Str(allow_none=True, validate=validate.Length(max=15))
    country_region = fields.Str(allow_none=True, validate=_text)
