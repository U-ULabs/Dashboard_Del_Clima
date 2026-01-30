"""Meteosource data source stub."""
from typing import Optional
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("METEOSOURCE_API_KEY")

def fetch_meteosource(lat: float, lon: float, location_name: str, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    """Fetch Meteosource observations."""
    # Use provided coordinates
    LAT = str(lat)
    LON = str(lon)
    
    # Meteosource API endpoint (example, check docs for exact endpoint)
    # Using 'point' endpoint for current/forecast data
    URL = "https://www.meteosource.com/api/v1/free/point"
    
    params = {
        "key": API_KEY,
        "lat": LAT,
        "lon": LON,
        "sections": "hourly", # Changed from 'current' to 'hourly'
        "units": "metric"
    }
    
    if not API_KEY or API_KEY.startswith("your_"):
        print("Warning: METEOSOURCE_API_KEY not set or invalid. Returning empty DataFrame.")
        cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source"]
        return pd.DataFrame(columns=cols)

    try:
        response = requests.get(URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching Meteosource data: {e}")
        cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source"]
        return pd.DataFrame(columns=cols)
        
    # Parse response
    if 'hourly' not in data:
        cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source", "station_id", "municipality"]
        return pd.DataFrame(columns=cols)
        
    hourly_data = data['hourly']['data']
    
    rows = []
    for hour in hourly_data:
        # hour structure: {'date': '2025-11-22T19:00:00', 'temperature': 22.5, 'wind': {'speed': 1.2}, ...}
        rows.append({
            "timestamp": pd.to_datetime(hour.get('date')),
            "lat": float(LAT),
            "lon": float(LON),
            "temp_c": hour.get('temperature'),
            "precip_mm": hour.get('precipitation', {}).get('total', 0.0),
            "wind_m_s": hour.get('wind', {}).get('speed', 0.0),
            "source": "meteosource",
            "station_id": f"{location_name} (Meteosource)",
            "municipality": location_name
        })
    
    return pd.DataFrame(rows)