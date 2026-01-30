import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd

try:
    experiment = mlflow.get_experiment_by_name("Hourly_Weather_Forecast")
    if experiment:
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"], max_results=1)
        if not runs.empty:
            run_id = runs.iloc[0].run_id
            logged_model = f"runs:/{run_id}/model"
            print(f"Loading model from {logged_model}...")
            model = mlflow.sklearn.load_model(logged_model)
            print("Model loaded successfully.")
        else:
            print("No runs found.")
    else:
        print("Experiment not found.")
except Exception as e:
    print(f"Error: {e}")
