"""Data cleaning helpers.

Small functions to drop duplicates, fill gaps and apply quality filters.
"""
import pandas as pd


import mlflow

def drop_duplicate_observations(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure municipality is in columns before dropping, or ignore if not present
    subset = ['timestamp', 'lat', 'lon', 'source', 'station_id']
    if 'municipality' in df.columns:
        subset.append('municipality')
    
    initial_rows = len(df)
    df_dedup = df.drop_duplicates(subset=subset)
    final_rows = len(df_dedup)
    
    # Log to MLflow if there is an active run, or start a new one
    if mlflow.active_run():
        mlflow.log_metric("cleaning_initial_rows", initial_rows)
        mlflow.log_metric("cleaning_final_rows", final_rows)
        mlflow.log_metric("cleaning_dropped_rows", initial_rows - final_rows)
    
    return df_dedup


def filter_valid_temps(df: pd.DataFrame, min_temp: float = -90, max_temp: float = 60) -> pd.DataFrame:
    return df[(df['temp_c'].isna()) | ((df['temp_c'] >= min_temp) & (df['temp_c'] <= max_temp))]
