import sqlite3


DATABASE = "app/northwind.db"


connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_name TEXT,
    contact_title TEXT,
    address TEXT,
    city TEXT,
    region TEXT,
    postal_code TEXT,
    country TEXT,
    phone TEXT,
    fax TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    supplier_id INTEGER,
    category_id INTEGER,
    quantity_per_unit TEXT,
    unit_price REAL,
    units_in_stock INTEGER,
    units_on_order INTEGER,
    reorder_level INTEGER,
    discontinued INTEGER DEFAULT 0
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_date TEXT,
    required_date TEXT,
    shipped_date TEXT,
    ship_via INTEGER,
    freight REAL,
    ship_name TEXT,
    ship_address TEXT,
    ship_city TEXT,
    ship_region TEXT,
    ship_postal_code TEXT,
    ship_country TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS order_details (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    unit_price REAL,
    quantity INTEGER,
    discount REAL DEFAULT 0,

    PRIMARY KEY (order_id, product_id),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
)
""")


connection.commit()
connection.close()


print("Northwind database created successfully.")