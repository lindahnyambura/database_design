from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2 import sql

# FastAPI app instance
app = FastAPI()

# Connect to PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname="airquality",  # your database name
        user="postgres",  # your PostgreSQL username
        password="***",  # your password
        host="localhost",  # server IP or 'localhost' if running on the same machine
        port="5432"  # PostgreSQL default port
    )
    return conn

# Pydantic model for Air Quality Readings
class AirQualityReading(BaseModel):
    reading_id: Optional[int] = None
    temperature: float
    humidity: float
    pm25: float
    pm10: float
    no2: float
    so2: float
    co: float

# POST /readings - Add new reading
@app.post("/readings/")
async def create_reading(reading: AirQualityReading):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO air_quality_readings (temperature, humidity, pm25, pm10, no2, so2, co)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING reading_id;
        """, (reading.temperature, reading.humidity, reading.pm25, reading.pm10, reading.no2, reading.so2, reading.co))
        reading_id = cursor.fetchone()[0]
        conn.commit()
        return {"reading_id": reading_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error creating reading")
    finally:
        cursor.close()
        conn.close()

# GET /readings/{reading_id} - Get a specific reading by ID
@app.get("/readings/{reading_id}")
async def get_reading(reading_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM air_quality_readings WHERE reading_id = %s;
    """, (reading_id,))
    reading = cursor.fetchone()

    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "reading_id": reading[0],
        "temperature": reading[1],
        "humidity": reading[2],
        "pm25": reading[3],
        "pm10": reading[4],
        "no2": reading[5],
        "so2": reading[6],
        "co": reading[7],
    }

# PUT /readings/{reading_id} - Update a reading by ID
@app.put("/readings/{reading_id}")
async def update_reading(reading_id: int, reading: AirQualityReading):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE air_quality_readings SET temperature = %s, humidity = %s, pm25 = %s, pm10 = %s, no2 = %s, so2 = %s, co = %s, 
            WHERE reading_id = %s;
        """, (reading.temperature, reading.humidity, reading.pm25, reading.pm10, reading.no2, reading.so2, reading.co, 
              reading_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reading not found")
        
        return {"message": "Reading updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error updating reading")
    finally:
        cursor.close()
        conn.close()

# DELETE /readings/{reading_id} - Delete a reading by ID
@app.delete("/readings/{reading_id}")
async def delete_reading(reading_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM air_quality_readings WHERE reading_id = %s;
        """, (reading_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reading not found")
        
        return {"message": "Reading deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error deleting reading")
    finally:
        cursor.close()
        conn.close()
