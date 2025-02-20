import sqlite3
from passlib.hash import sha256_crypt


# Connect to the DB (its created if not exist)
conn = sqlite3.connect('shop.db')
cursor = conn.cursor()

# Initial admin user information
name = "admin"
password = "1009"
role = "admin"

# Generate the hash with the passoword
hashedPassword = sha256_crypt.hash(password)

# Create the products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    product_price REAL NOT NULL,
    product_stock INTEGER DEFAULT 0
);''')


# Create the users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    user_name TEXT NOT NULL,
    user_password TEXT NOT NULL,
    user_role TEXT NOT NULL
);''')


# SQL query to add admin info
cursor.execute('''
INSERT INTO users (user_name, user_password, user_role) VALUES (?, ?, ?);
''', (name, hashedPassword, role))


# Create the customers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_phone TEXT,
    customer_address TEXT
);''')


# SQL query to add customer info
cursor.execute('''
INSERT INTO customers (customer_name, customer_email, customer_phone, customer_address) VALUES (?, ?, ?, ?);
''', ("Pepe Julian", "pepejulianonzima@gmail.com", "648 798 798", "Via de Lagos 2"))


# Create the orders table
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);''')


# Create the orders items table
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);''')


# Save the changes and close conection
conn.commit()
conn.close()
