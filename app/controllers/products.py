from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.schemas.product_schema import ProductSchema
from app.services import product_service
from app.utils.pagination import get_page_params

bp = Blueprint("products", __name__, url_prefix="/products")
schema = ProductSchema()


def _body():
    return request.get_json(silent=True) or {}


@bp.get("")
def list_products():
    limit, last_key = get_page_params()
    items, token = product_service.list_products(limit, last_key)
    return jsonify({"items": schema.dump(items, many=True), "count": len(items), "next_token": token})


@bp.post("")
def create_product():
    data = schema.load(_body())
    return jsonify(schema.dump(product_service.create_product(data))), 201


@bp.get("/<product_id>")
def get_product(product_id):
    return jsonify(schema.dump(product_service.get_product(product_id)))


@bp.route("/<product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    data = schema.load(_body(), partial=True)
    if not data:
        raise ValidationError({"_schema": ["Send at least one field to update"]})
    return jsonify(schema.dump(product_service.update_product(product_id, data)))
