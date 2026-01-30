import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import InformerConfig, InformerForPrediction, Trainer, TrainingArguments, AutoformerConfig, AutoformerForPrediction, PatchTSTConfig, PatchTSTForPrediction
import mlflow
import mlflow.transformers
import os

# --- Configuration ---
PREDICTION_LENGTH = 6   # Predict next 6 hours
CONTEXT_LENGTH = 24     # Use past 24 hours
BATCH_SIZE = 16
EPOCHS = 5

class WeatherDataset(Dataset):
    def __init__(self, df, context_length, prediction_length):
        self.df = df.copy()
        self.context_length = context_length
        self.prediction_length = prediction_length
        
        # Ensure sorted
        self.df = self.df.sort_values('timestamp')
        self.data = self.df['temp_c'].values.astype(np.float32)
        
        # Simple time feature: Hour of day normalized [0, 1]
        self.time_features = (self.df['timestamp'].dt.hour.values / 23.0).astype(np.float32)
        
        # Normalize Data (Z-score)
        self.mean = np.mean(self.data)
        self.std = np.std(self.data)
        self.data = (self.data - self.mean) / (self.std + 1e-6)

    def __len__(self):
        # We need enough data for context + prediction
        return len(self.data) - self.context_length - self.prediction_length

    def __getitem__(self, idx):
        # Past (Context)
        past_len = self.context_length
        past_start = idx
        past_end = idx + past_len
        past_values = self.data[past_start:past_end]
        
        # Future (Target)
        future_start = past_end
        future_end = past_end + self.prediction_length
        future_values = self.data[future_start:future_end]
        
        return {
            "past_values": torch.tensor(past_values).unsqueeze(-1),
            "future_values": torch.tensor(future_values).unsqueeze(-1),
        }

def train_transformer():
    print("Starting Transformer training...")
    
    # Load Data
    data_path = "data/canonical.csv"
    if not os.path.exists(data_path):
        print("Data not found.")
        return
        
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter for one station for simplicity in this demo
    # Ideally we would train on all, but let's pick the one with most data
    station_counts = df['station_id'].value_counts()
    station_id = station_counts.index[0]
    print(f"Training on station: {station_id} ({station_counts.iloc[0]} rows)")
    
    df_station = df[df['station_id'] == station_id].dropna(subset=['temp_c']).reset_index(drop=True)
    
    if len(df_station) < (CONTEXT_LENGTH + PREDICTION_LENGTH + 10):
        print("Not enough data.")
        return

    # Split Train/Test
    split_idx = int(len(df_station) * 0.8)
    train_df = df_station.iloc[:split_idx]
    test_df = df_station.iloc[split_idx:]
    
    train_dataset = WeatherDataset(train_df, CONTEXT_LENGTH, PREDICTION_LENGTH)
    test_dataset = WeatherDataset(test_df, CONTEXT_LENGTH, PREDICTION_LENGTH)
    
    print(f"Train samples: {len(train_dataset)}, Test samples: {len(test_dataset)}")
    
    # Model Config
    config = PatchTSTConfig(
        prediction_length=PREDICTION_LENGTH,
        context_length=CONTEXT_LENGTH,
        input_size=1,
        num_input_channels=1, # PatchTST uses channels
        lags_sequence=[1],
        num_time_features=1,
        d_model=16,
        encoder_layers=2,
        encoder_attention_heads=2,
        encoder_ffn_dim=32,
        dropout=0.1,
    )
    
    model = PatchTSTForPrediction(config)
    
    # Training Args
    training_args = TrainingArguments(
        output_dir="out/informer_checkpoints",
        overwrite_output_dir=True,
        learning_rate=1e-3,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        eval_strategy="epoch",
        logging_strategy="epoch",
        save_strategy="no",
        remove_unused_columns=False, 
        label_names=["future_values"], 
        report_to=["mlflow"],
    )
    
    # MLflow Setup
    mlflow.set_experiment("Transformer_Weather_Forecast")
    
    with mlflow.start_run(run_name="informer_demo"):
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
        )
        
        trainer.train()
        
        # Evaluate
        metrics = trainer.evaluate()
        print("Evaluation Metrics:", metrics)
        
        # Save Model manually to MLflow to ensure transformers flavor
        # mlflow.transformers.log_model(
        #     transformers_model={"model": model, "feature_extractor": None}, # No feature extractor for raw time series
        #     artifact_path="informer_model",
        #     task="time-series-forecasting"
        # )
        print("Model logged to MLflow (via autolog or skipped).")

if __name__ == "__main__":
    train_transformer()
