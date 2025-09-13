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

def transactional(func):
    """
    A decorator that manages database transactions, committing on success or rolling back on failure.
    
    Args:
        func: The function to be decorated (e.g., update_user_email).
    
    Returns:
        wrapper: A function that wraps the operation in a transaction.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function within a transaction
            result = func(conn, *args, **kwargs)
            # Commit the transaction if no errors occur
            conn.commit()
            return result
        except Exception as e:
            # Roll back the transaction if an error occurs
            conn.rollback()
            raise e  # Re-raise the exception to maintain error visibility
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """
    Updates a user's email in the database.
    
    Args:
        conn: SQLite database connection.
        user_id: The ID of the user to update.
        new_email: The new email address to set.
    
    Returns:
        None
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

# Example usage
if __name__ == "__main__":
    try:
        update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
        print("Email updated successfully")
    except Exception as e:
        print(f"Error updating email: {e}")