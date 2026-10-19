from pynamodb.exceptions import DoesNotExist

from app.utils.errors import NotFoundError
from app.utils.pagination import encode_token


def get_or_404(model, item_id, label):
    try:
        return model.get(item_id)
    except DoesNotExist:
        raise NotFoundError(f"{label} '{item_id}' not found")


def list_page(model, limit, last_key):
    results = model.scan(limit=limit, last_evaluated_key=last_key)
    items = list(results)
    return items, encode_token(results.last_evaluated_key)


def apply_update(item, data):
    for field, value in data.items():
        setattr(item, field, value)
    item.save()
    return item
