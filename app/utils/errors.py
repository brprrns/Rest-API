"""Custom exceptions + one place that turns every error into clean JSON."""
import logging

from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class BusinessRuleError(AppError):
    """Request is well-formed but breaks a rule (e.g. unknown customer id)."""
    status_code = 422


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"error": err.message}), err.status_code

    @app.errorhandler(HTTPException)
    def handle_http(err):
        return jsonify({"error": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception("Unhandled error")  # full stack trace -> CloudWatch
        return jsonify({"error": "Internal server error"}), 500
