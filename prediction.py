import requests
import joblib # For loading the trained model
import numpy as np

# API Base URL
BASE_URL = "https://database-design-zfw5.onrender.com"

# Fetch Latest Air Quality Reading
def fetch_latest_reading():
    response = requests.get(f"{BASE_URL}/readings")
    if response.status_code == 200:
        readings = response.json()
        if readings:
            latest_reading = readings[-1]  # Assuming the last entry is the latest
            return latest_reading
        else:
            print("No readings found.")
    else:
        print("Error fetching readings:", response.status_code)
    return None

# Load Model
def load_model():
    model = joblib.load("svm_model.pkl") 
    return model

# Prepare Data & Predict
def make_prediction():
    latest_reading = fetch_latest_reading()
    if latest_reading:
        model = load_model()

        # Extract relevant features from the reading
        features = np.array([
            latest_reading["temperature"],
            latest_reading["humidity"],
            latest_reading["pm25"],
            latest_reading["pm10"],
            latest_reading["no2"],
            latest_reading["so2"],
            latest_reading["co"]
        ]).reshape(1, -1)

        # Make prediction
        prediction = model.predict(features)
        print("Predicted Air Quality Level:", prediction[0])
    else:
        print("No data available for prediction.")

# Run Prediction Task
make_prediction()