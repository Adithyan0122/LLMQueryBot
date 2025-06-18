import sqlite3

def truncate_database(db_name):
    """
    Truncate all tables in the specified SQLite database.
    
    Args:
        db_name (str): Name of the SQLite database file
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Get list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        
        # Truncate each table
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"DELETE FROM {table_name}")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")  # Reset autoincrement
                print(f"Truncated table: {table_name}")
            except sqlite3.Error as e:
                print(f"Error truncating table {table_name}: {e}")
        
        # Commit changes and re-enable foreign keys
        conn.commit()
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("Database truncation completed successfully.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# Usage
truncate_database('data/examples.db')