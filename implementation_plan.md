# Implementation Plan - Dashboard Reorganization

## Goal
Reorganize the Streamlit dashboard (`app.py`) to separate the Map, Metrics, and Raw Data into distinct tabs, improving usability and clarity.

## User Review Required
*   **Layout Change**: The single-page layout will be replaced by a tabbed interface.

## Proposed Changes

### Dashboard (`app.py`)
*   **Introduce Tabs**: Use `st.tabs(["Métricas", "Mapa", "Datos"])`.
*   **Tab 1: Métricas**: Display the Temperature, Precipitation, and Wind charts here.
*   **Tab 2: Mapa**: Display the Station Map here.
*   **Tab 3: Datos**: Display the "Datos Combinados (Canonical Record)" dataframe here.

## Verification Plan

### Manual Verification
1.  **Restart App**: Run `pkill -f streamlit` and `./.venv/bin/streamlit run app.py`.
2.  **Check Tabs**: Open the app URL.
3.  **Verify Content**:
    *   Click "Métricas" tab -> Check if charts appear.
    *   Click "Mapa" tab -> Check if map appears.
    *   Click "Datos" tab -> Check if dataframe appears.
