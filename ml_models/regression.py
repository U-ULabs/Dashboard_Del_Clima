import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os

def train():
    print("Starting Hourly Forecast training...")
    
    # Load data
    data_path = "data/canonical.csv"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run the data pipeline first.")
        return

    df = pd.read_csv(data_path)
    
    # 1. Preprocessing & Feature Engineering
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort for lag creation
    df = df.sort_values(by=['station_id', 'timestamp'])
    
    # Extract Time Features
    df['hour'] = df['timestamp'].dt.hour
    
    # Create Target: Next Hour's Temperature
    # We group by station to ensure we don't shift data between different stations
    df['target_temp_next_hour'] = df.groupby('station_id')['temp_c'].shift(-1)
    
    # Drop rows where target is NaN (last hour of each station) or features are NaN
    features = ['temp_c', 'wind_m_s', 'precip_mm', 'hour']
    df_model = df.dropna(subset=features + ['target_temp_next_hour'])
    
    print(f"Training data rows: {len(df_model)}")
    
    if len(df_model) < 10:
        print("Not enough data to train.")
        return

    # 2. Split Data
    X = df_model[features]
    y = df_model['target_temp_next_hour']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. MLflow Tracking
    mlflow.set_experiment("Hourly_Weather_Forecast")
    
    with mlflow.start_run(run_name="linear_regression_t+1"):
        # Log Parameters
        params = {
            "model_type": "LinearRegression",
            "features": features,
            "target": "temp_c (t+1)",
            "test_size": 0.2,
            "random_state": 42
        }
        mlflow.log_params(params)
        
        # Train
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predict
        predictions = model.predict(X_test)
        
        # Metrics
        mse = mean_squared_error(y_test, predictions)
        rmse = mse ** 0.5
        mae = mean_absolute_error(y_test, predictions)
        
        print(f"RMSE: {rmse:.4f}")
        print(f"MAE: {mae:.4f}")
        
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        
        # Log Model
        mlflow.sklearn.log_model(model, "model")
        print("Model logged to MLflow.")

if __name__ == "__main__":
    train()
