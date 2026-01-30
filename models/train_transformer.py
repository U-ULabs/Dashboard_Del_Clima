import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import InformerConfig, InformerForPrediction, Trainer, TrainingArguments
import mlflow
import mlflow.transformers
import os

# --- Configuration ---
PREDICTION_LENGTH = 24  # Predict next 24 hours
CONTEXT_LENGTH = 48     # Use past 48 hours
BATCH_SIZE = 32
EPOCHS = 3

class WeatherDataset(Dataset):
    def __init__(self, df, context_length, prediction_length):
        self.df = df
        self.context_length = context_length
        self.prediction_length = prediction_length
        
        # Ensure sorted
        self.df = self.df.sort_values('timestamp')
        self.data = self.df['temp_c'].values.astype(np.float32)
        self.time_features = self.df['timestamp'].dt.hour.values.astype(np.float32)
        
        # Normalize
        self.mean = np.mean(self.data)
        self.std = np.std(self.data)
        self.data = (self.data - self.mean) / self.std

    def __len__(self):
        return len(self.data) - self.context_length - self.prediction_length

    def __getitem__(self, idx):
        # Past values
        past_start = idx
        past_end = idx + self.context_length
        past_values = self.data[past_start:past_end]
        past_time_features = self.time_features[past_start:past_end]
        
        # Future values (Target)
        future_start = past_end
        future_end = past_end + self.prediction_length
        future_values = self.data[future_start:future_end]
        future_time_features = self.time_features[future_start:future_end]
        
        # Informer expects:
        # past_values: (seq_len, input_size)
        # past_time_features: (seq_len, num_features)
        # future_values: (pred_len, input_size)
        # future_time_features: (pred_len, num_features)
        
        return {
            "past_values": torch.tensor(past_values).unsqueeze(-1),
            "past_time_features": torch.tensor(past_time_features).unsqueeze(-1),
            "past_observed_mask": torch.ones_like(torch.tensor(past_values)).unsqueeze(-1),
            "future_values": torch.tensor(future_values).unsqueeze(-1),
            "future_time_features": torch.tensor(future_time_features).unsqueeze(-1),
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
    station_id = df['station_id'].iloc[0]
    print(f"Training on station: {station_id}")
    df_station = df[df['station_id'] == station_id].dropna(subset=['temp_c'])
    
    if len(df_station) < (CONTEXT_LENGTH + PREDICTION_LENGTH + 10):
        print("Not enough data.")
        return

    # Split
    split_idx = int(len(df_station) * 0.8)
    train_df = df_station.iloc[:split_idx]
    test_df = df_station.iloc[split_idx:]
    
    train_dataset = WeatherDataset(train_df, CONTEXT_LENGTH, PREDICTION_LENGTH)
    test_dataset = WeatherDataset(test_df, CONTEXT_LENGTH, PREDICTION_LENGTH)
    
    # Model Config
    config = InformerConfig(
        prediction_length=PREDICTION_LENGTH,
        context_length=CONTEXT_LENGTH,
        input_size=1,
        num_time_features=1,
        lags_sequence=[1, 24],
        num_static_categorical_features=0,
        num_static_real_features=0,
        encoder_layers=2,
        decoder_layers=2,
        d_model=16, # Small model for speed
    )
    
    model = InformerForPrediction(config)
    
    # Training Args
    training_args = TrainingArguments(
        output_dir="out/informer_checkpoints",
        overwrite_output_dir=True,
        learning_rate=1e-4,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        evaluation_strategy="epoch",
        logging_strategy="epoch",
        save_strategy="no",
        remove_unused_columns=False, # Important for custom datasets
        label_names=["future_values"], # Important for computing metrics
    )
    
    # MLflow Autologging
    mlflow.transformers.autolog()
    
    with mlflow.start_run(run_name="informer_weather_forecast"):
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
        )
        
        trainer.train()
        
        print("Training complete.")

if __name__ == "__main__":
    train_transformer()
