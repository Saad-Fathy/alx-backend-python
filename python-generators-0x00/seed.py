#!/usr/bin/python3
import mysql.connector
import csv
import uuid
from mysql.connector import Error

def connect_db():
    """Connects to the MySQL database server."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_username",  # Replace with your MySQL username
            password="your_password"  # Replace with your MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Creates the ALX_prodev database if it does not exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        connection.commit()
        print("Database ALX_prodev created successfully or already exists")
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()

def connect_to_prodev():
    """Connects to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_username",  # Replace with your MySQL username
            password="your_password",  # Replace with your MySQL password
            database="ALX_prodev"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None

def create_table(connection):
    """Creates the user_data table if it does not exist."""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL,
            INDEX idx_user_id (user_id)
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()

def insert_data(connection, csv_file):
    """Inserts data from the CSV file into the user_data table if it does not exist."""
    try:
        cursor = connection.cursor()
        with open(csv_file, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Check if user_id already exists
                cursor.execute("SELECT user_id FROM user_data WHERE user_id = %s", (row['user_id'],))
                if cursor.fetchone():
                    continue  # Skip if user_id exists
                
                # Insert data
                insert_query = """
                INSERT INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
                """
                # Ensure user_id is a valid UUID
                user_id = str(uuid.UUID(row['user_id'])) if row['user_id'] else str(uuid.uuid4())
                data = (user_id, row['name'], row['email'], float(row['age']))
                cursor.execute(insert_query, data)
        
        connection.commit()
        print("Data inserted successfully")
    except Error as e:
        print(f"Error inserting data: {e}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    finally:
        cursor.close()

def stream_user_data():
    """Generator function to stream rows from the user_data table one by one."""
    connection = connect_to_prodev()
    if not connection:
        print("Failed to connect to database")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        for row in cursor:
            yield row  # Yield one row at a time
    except Error as e:
        print(f"Error streaming data: {e}")
    finally:
        cursor.close()
        connection.close()