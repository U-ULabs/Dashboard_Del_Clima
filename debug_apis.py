
import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from data_sources import meteoblue, meteosource

def debug_apis():
    load_dotenv()
    print("Debugging Data Sources...")
    
    # Check Env Vars
    mb_key = os.getenv("METEOBLUE_API_KEY")
    ms_key = os.getenv("METEOSOURCE_API_KEY")
    
    print(f"Meteoblue Key present: {bool(mb_key)} (Value: {mb_key[:5]}...)")
    print(f"Meteosource Key present: {bool(ms_key)} (Value: {ms_key[:5]}...)")
    
    # Test Meteoblue
    print("\nTesting Meteoblue...")
    try:
        df_mb = meteoblue.fetch_meteoblue(lat=6.2442, lon=-75.5812, location_name="Medellín")
        if df_mb.empty:
            print("❌ Meteoblue returned empty DataFrame.")
        else:
            print(f"✅ Meteoblue returned {len(df_mb)} rows.")
            print(df_mb.head())
    except Exception as e:
        print(f"❌ Meteoblue error: {e}")

    # Test Meteosource
    print("\nTesting Meteosource...")
    try:
        df_ms = meteosource.fetch_meteosource(lat=6.2442, lon=-75.5812, location_name="Medellín")
        if df_ms.empty:
            print("❌ Meteosource returned empty DataFrame.")
        else:
            print(f"✅ Meteosource returned {len(df_ms)} rows.")
            print(df_ms.head())
    except Exception as e:
        print(f"❌ Meteosource error: {e}")

if __name__ == "__main__":
    debug_apis()
