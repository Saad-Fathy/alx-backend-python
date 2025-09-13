import sqlite3

class ExecuteQuery:
    """
    A reusable context manager for executing parameterized SQL queries.
    """
    def __init__(self, db_name, query, params=()):
        """
        Initialize the context manager with database name, query, and parameters.
        
        Args:
            db_name (str): The name of the SQLite database file.
            query (str): The SQL query to execute.
            params (tuple): Parameters for the query (default: empty tuple).
        """
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Open a database connection, create a cursor, execute the query, and return results.
        
        Returns:
            list: The query results as a list of tuples.
        """
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the cursor and database connection.
        
        Args:
            exc_type: The type of the exception (if any).
            exc_value: The exception instance (if any).
            traceback: The traceback (if any).
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# Example usage with the context manager
if __name__ == "__main__":
    try:
        query = "SELECT * FROM users WHERE age > ?"
        with ExecuteQuery('users.db', query, (25,)) as results:
            print("Query results:", results)
    except Exception as e:
        print(f"Error executing query: {e}")