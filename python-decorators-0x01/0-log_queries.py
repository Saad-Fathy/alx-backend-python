import sqlite3
import functools
import logging
from datetime import datetime  # Added import

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')  # Removed asctime to use custom datetime

def log_queries(func):
    """
    A decorator that logs the SQL query with a custom timestamp before executing the decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = args[0] if args else "No query provided"
        # Use datetime for custom timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"{timestamp} - Executing query: {query}")
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    """
    Fetches all users from the database using the provided SQL query.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)