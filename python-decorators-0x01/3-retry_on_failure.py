import time
import sqlite3
import functools

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

def retry_on_failure(retries=3, delay=2):
    """
    A decorator that retries a function on failure up to a specified number of times.
    
    Args:
        retries: Number of retry attempts (default: 3).
        delay: Delay in seconds between retries (default: 2).
    
    Returns:
        wrapper: A function that retries the original function on exceptions.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries:
                        raise e  # Re-raise the exception on the final attempt
                    print(f"Attempt {attempt} failed with error: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    Fetches all users from the database.
    
    Args:
        conn: SQLite database connection.
    
    Returns:
        List of tuples containing the query results.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Example usage
if __name__ == "__main__":
    try:
        users = fetch_users_with_retry()
        print(users)
    except Exception as e:
        print(f"Failed to fetch users after retries: {e}")