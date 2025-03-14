from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional

# FastAPI App
app = FastAPI()

# MongoDB Connection
MONGO_URI = "mongodb+srv://jkiguta:vMve9B2a2oUKPVw0@cluster0.zh7yx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client["air_quality_db"]

# Collections
air_quality_readings = db["air_quality_readings"]
air_quality_levels = db["air_quality_levels"]
locations = db["locations"]
air_quality_log = db["air_quality_log"]

# Pydantic Models for Validation
class Locations(BaseModel):
    location_id: int
    population_density: int
    industrial_proximity_km: float

class AirQualityReading(BaseModel):
    reading_id: Optional[int] = None
    temperature: float
    humidity: float
    pm25: float
    pm10: float
    no2: float
    so2: float
    co: float
    location_id: Optional[int] = None

class AirQualityLog(BaseModel):
    location_id: int
    old_quality: str
    new_quality: str
    change_time: datetime

class AirQualityLevel(BaseModel):
    level_id: int
    quality_level: str


# **1. CREATE - Add New Air Quality Reading**
@app.post("/add_reading/")
async def add_air_quality_reading(data: AirQualityReading):
    result = await air_quality_readings.insert_one(data.dict())
    return {"message": "Reading added", "id": str(result.inserted_id)}


# **2. READ - Get All Air Quality Readings**
@app.get("/readings/", response_model=List[AirQualityReading])
async def get_all_readings():
    readings = await air_quality_readings.find({}, {"_id": 0}).to_list(length=100)  # Limit to 100 rows
    return readings


# **3. READ - Get Readings by Quality Level**
@app.get("/readings/{level}/", response_model=List[AirQualityReading])
async def get_air_quality_by_level(level: str):
    # Find all level_id(s) corresponding to the given quality level
    level_docs = await air_quality_levels.find({"quality_level": level}).to_list(None)
    
    if not level_docs:
        raise HTTPException(status_code=404, detail="Quality level not found.")

    # Extract all level_id values
    level_ids = [doc["level_id"] for doc in level_docs]

    # Find air quality readings where reading_id matches any of the level_id(s)
    readings = await air_quality_readings.find({"reading_id": {"$in": level_ids}}, {"_id": 0}).to_list(None)

    if not readings:
        raise HTTPException(status_code=404, detail="No readings found for this quality level.")

    return readings


# **4. UPDATE - Update Air Quality Level & Log Changes**
@app.put("/update_quality/{reading_id}/")
async def update_air_quality_level(reading_id: int, new_level: str):
    old_doc = await air_quality_readings.find_one({"reading_id": reading_id})
    if not old_doc:
        raise HTTPException(status_code=404, detail="No record found.")

    old_level = old_doc.get("quality_level", "Unknown")  # Handle missing quality_level field

    # Log the change
    log_entry = {
        "reading_id": reading_id,
        "old_quality": old_level,
        "new_quality": new_level,
        "change_time": datetime.now(timezone.utc),
    }
    await air_quality_log.insert_one(log_entry)

    # Update the reading
    result = await air_quality_readings.update_one(
        {"reading_id": reading_id},
        {"$set": {"quality_level": new_level}},
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Update failed.")

    return {"message": "Quality level updated and logged."}


# **5. DELETE - Remove a Reading**
@app.delete("/delete/{reading_id}/")
async def delete_air_quality_reading(reading_id: int):
    result = await air_quality_readings.delete_one({"reading_id": reading_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No record found.")
    return {"message": "Deleted successfully."}


# **Run Locally with Uvicorn**
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
