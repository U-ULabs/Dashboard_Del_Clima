"""Data transformation utilities.

Functions to transform raw source schemas into the canonical schema used by the
pipeline.
"""
import pandas as pd


import mlflow

CANONICAL_COLS = ["timestamp", "lat", "lon", "temp_c", "precip_mm", "wind_m_s", "source", "station_id"]


def to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    """Attempt to coerce a DataFrame to canonical columns.

    This function keeps only known columns and casts types where possible. It is
    tolerant to missing columns and will fill them with NaNs.
    """
    out = pd.DataFrame(columns=CANONICAL_COLS)
    for c in CANONICAL_COLS:
        if c in df.columns:
            out[c] = df[c]
        else:
            out[c] = pd.NA
    # cast timestamp to datetime
    if not out['timestamp'].isna().all():
        out['timestamp'] = pd.to_datetime(out['timestamp'], errors='coerce')
    
    # Log to MLflow
    if mlflow.active_run():
        mlflow.log_metric("transform_output_rows", len(out))
        
    return out
