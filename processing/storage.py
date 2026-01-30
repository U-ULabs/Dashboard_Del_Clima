"""Storage helpers for processed data.

This module contains small functions to persist data locally as CSV or to
push to object storage. Starts with CSV persistence only.
"""
from pathlib import Path
import pandas as pd


def save_csv(df: pd.DataFrame, path: str, index: bool = False) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=index)


def append_csv(df: pd.DataFrame, path: str, index: bool = False) -> None:
    p = Path(path)
    if p.exists():
        existing = pd.read_csv(p)
        df = pd.concat([existing, df], ignore_index=True)
    save_csv(df, path, index=index)
