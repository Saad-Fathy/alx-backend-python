#!/usr/bin/python3
import mysql.connector
from mysql.connector import Error

def stream_users_in_batches(batch_size):
    """Generator function to stream rows from user_data table in batches."""
    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host="localhost",
            user="your_username",  # Replace with your MySQL username
            password="your_password",  # Replace with your MySQL password
            database="ALX_prodev"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            # Execute query to fetch all rows from user_data
            cursor.execute("SELECT user_id, name, email, age FROM user_data")
            
            # Fetch rows in batches (Loop 1)
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                # Yield batch as a list of dictionaries (Loop 2)
                yield [
                    {
                        'user_id': row[0],
                        'name': row[1],
                        'email': row[2],
                        'age': int(row[3]) if row[3].is_integer() else float(row[3])
                    }
                    for row in rows
                ]
                
    except Error as e:
        print(f"Error streaming data: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def batch_processing(batch_size):
    """Generator function to process batches and filter users over age 25."""
    # Iterate over batches from stream_users_in_batches (Loop 3)
    for batch in stream_users_in_batches(batch_size):
        # Filter users over age 25 and yield individually
        for user in batch:
            if user['age'] > 25:
                yield user