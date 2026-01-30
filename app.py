"""Streamlit Dashboard for Weather Data Pipeline.

This app fetches data from multiple sources (SIATA, Meteoblue, Meteosource),
canonicalizes it, and displays it.
"""
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Import local modules (flat structure)
from data_sources import siata, meteoblue, meteosource
from processing import transform, cleaning, storage

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Weather Data Pipeline", layout="wide")

st.title("Dashboard de Métricas del Clima - Tiempo Real")
st.write("Este dashboard obtiene datos en tiempo real de SIATA, Meteosource y Meteoblue.")

st.sidebar.header("Configuration")
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Add clear cache button
if st.sidebar.button("🔄 Limpiar Caché y Actualizar"):
    st.cache_data.clear()
    st.rerun()

# Caching data fetching (reduced TTL to 5 minutes)
@st.cache_data(ttl=300)
def get_all_data(start_date, end_date):
    dfs = []
    
    # Locations configuration
    LOCATIONS = [
        {"name": "Medellín", "lat": 6.2442, "lon": -75.5812},
        {"name": "Bello", "lat": 6.3373, "lon": -75.5579},
        {"name": "Envigado", "lat": 6.1759, "lon": -75.5917},
        {"name": "Itagüí", "lat": 6.1846, "lon": -75.5991},
        {"name": "Sabaneta", "lat": 6.1520, "lon": -75.6156}
    ]

    # SIATA (Regional, fetches all available stations)
    try:
        df_siata = siata.fetch_siata(start=str(start_date), end=str(end_date))
        if not df_siata.empty:
            dfs.append(transform.to_canonical(df_siata))
    except Exception as e:
        st.error(f"SIATA Error: {e}")

    # Fetch Meteoblue and Meteosource for each location
    for loc in LOCATIONS:
        name = loc["name"]
        lat = loc["lat"]
        lon = loc["lon"]
        
        # Meteoblue
        try:
            df_meteoblue = meteoblue.fetch_meteoblue(lat=lat, lon=lon, location_name=name, start=str(start_date), end=str(end_date))
            if not df_meteoblue.empty:
                dfs.append(transform.to_canonical(df_meteoblue))
        except Exception as e:
            st.error(f"Meteoblue Error ({name}): {e}")
            
        # Meteosource
        try:
            df_meteosource = meteosource.fetch_meteosource(lat=lat, lon=lon, location_name=name, start=str(start_date), end=str(end_date))
            if not df_meteosource.empty:
                dfs.append(transform.to_canonical(df_meteosource))
        except Exception as e:
            st.error(f"Meteosource Error ({name}): {e}")

    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)
        df_final = cleaning.drop_duplicate_observations(df_final)
        # Sort by timestamp to make hourly data visible/ordered
        if 'timestamp' in df_final.columns:
            df_final = df_final.sort_values('timestamp', ascending=True)
        return df_final
    return pd.DataFrame()

if st.sidebar.button("Actualizar Datos"):
    with st.spinner("Obteniendo y procesando datos..."):
        df_final = get_all_data(start_date, end_date)
        
        if not df_final.empty:
            # Save full canonical dataset BEFORE filtering
            os.makedirs("data/out", exist_ok=True)
            output_path = "data/out/canonical.csv"
            storage.save_csv(df_final, output_path)
            st.info(f"Datos completos ({len(df_final)} registros) almacenados en {output_path}")

            # Municipality Filter
            if 'municipality' in df_final.columns:
                # Normalize municipality names (title case, strip)
                df_final['municipality'] = df_final['municipality'].astype(str).str.title().str.strip()
                
                available_munis = sorted(df_final['municipality'].unique().tolist())
                selected_munis = st.sidebar.multiselect("Filtrar por Municipio", available_munis, default=available_munis)
                
                if selected_munis:
                    df_final = df_final[df_final['municipality'].isin(selected_munis)]
            
            st.success(f"Datos mostrados: {len(df_final)} registros.")
            
            # Debug: Show source distribution (Restored)
            st.sidebar.write("### Distribución por Fuente")
            st.sidebar.write(df_final['source'].value_counts())

            # Tabs for layout
            tab_metrics, tab_map, tab_radares, tab_data, tab_pred = st.tabs(["Métricas", "Mapa", "Radares", "Datos", "Predicciones"])

            with tab_metrics:
                st.subheader("Métricas")
                
                # Temperature
                if 'temp_c' in df_final.columns:
                    st.write("### Temperatura (°C)")
                    df_temp = df_final.dropna(subset=['temp_c'])
                    if not df_temp.empty:
                        # Pivot to have sources as columns
                        chart_data_temp = df_temp.pivot_table(index='timestamp', columns='source', values='temp_c', aggfunc='mean')
                        st.line_chart(chart_data_temp)
                    else:
                        st.info("No hay datos de temperatura.")

                # Precipitation
                if 'precip_mm' in df_final.columns:
                    st.write("### Precipitación (mm)")
                    df_precip = df_final.dropna(subset=['precip_mm'])
                    if not df_precip.empty:
                        chart_data_precip = df_precip.pivot_table(index='timestamp', columns='source', values='precip_mm', aggfunc='mean')
                        st.bar_chart(chart_data_precip)
                    else:
                        st.info("No hay datos de precipitación.")

                # Wind
                if 'wind_m_s' in df_final.columns:
                    st.write("### Viento (m/s)")
                    df_wind = df_final.dropna(subset=['wind_m_s'])
                    if not df_wind.empty:
                        chart_data_wind = df_wind.pivot_table(index='timestamp', columns='source', values='wind_m_s', aggfunc='mean')
                        st.line_chart(chart_data_wind)
                    else:
                        st.info("No hay datos de viento.")

            with tab_map:
                st.subheader("Mapa de Estaciones")
                df_map = df_final.dropna(subset=['lat', 'lon']).copy()
                
                # Assign colors based on source
                color_map = {
                    'siata': '#FF0000',      # Red
                    'meteoblue': '#0000FF',  # Blue
                    'meteosource': '#00FF00' # Green
                }
                # st.map doesn't support color column directly in all versions, but let's try or use size
                # For simple st.map, we can't easily color. 
                # But we can separate them or just show them.
                # Let's just show them for now, but maybe add a legend in text.
                
                if not df_map.empty:
                    st.map(df_map, size=20)
                    st.caption(f"Mostrando {len(df_map)} estaciones con coordenadas válidas.")
                else:
                    st.warning("No hay datos con coordenadas válidas para mostrar en el mapa.")
                
                if df_final['lat'].isna().any():
                    st.warning("Nota: Algunas estaciones (ej. SIATA) no tienen coordenadas en el sistema y no aparecen en el mapa. Se han mapeado algunas manualmente.")

            with tab_radares:
                st.subheader("Red de Radares IDEAM")
                
                try:
                    from data_sources import ideam_radar
                    
                    # Controls
                    col1, col2 = st.columns(2)
                    with col1:
                        radar_name = st.selectbox("Seleccionar Radar", ["Carimagua", "Guaviare", "Barrancabermeja", "Munchique"])
                    with col2:
                        # Date selection for radar
                        radar_date = st.date_input("Fecha Radar", value=pd.to_datetime("2022-08-09"))
                    
                    date_str = radar_date.strftime("%Y/%m/%d")
                    
                    # List files
                    files = ideam_radar.list_available_radar_files(date_str, radar_name, limit=20)
                    
                    if files:
                        st.success(f"Se encontraron {len(files)} archivos para {radar_name} en {date_str}")
                        
                        # File selector
                        selected_file = st.selectbox("Seleccionar Archivo (Hora UTC)", files, format_func=lambda x: x.split('/')[-1])
                        
                        if st.button("Visualizar Radar"):
                            st.info(f"Iniciando visualización para: {selected_file}")
                            with st.spinner("Generando visualización..."):
                                try:
                                    fig = ideam_radar.create_radar_plot(selected_file)
                                    
                                    if fig:
                                        st.pyplot(fig)
                                        st.success("Gráfico generado.")
                                    else:
                                        st.error("La función retornó None. Revisa si el archivo es válido.")
                                except Exception as e:
                                    st.error(f"Excepción en la app: {e}")
                    else:
                        st.warning(f"No se encontraron archivos para {radar_name} en la fecha {date_str}. Intenta con otra fecha (ej. 2022/08/09).")
                        
                    st.divider()
                    st.write("### Ubicación de Radares")
                    df_radares = ideam_radar.get_radar_locations()
                    st.map(df_radares[['lat', 'lon']])
                        
                except Exception as e:
                    st.error(f"Error cargando módulo de radares: {e}")


            with tab_data:
                st.subheader("Datos Combinados (Canonical Record)")
                st.dataframe(df_final)

            # --- Predictions Tab ---
            with tab_pred:
                st.subheader("Predicción de Temperatura (Próxima Hora)")
                
                import mlflow
                from mlflow.tracking import MlflowClient
                
                # 1. Load Model
                # Find the latest run for "Hourly_Weather_Forecast"
                try:
                    experiment = mlflow.get_experiment_by_name("Hourly_Weather_Forecast")
                    if experiment:
                        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"], max_results=1)
                        if not runs.empty:
                            run_id = runs.iloc[0].run_id
                            logged_model = f"runs:/{run_id}/model"
                            
                            st.write(f"Cargando modelo desde Run ID: `{run_id}`")
                            model = mlflow.sklearn.load_model(logged_model)
                            
                            # 2. Prepare Data for Prediction
                            # We need the latest data point for each station
                            # Features: ['temp_c', 'wind_m_s', 'precip_mm', 'hour']
                            
                            if 'temp_c' in df_final.columns:
                                # Get latest available data per station
                                latest_data = df_final.sort_values('timestamp').groupby('station_id').tail(1).copy()
                                
                                # Feature Engineering
                                latest_data['timestamp'] = pd.to_datetime(latest_data['timestamp'])
                                latest_data['hour'] = latest_data['timestamp'].dt.hour
                                
                                # Fill NaNs if any (simple fill for demo)
                                latest_data = latest_data.fillna(0)
                                
                                features = ['temp_c', 'wind_m_s', 'precip_mm', 'hour']
                                
                                # Check if we have all features
                                if all(f in latest_data.columns for f in features):
                                    X_pred = latest_data[features]
                                    
                                    # Predict
                                    predictions = model.predict(X_pred)
                                    latest_data['predicted_temp_next_hour'] = predictions
                                    
                                    st.write("### Pronóstico para la próxima hora")
                                    st.dataframe(latest_data[['station_id', 'timestamp', 'temp_c', 'predicted_temp_next_hour']])
                                    
                                    # Visualization
                                    st.bar_chart(latest_data.set_index('station_id')[['temp_c', 'predicted_temp_next_hour']])
                                else:
                                    st.warning(f"Faltan columnas para predecir. Se requieren: {features}")
                        else:
                            st.warning("No se encontraron runs en el experimento 'Hourly_Weather_Forecast'.")
                    else:
                        st.warning("No existe el experimento 'Hourly_Weather_Forecast'. Ejecuta el entrenamiento primero.")
                except Exception as e:
                    st.error(f"Error generando predicciones: {e}")
                
        else:
            st.warning("No se pudieron obtener datos de ninguna fuente.")
