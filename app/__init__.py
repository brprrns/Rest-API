"""Application factory. Both `run_local.py` and the Lambda handler call create_app()."""
import logging
import time

from flask import Flask, g, jsonify, request

from app.config import Config
from app.controllers import customers, orders, products
from app.utils.errors import register_error_handlers
from app.utils.logger import configure_logging

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    configure_logging(Config.LOG_LEVEL)
    app = Flask(__name__)

    app.register_blueprint(customers.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(orders.bp)
    register_error_handlers(app)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.before_request
    def start_timer():
        g.start = time.perf_counter()

    @app.after_request
    def log_request(response):
        ms = (time.perf_counter() - g.get("start", time.perf_counter())) * 1000
        logger.info("%s %s -> %s (%.1f ms)", request.method, request.path, response.status_code, ms)
        return response

    return app
