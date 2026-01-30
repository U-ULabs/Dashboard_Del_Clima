"""IDEAM Radar data source.

Fetches and processes radar data from IDEAM's S3 bucket using xradar and cartopy.
"""
import warnings
import fsspec
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xradar as xd
from typing import Optional, List
import io
import s3fs
import cmweather

# Radar locations in Colombia
RADAR_LOCATIONS = {
    "Carimagua": {"lat": 4.567, "lon": -71.333, "range_km": 200},
    "Guaviare": {"lat": 2.567, "lon": -72.633, "range_km": 200},
    "Barrancabermeja": {"lat": 7.067, "lon": -73.850, "range_km": 200},
    "Munchique": {"lat": 2.533, "lon": -76.967, "range_km": 200},
}

def get_radar_locations() -> pd.DataFrame:
    """Return DataFrame with radar locations."""
    data = []
    for name, info in RADAR_LOCATIONS.items():
        data.append({
            "Name": name,
            "lat": info["lat"],
            "lon": info["lon"],
            "range_km": info["range_km"],
            "color": "blue"
        })
    return pd.DataFrame(data)

def list_available_radar_files(date_str: str, radar_name: str, limit: int = 10) -> List[str]:
    """List available radar files from IDEAM S3 bucket for a specific date and radar."""
    try:
        fs = fsspec.filesystem("s3", anon=True)
        # Pattern: s3-radaresideam/l2_data/YYYY/MM/DD/RadarName/*
        # date_str expected as YYYY/MM/DD
        pattern = f"s3-radaresideam/l2_data/{date_str}/{radar_name}/*"
        files = sorted(fs.glob(pattern))
        return files[:limit]
    except Exception as e:
        print(f"Error listing radar files: {e}")
        return []

def create_radar_plot(s3_path: str):
    """
    Reads a radar file from S3 and creates a matplotlib figure with reflectivity (DBZH).
    
    Args:
        s3_path: Full S3 path (e.g., 's3-radaresideam/...') or path without 's3://'
    
    Returns:
        matplotlib.figure.Figure or None if error
    """
    fig = None
    try:
        # Ensure s3:// prefix
        if not s3_path.startswith("s3://"):
            full_path = f"s3://{s3_path}"
        else:
            full_path = s3_path

        print(f"DEBUG: Opening {full_path}...")
        
        # Using fsspec to open a file-like object
        with fsspec.open(full_path, mode="rb", anon=True) as f:
            content = f.read()
            with io.BytesIO(content) as buffer:
                radar = xd.io.open_iris_datatree(buffer)
                
                # Georeference
                radar = radar.xradar.georeference()
                
                # Get first sweep
                sweep = radar["sweep_0"]
                
                # Get CRS
                proj_crs = xd.georeference.get_crs(sweep.ds)
                cart_crs = ccrs.Projection(proj_crs)
                
                # Create Plot
                # Use subplots for better memory management
                fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
                
                # Plot DBZH (Reflectivity)
                cmap = "jet"
                try:
                    import cmweather
                    cmap = "ChaseSpectral"
                except ImportError:
                    pass

                sweep["DBZH"].plot(
                    x="x",
                    y="y",
                    cmap=cmap,
                    transform=cart_crs,
                    cbar_kwargs={'label': 'Reflectividad [dBZ]', 'shrink': 0.8},
                    vmin=-10,
                    vmax=60,
                    ax=ax
                )
                
                # Add geographic features
                ax.coastlines()
                ax.add_feature(cfeature.BORDERS, linestyle=':')
                ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
                
                # Title
                try:
                    time_str = str(sweep["time"].values[0])[:19]
                except:
                    time_str = "Unknown Time"
                ax.set_title(f"Reflectividad - {time_str} UTC")
                
                return fig
        
    except Exception as e:
        print(f"Error creating radar plot for {s3_path}: {e}")
        import traceback
        traceback.print_exc()
        if fig:
            plt.close(fig)
        return None
