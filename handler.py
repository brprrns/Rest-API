"""AWS Lambda entry point. API Gateway -> apig-wsgi -> Flask app."""
from apig_wsgi import make_lambda_handler

from app import create_app

app = create_app()
lambda_handler = make_lambda_handler(app)
