from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path


app = Flask(__name__)

# Define EU member states for filtering
EU_COUNTRIES = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia',
    'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'EE': 'Estonia',
    'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'GR': 'Greece',
    'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands',
    'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SK': 'Slovakia',
    'SI': 'Slovenia', 'ES': 'Spain', 'SE': 'Sweden'
}

def get_db_connection():
    """Create a database connection."""
    try:
        conn = sqlite3.connect('database/eu_trust_freedom.db')
        conn.row_factory = sqlite3.Row
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Available tables:", [table[0] for table in tables])
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

@app.route('/')
def index():
    """Render the home page with map."""
    try:
        conn = get_db_connection()
        
        # First, check if we have data for 2024
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT year FROM freedom_scores ORDER BY year DESC")
        available_years = [row[0] for row in cursor.fetchall()]
        print("Available years:", available_years)
        
        if not available_years:
            raise Exception("No data found in freedom_scores table")
            
        latest_year = available_years[0]
        print(f"Using data for year: {latest_year}")
        
        # Get civil liberties data for EU countries
        data = conn.execute('''
            SELECT 
                c.country_code,
                c.country_name,
                f.civil_liberties_score,
                f.freedom_expression_belief,
                f.associational_rights,
                f.rule_of_law,
                f.personal_autonomy,
                f.year
            FROM countries c
            JOIN freedom_scores f ON c.country_id = f.country_id
            WHERE c.country_code IN (
                'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
                'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
            )
            AND f.year = ?
        ''', [latest_year]).fetchall()
        
        # Debug print raw data
        print("\nRaw data from database:")
        for row in data:
            print(f"Country: {row['country_code']}, Score: {row['civil_liberties_score']}")
        
        # Convert to dictionary for JavaScript - keep country codes in uppercase
        civil_liberties_data = {
            row['country_code']: {
                'country_name': row['country_name'],
                'civil_liberties_score': float(row['civil_liberties_score']) if row['civil_liberties_score'] is not None else None,
                'freedom_expression_belief': float(row['freedom_expression_belief']) if row['freedom_expression_belief'] is not None else None,
                'associational_rights': float(row['associational_rights']) if row['associational_rights'] is not None else None,
                'rule_of_law': float(row['rule_of_law']) if row['rule_of_law'] is not None else None,
                'personal_autonomy': float(row['personal_autonomy']) if row['personal_autonomy'] is not None else None,
                'year': row['year']
            } for row in data
        }
        
        # Debug print
        print("\nProcessed civil liberties data:")
        print(civil_liberties_data)
        
        if not civil_liberties_data:
            print("\nWarning: No civil liberties data found in database")
            print("Checking database tables...")
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            print("Tables in database:", [table[0] for table in tables])
            print("\nChecking freedom_scores records...")
            count = conn.execute("SELECT COUNT(*) FROM freedom_scores;").fetchone()[0]
            print(f"Total freedom_scores records: {count}")
            
        conn.close()
        return render_template('index.html', civil_liberties_data=civil_liberties_data)
        
    except Exception as e:
        print(f"Error in index route: {e}")
        import traceback
        traceback.print_exc()
        # Return empty data with error flag
        return render_template('index.html', 
                             civil_liberties_data={},
                             error_message=f"Failed to load civil liberties data: {str(e)}")

@app.route('/trust')
def trust():
    """Render the trust levels analysis page."""
    try:
        conn = get_db_connection()
        # Get combined trust and freedom data with civil liberties scores
        trust_data = conn.execute('''
            SELECT 
                c.country_name,
                t.trust_score,
                t.response_count,
                f.freedom_score,
                f.civil_liberties_score
            FROM countries c 
            JOIN trust_levels t ON c.country_id = t.country_id 
            LEFT JOIN freedom_scores f ON c.country_id = f.country_id
            ORDER BY t.trust_score DESC
        ''').fetchall()
        conn.close()
        return render_template('trust.html', trust_data=trust_data)
    except Exception as e:
        print(f"Database error: {e}")
        return render_template('trust.html', trust_data=[])

@app.route('/freedomindex')
def freedomindex():
    """Render the freedom index builder page."""
    return render_template('freedomindex.html')



@app.route('/isyour')
def isyour():
    """Render the country analysis page."""
    try:
        # Read FIW data, skipping the first few rows until we find the header
        with open('data/FIW2024.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Find the header row
        header_row = 0
        for i, line in enumerate(lines):
            if 'Country' in line and 'Edition' in line:
                header_row = i
                break
        
        # Create a DataFrame from the data after the header
        data_rows = []
        columns = [col.strip().strip('"') for col in lines[header_row].split(';')]
        
        for line in lines[header_row + 1:]:
            if line.strip():  # Skip empty lines
                values = [val.strip().strip('"') for val in line.split(';')]
                if len(values) == len(columns):  # Only add rows with correct number of columns
                    data_rows.append(values)
        
        df = pd.DataFrame(data_rows, columns=columns)
        
        # Get unique EU countries
        eu_countries = sorted(list(EU_COUNTRIES.values()))
        return render_template('isyour.html', countries=eu_countries)
    except Exception as e:
        print(f"Error reading data: {e}")
        return render_template('isyour.html', countries=[])

@app.route('/get_country_history', methods=['GET'])
def get_country_history():
    """Get historical civil liberties data for a specific country."""
    country = request.args.get('country')
    if not country:
        return jsonify({'error': 'No country specified'}), 400
        
    try:
        # Read FIW data, skipping the first few rows until we find the header
        with open('data/FIW2024.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Find the header row
        header_row = 0
        for i, line in enumerate(lines):
            if 'Country' in line and 'Edition' in line:
                header_row = i
                break
        
        # Create a DataFrame from the data after the header
        data_rows = []
        columns = [col.strip().strip('"') for col in lines[header_row].split(';')]
        
        for line in lines[header_row + 1:]:
            if line.strip():  # Skip empty lines
                values = [val.strip().strip('"') for val in line.split(';')]
                if len(values) == len(columns):  # Only add rows with correct number of columns
                    data_rows.append(values)
        
        df = pd.DataFrame(data_rows, columns=columns)
        
        # Filter for the specified country
        country_data = df[df['Country/Territory'] == country].copy()
        
        if country_data.empty:
            return jsonify({'error': 'Country not found or no data available'}), 404
            
        # Extract year and civil liberties score
        country_data['year'] = pd.to_numeric(country_data['Edition'])
        country_data['civil_liberties_score'] = pd.to_numeric(country_data['CL'])
        
        # Sort by year and select relevant columns
        result_data = country_data[['year', 'civil_liberties_score']].sort_values('year')
        
        # Convert to list of dictionaries
        results = result_data.to_dict('records')
        return jsonify({'data': results})
        
    except Exception as e:
        print(f"Error reading data: {e}")
        return jsonify({'error': f'Failed to get historical data for {country}'}), 500

@app.route('/get_country_data', methods=['GET'])
def get_country_data():
    """Get data for a specific country."""
    country = request.args.get('country')
    try:
        conn = get_db_connection()
        # Get both trust and freedom data for the country
        data = conn.execute('''
            SELECT 
                c.country_name,
                t.trust_score,
                t.response_count,
                f.freedom_score
            FROM countries c 
            JOIN trust_levels t ON c.country_id = t.country_id 
            LEFT JOIN freedom_scores f ON c.country_id = f.country_id 
            WHERE c.country_name = ? 
        ''', (country,)).fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        results = [dict(row) for row in data]
        return jsonify({'data': results})
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': f'Failed to get data for {country}'}), 500

@app.route('/get_eu_countries')
def get_eu_countries():
    """Get list of EU countries."""
    try:
        conn = get_db_connection()
        countries = conn.execute('''
            SELECT DISTINCT c.country_name 
            FROM countries c
            JOIN trust_levels t ON c.country_id = t.country_id
            ORDER BY c.country_name
        ''').fetchall()
        conn.close()
        return jsonify({'countries': [country['country_name'] for country in countries]})
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Failed to get country list'}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
