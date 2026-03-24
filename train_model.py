import pandas as pd
import pickle
from prophet import Prophet

# Load cleaned data
def load_cleaned_data(filepath="data/cleaned_aqi.csv"):
    df = pd.read_csv(filepath)
    return df

# Prepare data for Prophet
def prepare_prophet_df(df):
    prophet_df = df[["Date", "AQI"]].copy()
    prophet_df.columns = ["ds", "y"]
    prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])
    return prophet_df

# Train model
def train(prophet_df):
    model = Prophet()
    model.fit(prophet_df)
    print("Model training done!")
    return model

# Save model
def save_model(model, path="model.pkl"):
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {path}")

if __name__ == "__main__":
    df = load_cleaned_data()
    prophet_df = prepare_prophet_df(df)
    model = train(prophet_df)
    save_model(model)