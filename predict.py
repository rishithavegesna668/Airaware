import pickle
import pandas as pd

# Load trained model
def load_model(path="model.pkl"):
    with open(path, "rb") as f:
        model = pickle.load(f)
    return model

# Predict future AQI
def predict_aqi(model, days=7):

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(days)

    result.columns = [
        "Date",
        "Predicted_AQI",
        "Lower_Bound",
        "Upper_Bound"
    ]

    result["Predicted_AQI"] = result["Predicted_AQI"].round(1)

    return result

if __name__ == "__main__":
    model = load_model()
    predictions = predict_aqi(model, days=7)
    print(predictions)