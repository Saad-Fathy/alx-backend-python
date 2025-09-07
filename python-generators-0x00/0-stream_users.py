#!/usr/bin/python3
import mysql.connector
from mysql.connector import Error

def stream_users():
    """Generator function to stream rows from the user_data table one by one."""
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
            
            # Use one loop to yield rows as dictionaries
            for row in cursor:
                yield {
                    'user_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'age': int(row[3]) if row[3].is_integer() else float(row[3])
                }
                
    except Error as e:
        print(f"Error streaming data: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()