import pandas as pd
import sqlite3
from pathlib import Path

# Define EU member states
EU_COUNTRIES = {
    'AT': 'Austria',
    'BE': 'Belgium',
    'BG': 'Bulgaria',
    'HR': 'Croatia',
    'CY': 'Cyprus',
    'CZ': 'Czech Republic',
    'DK': 'Denmark',
    'EE': 'Estonia',
    'FI': 'Finland',
    'FR': 'France',
    'DE': 'Germany',
    'GR': 'Greece',
    'HU': 'Hungary',
    'IE': 'Ireland',
    'IT': 'Italy',
    'LV': 'Latvia',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'MT': 'Malta',
    'NL': 'Netherlands',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'SK': 'Slovakia',
    'SI': 'Slovenia',
    'ES': 'Spain',
    'SE': 'Sweden'
}

def process_trust_data(file_path):
    """Process trust data from the CSV file."""
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Filter for EU countries only
        df = df[df['code'].isin(EU_COUNTRIES.keys())]
        
        print("\nTrust data summary (EU countries only):")
        print(df)
        return df
    except Exception as e:
        print(f"Error reading trust data: {str(e)}")
        raise

def process_historical_fiw_data(base_path):
    """Process historical Freedom in the World data from 2013-2024."""
    all_data = []
    
    for year in range(2013, 2025):
        file_path = base_path / f'FIW{year}.csv'
        if not file_path.exists():
            print(f"Warning: Data file for {year} not found")
            continue
            
        try:
            # Read the CSV file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
                # Find the header row
        header_row = 0
        for i, line in enumerate(lines):
            if 'Country' in line or 'Territory' in line:
                header_row = i
                break
        
        # Clean up column names
        header = lines[header_row].strip()
        columns = [col.strip().strip('"') for col in header.split(';')]
        
        # Read data starting from the row after header
        data_rows = []
        for line in lines[header_row + 1:]:
            if line.strip():  # Skip empty lines
                values = [val.strip().strip('"') for val in line.split(';')]
                if len(values) == len(columns):  # Only add rows with correct number of columns
                    data_rows.append(values)
        
        # Create DataFrame
                df = pd.DataFrame(data_rows, columns=columns)
      
                # Filter for EU countries
                df = df[df['Country/Territory'].isin(EU_COUNTRIES.values())]
                
                # Add year column
                df['Year'] = year
                
                # Convert scores to numeric
                df['CL'] = pd.to_numeric(df['CL'], errors='coerce')  # Civil liberties score
                
                # Keep only necessary columns
                df = df[['Country/Territory', 'Year', 'CL']]
                
                all_data.append(df)
                
        except Exception as e:
            print(f"Error processing {year} data: {e}")
            continue
    
    # Combine all years
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        raise ValueError("No historical data could be processed")

def create_database():
    """Create the SQLite database with tables."""
    db_path = Path(__file__).parent.parent / 'database' / 'eu_trust_freedom.db'
    conn = sqlite3.connect(db_path)
    
    # Create tables
    conn.execute('''
    CREATE TABLE IF NOT EXISTS countries (
        country_id INTEGER PRIMARY KEY,
            country_name VARCHAR(100) NOT NULL,
            country_code CHAR(2) NOT NULL UNIQUE
        )
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS trust_levels (
        trust_id INTEGER PRIMARY KEY,
        country_id INTEGER,
        year INTEGER NOT NULL,
        trust_score DECIMAL(4,2),
        response_count INTEGER NOT NULL,
        FOREIGN KEY (country_id) REFERENCES countries(country_id),
        UNIQUE(country_id, year)
        )
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS freedom_scores (
        freedom_id INTEGER PRIMARY KEY,
        country_id INTEGER,
        year INTEGER NOT NULL,
            civil_liberties_score DECIMAL(4,2),
        FOREIGN KEY (country_id) REFERENCES countries(country_id),
        UNIQUE(country_id, year)
        )
    ''')

    return conn

def main():
    try:
    # Process data
        trust_data = process_trust_data(Path(__file__).parent.parent / 'data' / 'country_trust_results.csv')
        historical_data = process_historical_fiw_data(Path(__file__).parent.parent / 'data')
    
    # Create database
    conn = create_database()
    
    try:
            # Insert countries (EU only)
        for code, name in EU_COUNTRIES.items():
            conn.execute('INSERT OR IGNORE INTO countries (country_name, country_code) VALUES (?, ?)',
                       (name, code))
        
        # Insert trust levels
            for _, row in trust_data.iterrows():
                if row['code'] in EU_COUNTRIES:
            country_id = conn.execute('SELECT country_id FROM countries WHERE country_code = ?',
                                           (row['code'],)).fetchone()[0]
            conn.execute('''
                        INSERT OR REPLACE INTO trust_levels (country_id, trust_score, response_count, year)
                        VALUES (?, ?, ?, ?)
                    ''', (country_id, float(row['avg_trust']), int(row['response_count']), 2024))
        
            # Insert historical freedom scores
            for _, row in historical_data.iterrows():
                # Find matching country code
                country_code = next((code for code, name in EU_COUNTRIES.items() 
                                   if name == row['Country/Territory']), None)
                if country_code:
                    country_id = conn.execute('SELECT country_id FROM countries WHERE country_code = ?',
                                           (country_code,)).fetchone()[0]
            conn.execute('''
                        INSERT OR REPLACE INTO freedom_scores (
                            country_id,
                            civil_liberties_score,
                            year
                        ) VALUES (?, ?, ?)
                    ''', (
                        country_id,
                        float(row['CL']),
                        int(row['Year'])
                    ))
        
        conn.commit()
            print("\nDatabase updated successfully with historical data!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()
            
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()
