"""Central place for configuration. Everything comes from environment variables
so the same code runs locally, in tests and on Lambda."""
import os


class Config:
    AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
    # Only set this when using DynamoDB Local, e.g. http://localhost:8000
    DYNAMODB_HOST = os.getenv("DYNAMODB_HOST") or None

    CUSTOMERS_TABLE = os.getenv("CUSTOMERS_TABLE", "northwind-dev-customers")
    PRODUCTS_TABLE = os.getenv("PRODUCTS_TABLE", "northwind-dev-products")
    ORDERS_TABLE = os.getenv("ORDERS_TABLE", "northwind-dev-orders")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 100
