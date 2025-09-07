#!/usr/bin/python3
"""
Memory-efficient aggregation module using generators.
This module calculates the average age of users without loading all data into memory.
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


def stream_user_ages():
    """
    Generator function that yields user ages one by one from the database.
    This approach is memory-efficient as it doesn't load all records at once.
    
    Yields:
        int: User age
    """
    connection = connect_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row[0]  # row[0] is the age column
                
    except Error as e:
        print(f"Error fetching data: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def calculate_average_age():
    """
    Calculates the average age of all users using the generator.
    This function processes ages one by one without loading all data into memory.
    
    Returns:
        float: Average age of users, or 0 if no users found
    """
    total_age = 0
    count = 0
    
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count == 0:
        return 0
    
    return total_age / count


def main():
    """
    Main function that calculates and prints the average age.
    """
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age:.2f}")


if __name__ == "__main__":
    main()