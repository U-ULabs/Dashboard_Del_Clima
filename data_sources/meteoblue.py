"""meteoblue data source stub.

Provides a function to query meteoblue or similar global forecast APIs and
return normalized observations/forecasts.
"""
import os
import requests
import pandas as pd
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("METEOBLUE_API_KEY")

def fetch_meteoblue(lat: float, lon: float, location_name: str, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    """Fetch Meteoblue data and return a canonical DataFrame."""
    
    # Use provided coordinates
    LATITUDE = lat
    LONGITUDE = lon
    
    BASE_URL = "http://my.meteoblue.com/packages/basic-1h"
    
    params = {
        "apikey": API_KEY,
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "asl": 1500,
        "tz": "America/Bogota",
        "format": "json"
    }
    
    if not API_KEY or API_KEY.startswith("your_"):
        print("Warning: METEOBLUE_API_KEY not set or invalid. Returning empty DataFrame.")
        cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source"]
        return pd.DataFrame(columns=cols)

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching Meteoblue data: {e}")
        cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source"]
        return pd.DataFrame(columns=cols)

    if 'data_1h' not in data:
        print("Meteoblue 'data_1h' not found in response (Key might not support hourly).")
        cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source"]
        return pd.DataFrame(columns=cols)
        
    df = pd.DataFrame(data['data_1h'])
    
    # Rename columns to match canonical schema
    # 'data_1h' keys: 'time', 'temperature', 'precipitation', 'windspeed', etc.
    
    rename_map = {
        'time': 'timestamp',
        'temperature': 'temp_c',
        'precipitation': 'precip_mm',
        'windspeed': 'wind_m_s'
    }
    
    df.rename(columns=rename_map, inplace=True)
    
    df['lat'] = LATITUDE
    df['lon'] = LONGITUDE
    df['source'] = 'meteoblue'
    df['station_id'] = f"{location_name} (Meteoblue)"
    df['municipality'] = location_name
    
    # Convert timestamp
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter to canonical columns that exist
    canonical_cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source", "station_id", "municipality"]
    for col in canonical_cols:
        if col not in df.columns:
            df[col] = pd.NA
            
    return df[canonical_cols]