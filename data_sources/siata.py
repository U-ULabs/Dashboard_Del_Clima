"""SIATA data source.

Provides functions to fetch data from the SIATA APIs/Website and
normalize it into the project's common schema.
"""

import requests
from typing import Optional
import os
from bs4 import BeautifulSoup
import pandas as pd
import io
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SIATA_API_URL")

SIATA_ACUMPRECIPITACION_URL = "https://www.siata.gov.co/operacional/Meteorologia/AcumPrecipitacion/"

def get_latest_precipitation_url() -> Optional[str]:
    """Scrapes the SIATA directory to find the latest precipitation file."""
    try:
        response = requests.get(SIATA_ACUMPRECIPITACION_URL, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.txt') or href.endswith('.csv'):
                links.append(urljoin(SIATA_ACUMPRECIPITACION_URL, href))
        
        # Sort to get the latest (assuming filename contains date or they are listed in order)
        # SIATA files usually have names like DatosPacum_MonthYear.txt
        # We'll just take the last one found as a heuristic for "latest" if sorting isn't obvious,
        # or sort by name.
        links.sort()
        
        if links:
            return links[-1]
        return None
        
    except Exception as e:
        print(f"Error finding SIATA URL: {e}")
        return None

# Hardcoded coordinates for known stations (Name -> (Lat, Lon))
STATION_COORDINATES = {
    "Colegio Presbitero Bernardo Montoya": (6.337060, -75.503460),
    "Colegio Jose Manuel Sierra": (6.375, -75.450), # Approximate based on municipality
    "Edificio Gaspar de Rodas - Bello": (6.335, -75.560), # Approximate
    "Torre SIATA": (6.259, -75.591) # Example
}

def fetch_siata(start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    """Fetch SIATA precipitation data."""
    
    url = get_latest_precipitation_url()
    if not url:
        print("Could not determine SIATA data URL.")
        cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source", "station_id"]
        return pd.DataFrame(columns=cols)
        
    print(f"Fetching SIATA data from: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Attempt to parse
        # SIATA txt files are often comma or tab separated.
        # We'll try comma first, skipping the first row if it's metadata.
        
        content = response.text
        
        # Heuristic: check first line. If it contains "Fecha", it might be a header.
        # The screenshot showed "Fecha actualizacion" in the first line, so skip 1.
        
        try:
            df = pd.read_csv(io.StringIO(content), sep=',', skiprows=1, on_bad_lines='skip')
        except:
            # Try tab
            df = pd.read_csv(io.StringIO(content), sep='\t', skiprows=1, on_bad_lines='skip')
            
        # Normalize columns
        # We need to map SIATA columns to canonical.
        # SIATA columns (example): "Fecha", "Codigo", "Nombre", "Latitud", "Longitud", "Valor" (Precipitation)
        # Let's inspect columns if possible, but since we are writing code, we have to guess or use standard mapping.
        # Based on typical SIATA data:
        # Fecha, Codigo, Nombre, Latitud, Longitud, Calidad, Acumulado...
        
        # Normalize columns to lowercase
        df.columns = [c.lower().strip() for c in df.columns]
        
        # SIATA Columns: ['estacion', 'nombre', 'municipio', 'barrio', 'climatologia mes', 'acumulado mes (mm)', 'porcentaje mes']
        
        rename_map = {
            'acumulado mes (mm)': 'precip_mm',
            'nombre': 'station_id',
            'municipio': 'municipality'
        }
        
        df.rename(columns=rename_map, inplace=True)
        
        # Add missing canonical columns
        if 'timestamp' not in df.columns:
            # Use current time as timestamp for now, or extract from filename/header if possible
            # The header had "Fecha actualizacion: 2025/10/01 00:01"
            # We could parse it, but for now let's use pd.Timestamp.now() or a placeholder
            df['timestamp'] = pd.Timestamp.now()

        # Map coordinates
        df['lat'] = df['station_id'].apply(lambda x: STATION_COORDINATES.get(str(x).strip(), (pd.NA, pd.NA))[0])
        df['lon'] = df['station_id'].apply(lambda x: STATION_COORDINATES.get(str(x).strip(), (pd.NA, pd.NA))[1])

        if 'temp_c' not in df.columns:
            df['temp_c'] = pd.NA
        if 'wind_m_s' not in df.columns:
            df['wind_m_s'] = pd.NA
            
        df['source'] = 'siata'
        
        # Convert timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
        # Filter canonical
        # Filter canonical
        canonical_cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source", "station_id", "municipality"]
        
        # Ensure all canonical columns exist
        for col in canonical_cols:
            if col not in df.columns:
                df[col] = pd.NA
                
        return df[canonical_cols]

    except Exception as e:
        print(f"Error fetching/parsing SIATA data: {e}")
        cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source", "station_id"]
        return pd.DataFrame(columns=cols)