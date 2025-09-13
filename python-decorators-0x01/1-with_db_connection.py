import sqlite3
import functools

def with_db_connection(func):
    """
    A decorator that handles opening and closing SQLite database connections.
    
    Args:
        func: The function to be decorated (e.g., get_user_by_id).
    
    Returns:
        wrapper: A function that manages the connection and calls the original function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open a connection to the database
        conn = sqlite3.connect('users.db')
        try:
            # Call the original function, passing the connection as the first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Ensure the connection is closed, even if an error occurs
            conn.close()
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetches a user from the database by their ID.
    
    Args:
        conn: SQLite database connection.
        user_id: The ID of the user to fetch.
    
    Returns:
        A tuple containing the user data, or None if not found.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Example usage
if __name__ == "__main__":
    user = get_user_by_id(user_id=1)
    print(user)