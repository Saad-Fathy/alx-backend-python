import time
import sqlite3
import functools

query_cache = {}

def with_db_connection(func):
    """
    A decorator that handles opening and closing SQLite database connections.
    
    Args:
        func: The function to be decorated.
    
    Returns:
        wrapper: A function that manages the connection and calls the original function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

def cache_query(func):
    """
    A decorator that caches database query results based on the SQL query string.
    
    Args:
        func: The function to be decorated (e.g., fetch_users_with_cache).
    
    Returns:
        wrapper: A function that checks the cache before executing the query.
    """
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # Check if the query result is in the cache
        if query in query_cache:
            print(f"Returning cached result for query: {query}")
            return query_cache[query]
        # Execute the query and cache the result
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        print(f"Caching result for query: {query}")
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetches users from the database using the provided query, with caching.
    
    Args:
        conn: SQLite database connection.
        query: The SQL query to execute.
    
    Returns:
        List of tuples containing the query results.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Example usage
if __name__ == "__main__":
    try:
        # First call: Executes query and caches result
        users = fetch_users_with_cache(query="SELECT * FROM users")
        print("First call result:", users)
        
        # Second call: Uses cached result
        users_again = fetch_users_with_cache(query="SELECT * FROM users")
        print("Second call result:", users_again)
    except Exception as e:
        print(f"Error executing query: {e}")