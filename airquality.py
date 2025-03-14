from pymongo import MongoClient
from datetime import datetime, timezone

# Connect to MongoDB
client = MongoClient('mongodb+srv://jkiguta:vMve9B2a2oUKPVw0@cluster0.zh7yx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['air_quality_db']

# Collections
air_quality_readings = db['air_quality_readings']
air_quality_log = db['air_quality_log']
air_quality_errors = db['air_quality_errors']
locations = db['locations']
air_quality_levels = db['air_quality_levels']

# Sample Data
sample_data = [
    {
        "location": {"location_id": 1, "population_density": 5000, "industrial_proximity_km": 2.5},
        "temperature": 25.4,
        "humidity": 60.5,
        "pm25": 35.2,
        "pm10": 50.1,
        "no2": 12.5,
        "so2": 4.3,
        "co": 0.9,
        "quality_level": "Moderate"
    },
    {
        "location": {"location_id": 2, "population_density": 3000, "industrial_proximity_km": 1.2},
        "temperature": 28.1,
        "humidity": 55.3,
        "pm25": 40.8,
        "pm10": 65.2,
        "no2": 15.6,
        "so2": 5.1,
        "co": 1.1,
        "quality_level": "Poor"
    }
]
# CRUD Operations

## 1. CREATE - Add a new air quality reading
def add_air_quality_reading(data):
    air_quality_readings.insert_one(data)
    print("Added new air quality reading.")

## 2. READ - Get all air quality readings
def get_all_readings():
    return list(air_quality_readings.find({}, {"_id": 0}))

## 3. READ - Get air quality readings by quality level
def get_air_quality_by_level(level):
    return list(air_quality_readings.find({"quality_level": level}, {"_id": 0}))

## 4. UPDATE - Update air quality level and log changes
def update_air_quality_level(location_id, new_level):
    old_doc = air_quality_readings.find_one({"location.location_id": location_id})
    if not old_doc:
        return "No record found for this location."

    old_level = old_doc["quality_level"]

    log_entry = {
        "location_id": location_id,
        "old_quality": old_level,
        "new_quality": new_level,
        "change_time": datetime.now(timezone.utc)
    }
    air_quality_log.insert_one(log_entry)

    air_quality_readings.update_one(
        {"location.location_id": location_id},
        {"$set": {"quality_level": new_level}}
    )
    return "Updated quality level and logged change."

## 5. DELETE - Remove an air quality reading
def delete_air_quality_reading(location_id):
    result = air_quality_readings.delete_one({"location.location_id": location_id})
    return "Deleted successfully." if result.deleted_count > 0 else "No record found."

# Testing the Functions

print("All Readings:", get_all_readings())
print("Moderate Readings:", get_air_quality_by_level("Moderate"))

print(update_air_quality_level(1, "Poor"))

print(delete_air_quality_reading(2))

add_air_quality_reading(sample_data[1])
