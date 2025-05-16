import sqlite3
import os

# EU countries data
EU_COUNTRIES = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia',
    'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'EE': 'Estonia',
    'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'GR': 'Greece',
    'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands',
    'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SK': 'Slovakia',
    'SI': 'Slovenia', 'ES': 'Spain', 'SE': 'Sweden'
}

# Sample civil liberties data for 2024 (for demonstration)
CIVIL_LIBERTIES_DATA = {
    'AT': (58, 16, 12, 15, 15), 'BE': (57, 15, 12, 15, 15),
    'BG': (48, 13, 10, 12, 13), 'HR': (52, 14, 11, 13, 14),
    'CY': (55, 15, 11, 14, 15), 'CZ': (53, 14, 11, 14, 14),
    'DK': (59, 16, 12, 15, 16), 'EE': (56, 15, 11, 15, 15),
    'FI': (59, 16, 12, 15, 16), 'FR': (52, 14, 11, 13, 14),
    'DE': (58, 15, 12, 15, 16), 'GR': (51, 14, 10, 13, 14),
    'HU': (44, 11, 9, 12, 12), 'IE': (57, 15, 12, 15, 15),
    'IT': (53, 14, 11, 14, 14), 'LV': (53, 14, 11, 14, 14),
    'LT': (54, 14, 11, 14, 15), 'LU': (58, 16, 12, 15, 15),
    'MT': (55, 15, 11, 14, 15), 'NL': (58, 16, 12, 15, 15),
    'PL': (48, 13, 10, 12, 13), 'PT': (56, 15, 11, 15, 15),
    'RO': (49, 13, 10, 13, 13), 'SK': (51, 14, 10, 13, 14),
    'SI': (54, 14, 11, 14, 15), 'ES': (55, 15, 11, 14, 15),
    'SE': (59, 16, 12, 15, 16)
}

def init_db():
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('database/eu_trust_freedom.db')
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.executescript('''
        DROP TABLE IF EXISTS freedom_scores;
        DROP TABLE IF EXISTS trust_levels;
        DROP TABLE IF EXISTS countries;
    ''')
    
    # Read schema
    with open('database/schema.sql', 'r') as f:
        schema = f.read()
    
    # Execute schema
    cursor.executescript(schema)
    
    # Insert countries
    for code, name in EU_COUNTRIES.items():
        cursor.execute(
            'INSERT INTO countries (country_code, country_name) VALUES (?, ?)',
            (code, name)
        )
    
    # Insert freedom scores
    year = 2024
    for code, scores in CIVIL_LIBERTIES_DATA.items():
        # Get country_id
        cursor.execute('SELECT country_id FROM countries WHERE country_code = ?', (code,))
        country_id = cursor.fetchone()[0]
        
        # Insert freedom scores
        cursor.execute('''
            INSERT INTO freedom_scores (
                country_id, year, civil_liberties_score,
                freedom_expression_belief, associational_rights,
                rule_of_law, personal_autonomy
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (country_id, year, scores[0], scores[1], scores[2], scores[3], scores[4]))
    
    # Commit changes
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
