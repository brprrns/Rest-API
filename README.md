# Northwind REST API

A small REST API built with **Flask, AWS Lambda, and DynamoDB** using the Northwind sample data.

## What can you do?

### Customers
- Get all customers
- Create a customer
- Get or update one customer
- See a customer's order history

### Products
- Get all products
- Create a product
- Get or update a product

### Orders
- Get all orders
- Place a new order
- Get or update an order
- Update shipping details/status

### Health
- `/health` checks whether the API is running.

## How it works

```text
Client
  ↓
API Gateway
  ↓
AWS Lambda + Flask
  ↓
DynamoDB
```

The project is separated into simple layers:

- `models` → database tables
- `schemas` → validate and format data
- `controllers` → API routes
- `services` → business logic and database operations

## Run locally

Create a virtual environment and install the packages:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Start DynamoDB locally:

```bash
docker run -d -p 8000:8000 amazon/dynamodb-local
```

Set the local AWS settings:

```bash
export DYNAMODB_HOST=http://localhost:8000
export AWS_REGION=ap-south-1
export AWS_ACCESS_KEY_ID=local
export AWS_SECRET_ACCESS_KEY=local
```

Load sample data:

```bash
python -m scripts.seed_data --data-dir data/sample --create-tables
```

Start the API:

```bash
python run_local.py
```

Test it:

```bash
curl http://127.0.0.1:5000/customers
```

## Run tests

No AWS account is needed for testing.

```bash
pytest --cov=app
```

The DynamoDB calls are mocked during tests.

## Using real Northwind data

The `data/sample` folder only contains a small amount of data.

For the full Northwind database:

1. Load the `mywind` SQL files into MySQL.
2. Export these tables to CSV:
   - customers
   - products
   - orders
   - order_details
3. Put the CSV files in `data/northwind/`.
4. Run:

```bash
python -m scripts.seed_data --data-dir data/northwind
```

## Deploy to AWS

You need:

- AWS account
- AWS CLI
- AWS SAM CLI

Build and deploy:

```bash
sam build
sam deploy --guided
```

AWS will create the Lambda function, API Gateway, DynamoDB tables, and CloudWatch logs.

After deployment, SAM gives you an `ApiUrl`.

Example:

```bash
curl $API_URL/customers
curl $API_URL/customers/1/orders
```

## Example: Create a customer

```bash
curl -X POST $API_URL/customers \
  -H "Content-Type: application/json" \
  -d '{"company":"Company Z","email_address":"z@example.com","city":"Bengaluru"}'
```

## Example: Place an order

```bash
curl -X POST $API_URL/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"1","items":[{"product_id":"1","quantity":3,"discount":0.1}]}'
```

The server calculates the product price and order total.

## Example: Update an order

```bash
curl -X PUT $API_URL/orders/<order-id> \
  -H "Content-Type: application/json" \
  -d '{"status":"Shipped","shipped_date":"2006-03-25"}'
```

## Errors

The API returns JSON errors:

- `400` → invalid request
- `404` → not found
- `422` → business rule failed
- `500` → server error

## Logs

Application logs are available in **CloudWatch Logs**.

You can also watch Lambda logs from your terminal:

```bash
sam logs -n ApiFunction --stack-name northwind-api --tail
```

## Git workflow

Create the project:

```bash
git init
git add .
git commit -m "feat: initial Northwind REST API"
```

For a new feature:

```bash
git checkout -b feature/order-validation
git commit -m "fix: reject discontinued products"
```

Keep commits small and use simple Conventional Commit prefixes such as:

```text
feat:
fix:
test:
docs:
```

## Clean up AWS resources

When you're finished:

```bash
sam delete
```