import sqlite3

def check_tables():
    try:
        conn = sqlite3.connect('database/eu_trust_freedom.db')
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get sample data
            try:
                cursor.execute(f"SELECT * FROM {table[0]} LIMIT 1;")
                row = cursor.fetchone()
                if row:
                    print("\nSample row:")
                    for i, col in enumerate(columns):
                        print(f"  - {col[1]}: {row[i]}")
            except Exception as e:
                print(f"Error getting sample data: {e}")
            print("\n" + "-"*50)
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == '__main__':
    check_tables()
