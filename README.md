# database_design
# Air Quality Prediction System

## Data Flow

1. **Data Collection**
   - Sensor readings are collected and sent to the API.
   - Data is received via `POST /add_reading/` and stored in PostgreSQL.

2. **Data Retrieval**
   - Fetch all readings: `GET /readings/`
   - Fetch readings by air quality level: `GET /readings/{level}/`

3. **Data Update**
   - Modify an existing air quality reading: `PUT /update_quality/{reading_id}/`

4. **Data Deletion**
   - Remove a reading from the database: `DELETE /delete/{reading_id}/`

5. **Prediction Process**
   - Data is preprocessed and passed to the `svm-model.pkl`.
   - Predictions are generated based on historical data.
   - Results are stored in MongoDB for further analysis.

6. **System Components**
   - **FastAPI**: API layer for CRUD operations and predictions.
   - **PostgreSQL**: Stores structured air quality readings.
   - **MongoDB**: Stores prediction results.
   - **SVM Model**: Predicts air quality classification based on input data.

7. **Pipeline Execution**
   - Data is fetched, cleaned, and prepared.
   - ML model makes predictions.
   - Predictions are logged and stored for retrieval.

## Key Components

### 1. Database System
- **PostgreSQL**: Stores structured air quality readings, station information, and prediction logs.
- **MongoDB**: Stores prediction results and model performance metrics in a flexible document format.

### 2. API Layer
- **FastAPI**: Provides RESTful endpoints for data retrieval and submission.
- Handles CRUD operations for air quality data and predictions.

### 3. Machine Learning Model
- **SVM Model**: Predicts air quality parameters based on historical data.
- Saved as `svm_model.pkl` in the project.

## Installation Requirements

### Core Dependencies
```
fastapi==0.103.1
uvicorn==0.23.2
sqlalchemy==2.0.20
psycopg2-binary==2.9.7
pymongo==4.5.0
tensorflow==2.13.0
numpy==1.24.3
pandas==2.1.0
scikit-learn==1.3.0
```

## Setup and Run

### 1. Database Setup
- Install and configure PostgreSQL and MongoDB.
- Create necessary tables and collections.

## API Usage

### Key Endpoints
- `GET /readings/` - Retrieve all air quality readings.
- `GET /readings/{level}/` - Retrieve air quality readings filtered by level.
- `POST /add_reading/` - Add new air quality readings.
- `PUT /update_quality/{reading_id}/` - Update an existing air quality reading.
- `DELETE /delete/{reading_id}/` - Delete an air quality reading.

### FastAPI App
```python
# FastAPI App
app = FastAPI()

# MongoDB Connection
MONGO_URI = "mongodb+srv://jkiguta:vMve9B2a2oUKPVw0@cluster0.zh7yx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client["air_quality_db"]
```

## Data Pipeline Process

1. **Data Acquisition**: Collect data from sensors and external sources.
2. **Preprocessing**: Clean data and extract relevant features.
3. **Prediction**: Apply the ML model to make forecasts.
4. **Storage**: Save results to PostgreSQL and MongoDB.
5. **API Access**: Make data available through FastAPI endpoints.

This streamlined workflow ensures efficient data handling, storage, and real-time predictions for air quality monitoring.

