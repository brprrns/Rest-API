"""Sends a fake API Gateway event through the real Lambda handler."""
import json

from handler import lambda_handler


def _event(method, path):
    return {
        "version": "2.0", "rawPath": path, "rawQueryString": "",
        "headers": {"host": "example.com"}, "isBase64Encoded": False,
        "requestContext": {"http": {"method": method, "path": path, "protocol": "HTTP/1.1",
                                    "sourceIp": "1.2.3.4"}},
    }


def test_health_through_lambda_handler():
    result = lambda_handler(_event("GET", "/health"), None)
    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == {"status": "ok"}
