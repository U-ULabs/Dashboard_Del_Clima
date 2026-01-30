import pytest
import pandas as pd
from processing import cleaning

def test_drop_duplicate_observations():
    df = pd.DataFrame({
        'timestamp': ['2023-01-01', '2023-01-01'],
        'lat': [6.0, 6.0],
        'lon': [-75.0, -75.0],
        'source': ['test', 'test'],
        'station_id': ['A', 'A'],
        'temp_c': [25.0, 25.0]
    })
    result = cleaning.drop_duplicate_observations(df)
    assert len(result) == 1

def test_drop_duplicates_different_stations():
    df = pd.DataFrame({
        'timestamp': ['2023-01-01', '2023-01-01'],
        'lat': [6.0, 6.0],
        'lon': [-75.0, -75.0],
        'source': ['test', 'test'],
        'station_id': ['A', 'B'], # Different stations
        'temp_c': [25.0, 25.0]
    })
    result = cleaning.drop_duplicate_observations(df)
    assert len(result) == 2
