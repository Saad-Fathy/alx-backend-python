#!/usr/bin/python3
"""
Batch processing module for handling large datasets using generators.
This module provides functions to stream and process user data in batches.
"""

import mysql.connector
from mysql.connector import Error


def connect_db():
    """
    Establishes connection to the MySQL database.
    
    Returns:
        mysql.connector.connection: Database connection object or None if failed
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ALX_prodev',
            user='root',
            password='root'
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


def stream_users_in_batches(batch_size):
    """
    Generator function that fetches users from database in batches.
    
    Args:
        batch_size (int): Number of records to fetch per batch
        
    Yields:
        list: Batch of user records as dictionaries
    """
    connection = connect_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
                
    except Error as e:
        print(f"Error fetching data: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def batch_processing(batch_size):
    """
    Processes batches of users and filters those over age 25.
    
    Args:
        batch_size (int): Size of each batch to process
        
    Prints filtered user records to stdout.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)