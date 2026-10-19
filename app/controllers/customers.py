from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.schemas.customer_schema import CustomerSchema
from app.schemas.order_schema import OrderSchema
from app.services import customer_service, order_service
from app.utils.pagination import get_page_params

bp = Blueprint("customers", __name__, url_prefix="/customers")
schema = CustomerSchema()
order_schema = OrderSchema()


def _body():
    return request.get_json(silent=True) or {}


@bp.get("")
def list_customers():
    limit, last_key = get_page_params()
    items, token = customer_service.list_customers(limit, last_key)
    return jsonify({"items": schema.dump(items, many=True), "count": len(items), "next_token": token})


@bp.post("")
def create_customer():
    data = schema.load(_body())
    return jsonify(schema.dump(customer_service.create_customer(data))), 201


@bp.get("/<customer_id>")
def get_customer(customer_id):
    return jsonify(schema.dump(customer_service.get_customer(customer_id)))


@bp.route("/<customer_id>", methods=["PUT", "PATCH"])
def update_customer(customer_id):
    data = schema.load(_body(), partial=True)
    if not data:
        raise ValidationError({"_schema": ["Send at least one field to update"]})
    return jsonify(schema.dump(customer_service.update_customer(customer_id, data)))


@bp.get("/<customer_id>/orders")
def order_history(customer_id):
    limit, last_key = get_page_params()
    items, token = order_service.get_order_history(customer_id, limit, last_key)
    return jsonify({"customer_id": customer_id, "count": len(items),
                    "items": order_schema.dump(items, many=True), "next_token": token})
