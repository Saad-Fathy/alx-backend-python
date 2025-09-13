import sqlite3
import functools
import logging

# Configure logging to display query information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_queries(func):
    """
    A decorator that logs the SQL query before executing the decorated function.
    
    Args:
        func: The function to be decorated (e.g., fetch_all_users).
    
    Returns:
        wrapper: A function that logs the query and calls the original function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from the arguments (assuming query is the first argument)
        query = args[0] if args else "No query provided"
        # Log the query
        logging.info(f"Executing query: {query}")
        # Call the original function with its arguments and return the result
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    """
    Fetches all users from the database using the provided SQL query.
    
    Args:
        query: The SQL query to execute.
    
    Returns:
        List of tuples containing the query results.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example usage
if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)