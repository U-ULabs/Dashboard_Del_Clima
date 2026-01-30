
import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from data_sources import siata, meteoblue, meteosource
from processing import transform, cleaning

def debug_pipeline():
    load_dotenv()
    print("Debugging Full Pipeline...")
    
    start_date = "2025-11-22"
    end_date = "2025-11-29"
    
    dfs = []
    
    print("\n1. Fetching SIATA...")
    try:
        df_siata = siata.fetch_siata(start=start_date, end=end_date)
        print(f"   SIATA raw rows: {len(df_siata)}")
        if not df_siata.empty:
            print(f"   SIATA columns: {df_siata.columns.tolist()}")
            df_siata_canon = transform.to_canonical(df_siata)
            print(f"   SIATA canonical rows: {len(df_siata_canon)}")
            dfs.append(df_siata_canon)
    except Exception as e:
        print(f"   SIATA Error: {e}")

    print("\n2. Fetching Meteoblue (Medellín)...")
    try:
        df_meteoblue = meteoblue.fetch_meteoblue(lat=6.2442, lon=-75.5812, location_name="Medellín", start=start_date, end=end_date)
        print(f"   Meteoblue raw rows: {len(df_meteoblue)}")
        if not df_meteoblue.empty:
            df_mb_canon = transform.to_canonical(df_meteoblue)
            print(f"   Meteoblue canonical rows: {len(df_mb_canon)}")
            dfs.append(df_mb_canon)
    except Exception as e:
        print(f"   Meteoblue Error: {e}")

    print("\n3. Fetching Meteosource (Medellín)...")
    try:
        df_meteosource = meteosource.fetch_meteosource(lat=6.2442, lon=-75.5812, location_name="Medellín", start=start_date, end=end_date)
        print(f"   Meteosource raw rows: {len(df_meteosource)}")
        if not df_meteosource.empty:
            df_ms_canon = transform.to_canonical(df_meteosource)
            print(f"   Meteosource canonical rows: {len(df_ms_canon)}")
            dfs.append(df_ms_canon)
    except Exception as e:
        print(f"   Meteosource Error: {e}")

    if dfs:
        print("\n4. Concatenating...")
        df_final = pd.concat(dfs, ignore_index=True)
        print(f"   Combined rows: {len(df_final)}")
        
        print("\n5. Cleaning...")
        # Start MLflow run for the pipeline
        import mlflow
        mlflow.set_experiment("Data_Pipeline")
        
        with mlflow.start_run(run_name="daily_ingestion"):
            df_final = cleaning.drop_duplicate_observations(df_final)
            print(f"   Final rows: {len(df_final)}")
            
            print("\n6. Source Distribution:")
            print(df_final['source'].value_counts())
            
            print("\n7. Saving to data/canonical.csv...")
            os.makedirs("data", exist_ok=True)
            output_path = "data/canonical.csv"
            df_final.to_csv(output_path, index=False)
            mlflow.log_artifact(output_path)
            
            print("\n8. Sample Data:")
            print(df_final.head())
            print(df_final.tail())
    else:
        print("\n❌ No data collected.")

if __name__ == "__main__":
    debug_pipeline()
