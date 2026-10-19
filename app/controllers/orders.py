from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.schemas.order_schema import OrderCreateSchema, OrderSchema, OrderUpdateSchema
from app.services import order_service
from app.utils.pagination import get_page_params

bp = Blueprint("orders", __name__, url_prefix="/orders")
create_schema = OrderCreateSchema()
update_schema = OrderUpdateSchema()
schema = OrderSchema()


def _body():
    return request.get_json(silent=True) or {}


@bp.get("")
def list_orders():
    limit, last_key = get_page_params()
    items, token = order_service.list_orders(limit, last_key)
    return jsonify({"items": schema.dump(items, many=True), "count": len(items), "next_token": token})


@bp.post("")
def create_order():
    data = create_schema.load(_body())
    return jsonify(schema.dump(order_service.create_order(data))), 201


@bp.get("/<order_id>")
def get_order(order_id):
    return jsonify(schema.dump(order_service.get_order(order_id)))


@bp.route("/<order_id>", methods=["PUT", "PATCH"])
def update_order(order_id):
    data = update_schema.load(_body())
    if not data:
        raise ValidationError({"_schema": ["Send at least one field to update"]})
    return jsonify(schema.dump(order_service.update_order(order_id, data)))
