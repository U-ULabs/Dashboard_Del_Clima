import pytest
import pandas as pd
import numpy as np
from processing import transform

def test_to_canonical_structure():
    df = pd.DataFrame({
        'timestamp': ['2023-01-01'],
        'lat': [6.0],
        'lon': [-75.0],
        'temp_c': [25.0],
        'extra': ['ignore']
    })
    result = transform.to_canonical(df)
    
    expected_cols = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source", "station_id"]
    assert list(result.columns) == expected_cols
    assert 'extra' not in result.columns

def test_to_canonical_casting():
    df = pd.DataFrame({
        'timestamp': ['2023-01-01'],
        'lat': [6.0],
        'lon': [-75.0],
        'temp_c': [25.0]
    })
    result = transform.to_canonical(df)
    assert pd.api.types.is_datetime64_any_dtype(result['timestamp'])
    assert result['precip_mm'].isna().all()
