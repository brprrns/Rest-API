"""Simple cursor pagination. DynamoDB gives us a 'last evaluated key'; we hand
it to the client as an opaque base64 token called next_token."""
import base64
import json

from flask import request
from marshmallow import ValidationError

from app.config import Config


def encode_token(key):
    if not key:
        return None
    return base64.urlsafe_b64encode(json.dumps(key).encode()).decode()


def decode_token(token):
    if not token:
        return None
    try:
        return json.loads(base64.urlsafe_b64decode(token.encode()))
    except Exception:
        raise ValidationError({"next_token": ["Invalid pagination token"]})


def get_page_params():
    """Reads ?limit= and ?next_token= from the query string."""
    raw = request.args.get("limit", Config.DEFAULT_PAGE_SIZE)
    try:
        limit = int(raw)
    except (TypeError, ValueError):
        raise ValidationError({"limit": ["Must be an integer"]})
    if not 1 <= limit <= Config.MAX_PAGE_SIZE:
        raise ValidationError({"limit": [f"Must be between 1 and {Config.MAX_PAGE_SIZE}"]})
    return limit, decode_token(request.args.get("next_token"))
