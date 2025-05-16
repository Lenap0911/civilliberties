import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def create_trust_civil_liberties_chart():
    """Create a chart comparing trust in legal systems with civil liberties scores."""
    # Connect to database
    db_path = Path(__file__).parent.parent / 'database' / 'eu_trust_freedom.db'
    conn = sqlite3.connect(db_path)
    
    # Get combined data
    query = """
    SELECT 
        c.country_name,
        c.country_code,
        t.trust_score,
        f.civil_liberties_score
    FROM countries c
    JOIN trust_levels t ON c.country_id = t.country_id
    JOIN freedom_scores f ON c.country_id = f.country_id
    WHERE t.year = 2024 AND f.year = 2024
    ORDER BY t.trust_score DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Create output directory
    charts_folder = Path(__file__).parent.parent / 'static' / 'charts'
    charts_folder.mkdir(exist_ok=True)
    
    # Create the comparison chart
    plt.figure(figsize=(15, 8))
    
    # Set up bar positions
    x = np.arange(len(df))
    width = 0.35
    
    # Create bars
    plt.bar(x - width/2, df['trust_score'], width, 
            label='Trust in Legal System (0-10)', color='#2ecc71', alpha=0.7)
    plt.bar(x + width/2, df['civil_liberties_score'], width,
            label='Civil Liberties Score', color='#3498db', alpha=0.7)
    
    # Customize the chart
    plt.xlabel('Countries')
    plt.ylabel('Scores')
    plt.title('Trust in Legal Systems vs Civil Liberties by Country', pad=20)
    plt.xticks(x, df['country_code'], rotation=45)
    plt.legend()
    
    # Add value labels on bars
    for i in x:
        plt.text(i - width/2, df['trust_score'].iloc[i], 
                f'{df["trust_score"].iloc[i]:.1f}', 
                ha='center', va='bottom')
        plt.text(i + width/2, df['civil_liberties_score'].iloc[i],
                f'{df["civil_liberties_score"].iloc[i]:.1f}',
                ha='center', va='bottom')
    
    # Add grid for better readability
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    plt.savefig(charts_folder / 'trust_freedom_deviation.png',
                bbox_inches='tight', dpi=300)
    plt.close()

def main():
    """Create all visualizations."""
    create_trust_civil_liberties_chart()

if __name__ == "__main__":
    main()