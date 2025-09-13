import sqlite3

class DatabaseConnection:
    """
    A class-based context manager for handling SQLite database connections.
    """
    def __init__(self, db_name):
        """
        Initialize the context manager with the database name.
        
        Args:
            db_name (str): The name of the SQLite database file.
        """
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """
        Open a database connection and return it.
        
        Returns:
            sqlite3.Connection: The open database connection.
        """
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the database connection.
        
        Args:
            exc_type: The type of the exception (if any).
            exc_value: The exception instance (if any).
            traceback: The traceback (if any).
        """
        if self.conn:
            self.conn.close()

# Example usage with the context manager
if __name__ == "__main__":
    try:
        with DatabaseConnection('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            print("Query results:", results)
    except Exception as e:
        print(f"Error executing query: {e}")