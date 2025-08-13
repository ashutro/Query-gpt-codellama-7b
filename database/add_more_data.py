# database/add_more_data.py
import sqlite3
import random
from datetime import datetime, timedelta

def add_extended_data():
    conn = sqlite3.connect('database/querygpt.db')
    cursor = conn.cursor()
    
    # Add more customers
    additional_customers = []
    countries = ['USA', 'Canada', 'UK', 'Australia', 'Germany', 'France']
    cities = {
        'USA': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
        'Canada': ['Toronto', 'Vancouver', 'Montreal'],
        'UK': ['London', 'Manchester', 'Birmingham'],
        'Australia': ['Sydney', 'Melbourne', 'Brisbane'],
        'Germany': ['Berlin', 'Munich', 'Hamburg'],
        'France': ['Paris', 'Lyon', 'Marseille']
    }
    
    for i in range(6, 51):  # Add customers 6-50
        country = random.choice(countries)
        city = random.choice(cities[country])
        reg_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
        
        additional_customers.append((
            i,
            f'Customer{i}',
            f'LastName{i}',
            f'customer{i}@email.com',
            reg_date.strftime('%Y-%m-%d'),
            country,
            city,
            random.choice([0, 1])
        ))
    
    cursor.executemany('''
    INSERT OR REPLACE INTO customers VALUES (?,?,?,?,?,?,?,?)
    ''', additional_customers)
    
    # Add more products
    categories = ['Electronics', 'Appliances', 'Apparel', 'Books', 'Sports', 'Home']
    additional_products = []
    
    for i in range(6, 21):  # Add products 6-20
        category = random.choice(categories)
        price = round(random.uniform(10, 500), 2)
        cost = round(price * random.uniform(0.4, 0.7), 2)
        
        additional_products.append((
            i,
            f'Product {i}',
            category,
            price,
            cost,
            f'Description for product {i}',
            '2023-01-01'
        ))
    
    cursor.executemany('''
    INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?)
    ''', additional_products)
    
    conn.commit()
    conn.close()
    print("Extended sample data added successfully!")

if __name__ == "__main__":
    add_extended_data()
