import pandas as pd

def load_data(filepath="data/city_day.csv"):
    df = pd.read_csv(filepath)
    return df
def preprocess(df):
    df = df[df["City"] == "Delhi"]
    df["Date"] = pd.to_datetime(df["Date"])

    df = df.dropna(subset=["AQI"])

    df = df.sort_values("Date")

    df["Day"] = df["Date"].dt.day
    df["Weekday"] = df["Date"].dt.dayofweek

    df = df.reset_index(drop=True)
    return df

def save_cleaned(df, output_path="data/cleaned_aqi.csv"):
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")

if __name__ == "__main__":
    df = load_data()
    df = preprocess(df)
    save_cleaned(df)
    print(df.head())