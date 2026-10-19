"""Load Northwind CSV exports into DynamoDB.

    python -m scripts.seed_data --data-dir data/sample            # real AWS (uses your AWS creds)
    python -m scripts.seed_data --data-dir data/sample --create-tables   # DynamoDB Local

Expected files in --data-dir (export them from the mywind MySQL database):
    customers.csv, products.csv, orders.csv, order_details.csv
"""
import argparse
import csv
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("seed")

ORDER_STATUS = {"0": "New", "1": "Invoiced", "2": "Shipped", "3": "Closed"}  # mywind orders_status


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            # MySQL exports use '', NULL or \N for missing values
            yield {k: (None if v in ("", "NULL", "\\N") else v) for k, v in row.items()}


def pick(row, model):
    allowed = model.get_attributes().keys()
    return {k: v for k, v in row.items() if k in allowed and v is not None}


def iso(value):
    return datetime.fromisoformat(value).isoformat() if value else None


def seed(data_dir: Path, create_tables: bool):
    if create_tables:
        for model in (Customer, Product, Order):
            if not model.exists():
                model.create_table(wait=True)
                log.info("Created table %s", model.Meta.table_name)

    count = 0
    with Customer.batch_write() as batch:
        for row in read_csv(data_dir / "customers.csv"):
            batch.save(Customer(**pick(row, Customer)))
            count += 1
    log.info("Customers: %d", count)

    count = 0
    with Product.batch_write() as batch:
        for row in read_csv(data_dir / "products.csv"):
            data = pick(row, Product)
            data["list_price"] = float(row["list_price"])
            if row.get("standard_cost"):
                data["standard_cost"] = float(row["standard_cost"])
            data["discontinued"] = int(row.get("discontinued") or 0)
            for key in ("reorder_level", "target_level"):
                if row.get(key):
                    data[key] = int(float(row[key]))
            batch.save(Product(**data))
            count += 1
    log.info("Products: %d", count)

    names = {r["id"]: r["product_name"] for r in read_csv(data_dir / "products.csv")}
    lines = defaultdict(list)
    for row in read_csv(data_dir / "order_details.csv"):
        lines[row["order_id"]].append(OrderItem(
            product_id=row["product_id"], product_name=names.get(row["product_id"]),
            quantity=int(float(row["quantity"])), unit_price=float(row["unit_price"]),
            discount=float(row.get("discount") or 0)))

    count = 0
    with Order.batch_write() as batch:
        for row in read_csv(data_dir / "orders.csv"):
            data = pick(row, Order)
            items = lines.get(row["id"], [])
            data.update(
                order_date=iso(row["order_date"]), shipped_date=iso(row.get("shipped_date")),
                status=ORDER_STATUS.get(row.get("status_id"), "New"),
                shipping_fee=float(row.get("shipping_fee") or 0), items=items,
                total_amount=round(sum(i.quantity * i.unit_price * (1 - i.discount) for i in items), 2))
            batch.save(Order(**data))
            count += 1
    log.info("Orders: %d", count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/sample", type=Path)
    parser.add_argument("--create-tables", action="store_true",
                        help="create the tables first (only for DynamoDB Local / tests)")
    args = parser.parse_args()
    seed(args.data_dir, args.create_tables)
