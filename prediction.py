import requests
import tensorflow as tf
import pandas as pd
import logging
from datetime import datetime
import os
import urllib.request

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'air_quality_prediction_{datetime.now().strftime("%Y%m%d")}.log'
)
logger = logging.getLogger()
# Configurable parameters
API_URL_LATEST = "http://http://127.0.0.1:8000/air_quality/latest"
API_URL_LOG = "http://http://127.0.0.1:8000/predictions"
MODEL_URL = "https://github.com/lindahnyambura/database_design/blob/main/saved-model/nn_model_rmsprop.keras"
MODEL_PATH = "nn_model_rmsprop.keras"
REQUIRED_FEATURES = ["temperature", "humidity", "pm25", "pm10", "no2", "so2", "co"]

# Download model if not already present
if not os.path.exists(MODEL_PATH):
    logger.info(f"Downloading model from {MODEL_URL}")
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        logger.info("Model downloaded successfully")
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        raise


def fetch_latest_data():
    """Fetch the latest air quality data from the API."""
    logger.info(f"Fetching data from {API_URL_LATEST}")
    try:
        response = requests.get(API_URL_LATEST)
        response.raise_for_status()
        logger.info("Successfully fetched latest data")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data: {e}")
        return None


def handle_missing_data(data):
    """Handle missing values in the dataset."""
    logger.info("Checking for missing data")
    df = pd.DataFrame([data])
    missing_features = [feature for feature in REQUIRED_FEATURES if feature not in df.columns]

    if missing_features:
        logger.warning(f"Missing features: {missing_features}")
        for feature in missing_features:
            df[feature] = 0

    for feature in REQUIRED_FEATURES:
        if df[feature].isna().any():
            logger.warning(f"NaN values found in {feature}, filling with mean")
            df[feature] = df[feature].fillna(df[feature].mean())

    logger.info("Missing data handling complete")
    return df


def preprocess_data(df):
    """Preprocess the data for the model."""
    logger.info("Preprocessing data")
    for feature in REQUIRED_FEATURES:
        df[feature] = pd.to_numeric(df[feature], errors='coerce')

    input_data = df[REQUIRED_FEATURES].values
    input_data = input_data.reshape((input_data.shape[0], input_data.shape[1], 1))
    logger.info(f"Data preprocessed, shape: {input_data.shape}")
    return input_data


def make_prediction(input_data):
    """Make prediction using the CNN model."""
    logger.info("Loading model and making prediction")
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        prediction = model.predict(input_data)
        predicted_class = prediction.argmax(axis=-1)[0]
        logger.info(f"Prediction successful: {predicted_class}")
        return int(predicted_class)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return None


def log_result_to_database(data, prediction):
    """Log the prediction result back to the database."""
    logger.info("Logging prediction result to database")
    payload = {
        "original_data": data,
        "prediction": int(prediction),
        "timestamp": datetime.now().isoformat()
    }

    try:
        response = requests.post(API_URL_LOG, json=payload)
        response.raise_for_status()
        logger.info("Successfully logged prediction to database")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to log prediction to database: {e}")
        return False
def main():
    """Main function to run the prediction workflow."""
    logger.info("Starting air quality prediction workflow")
    latest_data = fetch_latest_data()

    if latest_data:
        df = handle_missing_data(latest_data)
        input_data = preprocess_data(df)
        result = make_prediction(input_data)

        if result is not None:
            log_success = log_result_to_database(latest_data, result)
            print(f"Predicted Air Quality Classification: {result}")
            print(f"Result logged to database: {'Success' if log_success else 'Failed'}")
        else:
            print("Prediction failed")
    else:
        print("Could not make prediction: No data available")

    logger.info("Air quality prediction workflow completed")


if __name__ == "__main__":
    main()
