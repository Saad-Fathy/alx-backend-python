import asyncio
import aiosqlite

async def async_fetch_users():
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        list: List of tuples containing all user records.
    """
    async with aiosqlite.connect('users.db') as conn:
        cursor = await conn.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        list: List of tuples containing user records with age > 40.
    """
    async with aiosqlite.connect('users.db') as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE age > ?", (40,))
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def fetch_concurrently():
    """
    Execute async_fetch_users and async_fetch_older_users concurrently.
    
    Returns:
        tuple: Results of both queries (all users, older users).
    """
    results = await asyncio.gather(async_fetch_users(), async_fetch_older_users())
    return results

# Example usage
if __name__ == "__main__":
    try:
        # Run the concurrent fetch
        all_users, older_users = asyncio.run(fetch_concurrently())
        print("All users:", all_users)
        print("Users older than 40:", older_users)
    except Exception as e:
        print(f"Error executing queries: {e}")