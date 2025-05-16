import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from pathlib import Path
import numpy as np

def analyze_trust_civil_liberties():
    """Analyze relationship between trust levels and civil liberties scores."""
    try:
        # Set up paths
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / "static" / "charts"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(script_dir.parent / 'database' / 'eu_trust_freedom.db')
        
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
        
        # Use full country names instead of codes, adjust rotation for better readability
        plt.xticks(x, df['country_name'], rotation=45, ha='right')
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
        
        # Adjust layout and figure size for longer country names
        plt.subplots_adjust(bottom=0.2)  # Make more room for country names
        
        # Save the chart
        plt.savefig(output_dir / 'trust_freedom_deviation.png',
                    bbox_inches='tight', dpi=300)
        plt.close()
        
        print("Trust vs Civil Liberties visualization generated successfully!")
            
    except Exception as e:
        print(f"Error analyzing trust and civil liberties: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_trust_civil_liberties() 