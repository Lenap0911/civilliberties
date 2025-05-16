import sqlite3
from pathlib import Path

def main():
    try:
        # Connect to database
        db_path = Path(__file__).parent.parent / 'database' / 'eu_trust_freedom.db'
        conn = sqlite3.connect(db_path)
        
        # Get all countries
        cursor = conn.execute('''
            SELECT c.country_name, c.country_code, 
                   t.trust_score, f.civil_liberties_score
            FROM countries c
            LEFT JOIN trust_levels t ON c.country_id = t.country_id
            LEFT JOIN freedom_scores f ON c.country_id = f.country_id
            ORDER BY c.country_name
        ''')
        
        print("\nCountries in database:")
        print("=" * 70)
        print(f"{'Country':<30} {'Code':<6} {'Trust':<10} {'Civil Liberties'}")
        print("-" * 70)
        
        for row in cursor:
            print(f"{row[0]:<30} {row[1]:<6} {row[2] if row[2] else 'N/A':<10} {row[3] if row[3] else 'N/A'}")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 