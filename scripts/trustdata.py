import pandas as pd
from pathlib import Path

def main():
    try:
        # 1. Set up paths
        script_dir = Path(__file__).parent
        data_path = script_dir.parent / "data" / "country_trust_results.csv"
        
        # 2. Read the CSV file
        df = pd.read_csv(data_path)
        
        # 3. Verify data
        print("\nLoaded data:")
        print(df)
        
        # 4. Data is already processed, so we can use it directly
        # You can add any additional processing or analysis here
        
        print("\nSuccess! Results:")
        print(df)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()