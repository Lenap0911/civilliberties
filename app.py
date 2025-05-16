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
    """Render the freedom compass page."""
    return render_template('freedom_compass.html')

@app.route('/calculate', methods=['POST'])
def calculate_freedom_match():
    """Calculate freedom index matches based on user ideal profile (distance)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input."}), 400

        # User input: 0-100 scale, convert to 0-4 scale
        def scale_to_four(val):
            try:
                v = float(val)
                return max(0, min(4, round(v / 25)))  # 0-24=0, 25-49=1, 50-74=2, 75-99=3, 100=4
            except Exception:
                return 0

        # User weights as 0-1 scale for weighting distance
        user_weights = [
            max(0, min(1, float(data.get('weight1', 25)) / 100)),
            max(0, min(1, float(data.get('weight2', 25)) / 100)),
            max(0, min(1, float(data.get('weight3', 25)) / 100)),
            max(0, min(1, float(data.get('weight4', 25)) / 100)),
        ]
        user_profile = [
            scale_to_four(data.get('weight1', 25)),
            scale_to_four(data.get('weight2', 25)),
            scale_to_four(data.get('weight3', 25)),
            scale_to_four(data.get('weight4', 25)),
        ]

        # Load FIW2024.csv data
        try:
            csv_path = Path('data/FIW2024.csv')
            if not csv_path.exists():
                return jsonify({"error": "Freedom index data not found."}), 500

            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            header_row = 0
            for i, line in enumerate(lines):
                if 'Country/Territory' in line and 'Edition' in line:
                    header_row = i
                    break
            data_rows = []
            columns = [col.strip().strip('"') for col in lines[header_row].split(';')]
            for line in lines[header_row + 1:]:
                if line.strip():
                    values = [val.strip().strip('"') for val in line.split(';')]
                    if len(values) == len(columns):
                        data_rows.append(values)
            df = pd.DataFrame(data_rows, columns=columns)

            eu_country_names = set(EU_COUNTRIES.values())
            df = df[(df["Edition"] == "2024") & (df["Country/Territory"].isin(eu_country_names))]
            if df.empty:
                return jsonify({"error": "No matching data found for EU countries in 2024."}), 404

            required_cols = ["G1", "G2", "G3", "G4"]
            for col in required_cols:
                if col not in df.columns:
                    return jsonify({"error": f"Missing column {col} in CSV data."}), 500
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Compute weighted Euclidean distance to user profile
            def weighted_distance(row):
                num = 0.0
                denom = 0.0
                for i, c in enumerate(["G1", "G2", "G3", "G4"]):
                    w = user_weights[i]
                    if pd.isna(row[c]):
                        continue  # skip missing data
                    num += w * (user_profile[i] - row[c]) ** 2
                    denom += w
                # If all weights are zero or all missing, treat as max distance
                if denom == 0:
                    return float('inf')
                return (num / denom) ** 0.5
            df["distance"] = df.apply(weighted_distance, axis=1)
            top = df.sort_values("distance").head(3)
            min_dist = top["distance"].min()
            max_dist = top["distance"].max()

            # For display, convert distance to a match percentage (closer = higher)
            def dist_to_match(dist):
                # If all distances are the same, just return 100
                if max_dist == min_dist:
                    return 100.0
                # Otherwise, invert and scale
                return round(100 * (1 - (dist - min_dist) / (max_dist - min_dist)), 1)

            results = []
            for _, row in top.iterrows():
                results.append({
                    "country": row["Country/Territory"],
                    "match_percentage": dist_to_match(row["distance"]),
                    "scores": {
                        "movement": float(row["G1"]),
                        "property": float(row["G2"]),
                        "social": float(row["G3"]),
                        "equality": float(row["G4"])
                    }
                })
            return jsonify({
                "matches": results,
                "user_input": {
                    "movement": data.get('weight1', 25),
                    "property": data.get('weight2', 25),
                    "social": data.get('weight3', 25),
                    "equality": data.get('weight4', 25)
                },
                "user_scaled": {
                    "movement": user_profile[0],
                    "property": user_profile[1],
                    "social": user_profile[2],
                    "equality": user_profile[3]
                }
            })

        except Exception as e:
            print(f"Error processing CSV data: {e}")
            return jsonify({"error": f"Data processing error: {str(e)}"}), 500

    except Exception as e:
        print(f"Error in calculate_freedom_match: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/isyour')
def isyour():
    """Render the country analysis page."""
    try:
        # Get EU countries directly from the database
        conn = get_db_connection()
        data = conn.execute('''
            SELECT DISTINCT c.country_name
            FROM countries c
            WHERE c.country_code IN (
                'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
                'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
            )
            ORDER BY c.country_name
        ''').fetchall()
        
        eu_countries = [row['country_name'] for row in data]
        conn.close()
        return render_template('isyour.html', countries=eu_countries)
    except Exception as e:
        print(f"Error reading data: {e}")
        return render_template('isyour.html', countries=[])

@app.route('/get_country_history')
def get_country_history():
    """Get historical civil liberties data for a specific country."""
    try:
        country = request.args.get('country')
        if not country:
            return jsonify({'error': 'Country parameter is required'})

        conn = get_db_connection()
        data = conn.execute('''
            SELECT 
                f.year,
                f.civil_liberties_score
            FROM countries c
            JOIN freedom_scores f ON c.country_id = f.country_id
            WHERE c.country_name = ?
            AND f.year BETWEEN 2013 AND 2024
            ORDER BY f.year
        ''', [country]).fetchall()
        
        conn.close()

        if not data:
            return jsonify({'error': 'No data found for the specified country'})

        return jsonify({
            'data': [{'year': row['year'], 'civil_liberties_score': row['civil_liberties_score']} for row in data]
        })

    except Exception as e:
        print(f"Error fetching country history: {e}")
        return jsonify({'error': 'Failed to fetch country data'})

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
