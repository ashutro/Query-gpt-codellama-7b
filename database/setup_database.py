# database/setup_database.py
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

def create_database():
    """Create SQLite database with sample e-commerce data"""
    conn = sqlite3.connect('database/querygpt.db')
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        registration_date DATE,
        country TEXT,
        city TEXT,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        cost DECIMAL(10,2) NOT NULL,
        description TEXT,
        created_date DATE
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date DATE NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        status TEXT NOT NULL,
        shipping_country TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    ''')
    
    # Create order_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        item_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    
    conn.commit()
    return conn

def populate_sample_data(conn):
    """Populate database with realistic sample data"""
    cursor = conn.cursor()
    
    # Sample customers data
    customers_data = [
        (1, 'John', 'Smith', 'john.smith@email.com', '2023-01-15', 'USA', 'New York', 1),
        (2, 'Sarah', 'Johnson', 'sarah.j@email.com', '2023-02-20', 'USA', 'Los Angeles', 1),
        (3, 'Mike', 'Brown', 'mike.brown@email.com', '2023-03-10', 'Canada', 'Toronto', 1),
        (4, 'Emma', 'Davis', 'emma.davis@email.com', '2023-04-05', 'UK', 'London', 0),
        (5, 'David', 'Wilson', 'david.w@email.com', '2023-05-12', 'Australia', 'Sydney', 1),
    ]
    
    cursor.executemany('''
    INSERT OR REPLACE INTO customers VALUES (?,?,?,?,?,?,?,?)
    ''', customers_data)
    
    # Sample products data
    products_data = [
        (1, 'Laptop Pro 15"', 'Electronics', 1299.99, 800.00, 'High-performance laptop', '2023-01-01'),
        (2, 'Wireless Headphones', 'Electronics', 199.99, 120.00, 'Noise-cancelling headphones', '2023-01-01'),
        (3, 'Coffee Machine', 'Appliances', 299.99, 180.00, 'Automatic coffee maker', '2023-01-01'),
        (4, 'Running Shoes', 'Apparel', 129.99, 70.00, 'Professional running shoes', '2023-01-01'),
        (5, 'Smartphone Case', 'Accessories', 29.99, 15.00, 'Protective phone case', '2023-01-01'),
    ]
    
    cursor.executemany('''
    INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?)
    ''', products_data)
    
    # Sample orders data
    orders_data = [
        (1, 1, '2023-06-01', 1499.98, 'completed', 'USA'),
        (2, 2, '2023-06-15', 329.98, 'completed', 'USA'),
        (3, 3, '2023-07-01', 159.98, 'shipped', 'Canada'),
        (4, 1, '2023-07-15', 29.99, 'completed', 'USA'),
        (5, 5, '2023-08-01', 1629.97, 'processing', 'Australia'),
    ]
    
    cursor.executemany('''
    INSERT OR REPLACE INTO orders VALUES (?,?,?,?,?,?)
    ''', orders_data)
    
    # Sample order_items data
    order_items_data = [
        (1, 1, 1, 1, 1299.99),  # Order 1: Laptop
        (2, 1, 2, 1, 199.99),   # Order 1: Headphones
        (3, 2, 3, 1, 299.99),   # Order 2: Coffee Machine
        (4, 2, 5, 1, 29.99),    # Order 2: Phone Case
        (5, 3, 4, 1, 129.99),   # Order 3: Running Shoes
        (6, 3, 5, 1, 29.99),    # Order 3: Phone Case
        (7, 4, 5, 1, 29.99),    # Order 4: Phone Case
        (8, 5, 1, 1, 1299.99),  # Order 5: Laptop
        (9, 5, 2, 1, 199.99),   # Order 5: Headphones
        (10, 5, 4, 1, 129.99),  # Order 5: Running Shoes
    ]
    
    cursor.executemany('''
    INSERT OR REPLACE INTO order_items VALUES (?,?,?,?,?)
    ''', order_items_data)
    
    conn.commit()
    print("Sample data populated successfully!")

if __name__ == "__main__":
    conn = create_database()
    populate_sample_data(conn)
    conn.close()
