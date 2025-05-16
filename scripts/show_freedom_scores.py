import sqlite3
import pandas as pd
from pathlib import Path

def show_freedom_scores():
    """Display the contents of the freedom_scores table."""
    try:
        # Connect to database
        db_path = Path(__file__).parent.parent / 'database' / 'eu_trust_freedom.db'
        conn = sqlite3.connect(db_path)
        
        # Query to get freedom scores with country names
        query = """
        SELECT 
            c.country_name,
            f.freedom_score,
            f.civil_liberties_score,
            f.year
        FROM countries c
        JOIN freedom_scores f ON c.country_id = f.country_id
        ORDER BY c.country_name;
        """
        
        # Read into pandas DataFrame for nice display
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Set display options for better readability
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        print("\nFreedom Scores Table Contents:")
        print("==============================")
        print(df.to_string(index=False))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    show_freedom_scores() 