import sqlite3
import random
from datetime import datetime, timedelta

# Create database
conn = sqlite3.connect('sales.db')
cursor = conn.cursor()

# Create tables
cursor.executescript('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        region TEXT,
        segment TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        order_date TEXT,
        total_amount REAL,
        status TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
''')

# Sample data
regions = ['North', 'South', 'East', 'West']
segments = ['Enterprise', 'SMB', 'Startup']
categories = ['Software', 'Hardware', 'Services', 'Consulting']
statuses = ['Completed', 'Pending', 'Cancelled']

# Insert customers
customers = [
    (1, 'Rahul Sharma', 'rahul@email.com', 'North', 'Enterprise'),
    (2, 'Priya Patel', 'priya@email.com', 'South', 'SMB'),
    (3, 'Amit Singh', 'amit@email.com', 'East', 'Startup'),
    (4, 'Sneha Verma', 'sneha@email.com', 'West', 'Enterprise'),
    (5, 'Raj Kumar', 'raj@email.com', 'North', 'SMB'),
    (6, 'Anjali Gupta', 'anjali@email.com', 'South', 'Startup'),
    (7, 'Vikram Mehta', 'vikram@email.com', 'East', 'Enterprise'),
    (8, 'Pooja Joshi', 'pooja@email.com', 'West', 'SMB'),
]

# Insert products
products = [
    (1, 'CRM Pro', 'Software', 299.99),
    (2, 'Laptop Elite', 'Hardware', 1299.99),
    (3, 'Cloud Setup', 'Services', 499.99),
    (4, 'Strategy Plan', 'Consulting', 899.99),
    (5, 'Analytics Suite', 'Software', 399.99),
    (6, 'Server Unit', 'Hardware', 2499.99),
    (7, 'Support Pack', 'Services', 199.99),
    (8, 'Growth Plan', 'Consulting', 1199.99),
]

cursor.executemany('INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?)', customers)
cursor.executemany('INSERT OR IGNORE INTO products VALUES (?,?,?,?)', products)

# Generate 200 random orders
random.seed(42)
base_date = datetime(2025, 1, 1)

for i in range(1, 201):
    customer_id = random.randint(1, 8)
    product_id = random.randint(1, 8)
    quantity = random.randint(1, 10)
    price = products[product_id - 1][3]
    total = round(quantity * price, 2)
    order_date = base_date + timedelta(days=random.randint(0, 365))
    status = random.choice(statuses)

    cursor.execute(
        'INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?,?)',
        (i, customer_id, product_id, quantity,
         order_date.strftime('%Y-%m-%d'), total, status)
    )

conn.commit()
conn.close()

print("✅ Database created successfully!")
print("📦 Tables: customers, products, orders")
print("👥 8 customers across 4 regions")
print("🛍️ 8 products across 4 categories")
print("📋 200 orders generated!")