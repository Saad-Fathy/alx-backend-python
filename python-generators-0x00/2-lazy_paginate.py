#!/usr/bin/python3
"""
Lazy pagination module for efficiently loading paginated data from database.
This module provides a generator-based approach to fetch data page by page.
"""

import seed


def paginate_users(page_size, offset):
    """
    Fetches a page of users from the database.
    
    Args:
        page_size (int): Number of records to fetch per page
        offset (int): Starting position for the page
        
    Returns:
        list: List of user records as dictionaries
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_paginate(page_size):
    """
    Generator function that lazily loads paginated user data.
    Only fetches the next page when needed.
    
    Args:
        page_size (int): Number of records per page
        
    Yields:
        list: Page of user records as dictionaries
    """
    offset = 0
    
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size


# Alias for the function name used in the test
lazy_pagination = lazy_paginate