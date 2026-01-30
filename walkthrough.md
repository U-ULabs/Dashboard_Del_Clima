# Weather Dashboard Walkthrough

## Overview
This dashboard integrates weather data from SIATA, Meteoblue, and Meteosource into a single canonical record. It visualizes the data using maps and charts.

## Features
*   **Data Integration**: Fetches data from multiple APIs/sources.
*   **Canonicalization**: Normalizes data into a standard schema (`timestamp`, `lat`, `lon`, `temp_c`, `precip_mm`, `wind_m_s`, `source`, `station_id`).
*   **Cleaning**: Deduplicates observations.
*   **Caching**: Uses Streamlit's `@st.cache_data` to optimize performance and avoid redundant API calls.
*   **Persistence**: Saves the processed canonical record to `data/out/canonical.csv`.
*   **Visualization**:
    *   **Map**: Shows stations with valid coordinates.
    *   **Charts**: Line charts for Temperature and Wind; Bar chart for Precipitation.

## Setup & Run
1.  **Install Dependencies**:
    ```bash
    ./venv/bin/pip install -r requirements.txt
    ```
2.  **Run Dashboard**:
    ```bash
    ./venv/bin/streamlit run app.py
    ```

## Recent Changes
*   **Fixed API Keys**: Updated `.env`.
*   **Fixed Meteoblue**: Corrected API parameters and parsing.
*   **Fixed SIATA**: Corrected column mapping and handled missing coordinates.
    *   **Coordinate Mapping**: Added a manual mapping for known stations (e.g., "Colegio Presbitero Bernardo Montoya") to allow them to appear on the map despite the source file lacking coordinates.
*   **Added Visualizations**: Added charts for Precipitation and Wind.
*   **Added Caching**: Implemented `@st.cache_data` for the data pipeline.
*   **Added Tests**: Implemented `pytest` suite in `tests/` folder.

