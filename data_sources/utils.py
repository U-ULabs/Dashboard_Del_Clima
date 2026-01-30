"""Utility helpers for data_sources.

Small helpers to normalize timestamps, convert units, and load credentials.
"""
from datetime import datetime
from typing import Optional


def parse_iso(ts: str) -> Optional[datetime]:
    if ts is None:
        return None
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        try:
            # fallback for naive formats
            return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None


def c_to_f(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0
