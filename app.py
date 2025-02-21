# New FastAPI application using tailor2 schema
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import asyncpg
from typing import Optional, List
from enum import Enum
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fit_zone_calculator import FitZoneCalculator

app = FastAPI()

# Database connection settings
DB_CONFIG = {
    "database": "tailor2",
    "user": "seandavey",
    "password": "securepassword",
    "host": "localhost"
}

# Enums for constrained fields
class FitType(str, Enum):
    TIGHT = "Tight"
    PERFECT = "Perfect"
    RELAXED = "Relaxed"
    OVERSIZED = "Oversized"

class Gender(str, Enum):
    MEN = "Men"
    WOMEN = "Women"
    UNISEX = "Unisex"

class Unit(str, Enum):
    INCHES = "in"
    CENTIMETERS = "cm"

# Pydantic Models
class Brand(BaseModel):
    id: int
    name: str
    default_unit: Unit
    size_guide_url: Optional[str]

class SizeGuide(BaseModel):
    brand: str
    gender: Gender
    category: str
    size_label: str
    chest_range: Optional[str]
    sleeve_range: Optional[str]
    waist_range: Optional[str]
    neck_range: Optional[str]
    unit: Unit

class UserFitZone(BaseModel):
    category: str
    tight_min: Optional[float]
    perfect_min: float
    perfect_max: float
    relaxed_max: Optional[float]

class UserGarment(BaseModel):
    brand_id: int
    category: str
    size_label: str
    chest_range: str
    fit_feedback: Optional[str]

class FitFeedback(BaseModel):
    overall_fit: str
    chest_fit: Optional[str]
    sleeve_fit: Optional[str]
    neck_fit: Optional[str]
    waist_fit: Optional[str]

# Connection Functions
async def get_pool():
    return await asyncpg.create_pool(**DB_CONFIG)

def get_db():
    return psycopg2.connect(
        dbname=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        cursor_factory=RealDictCursor
    )

# Create connection pool on startup
pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await get_pool()

@app.on_event("shutdown")
async def shutdown():
    if pool:
        await pool.close()

# Start with basic structure and add endpoints one by one 

@app.get("/user/{user_id}/closet")
async def get_closet(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                ug.id as garment_id,
                b.name as brand_name,
                ug.category as garment_name,
                ug.size_label as size,
                ug.chest_range as chest_range,
                ug.fit_feedback,
                ug.created_at
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            WHERE ug.user_id = %s 
            AND ug.owns_garment = true
            ORDER BY ug.created_at DESC
        """, (user_id,))
        
        garments = cur.fetchall()
        print(f"Raw SQL results: {garments}")  # Debug log
        
        formatted_garments = [{
            "id": g["garment_id"],
            "brand": g["brand_name"],
            "category": g["garment_name"],
            "size": g["size"],
            "chestRange": g["chest_range"],
            "fitFeedback": g["fit_feedback"],
            "createdAt": g["created_at"].isoformat() if g["created_at"] else None,
            "ownsGarment": True
        } for g in garments]
        
        print(f"Formatted response: {formatted_garments}")  # Debug log
        return formatted_garments
        
    finally:
        cur.close()
        conn.close()

@app.get("/user/{user_id}/measurements")
async def get_user_measurements(user_id: str):
    try:
        # Get garments
        garments = get_user_garments(user_id)
        
        # Calculate fit zones
        calculator = FitZoneCalculator(user_id)
        fit_zone = calculator.calculate_chest_fit_zone(garments)
        
        # Cache results in user_fit_zones
        save_fit_zone(user_id, 'chest', fit_zone)
        
        # Return response
        return format_measurements_response(garments, fit_zone)
    except Exception as e:
        print(f"Error in get_user_measurements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/ideal_measurements")
async def get_ideal_measurements(user_id: str):
    """Get user's ideal measurements based on their fit zones"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        try:
            # Get user's fit zones
            cur.execute("""
                SELECT category, perfect_min, perfect_max
                FROM user_fit_zones
                WHERE user_id = %s
            """, (user_id,))
            
            fit_zones = cur.fetchall()
            
            # Format response
            measurements = [{
                "type": zone["category"],
                "min": float(zone["perfect_min"]),
                "max": float(zone["perfect_max"]),
                "unit": "in"
            } for zone in fit_zones]
            
            # If no fit zones found, return default chest measurement
            if not measurements:
                measurements = [{
                    "type": "chest",
                    "min": 40.0,
                    "max": 42.0,
                    "unit": "in"
                }]
            
            return measurements
            
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        print(f"Error in get_ideal_measurements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add these helper functions
def get_user_garments(user_id: str) -> list:
    """Get all owned garments for a user"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                b.name as brand,
                ug.category as garment_name,
                CASE 
                    WHEN ug.chest_range ~ '^[0-9]+(\.[0-9]+)?-[0-9]+(\.[0-9]+)?$' THEN 
                        (CAST(split_part(ug.chest_range, '-', 1) AS FLOAT) + 
                         CAST(split_part(ug.chest_range, '-', 2) AS FLOAT)) / 2
                    WHEN ug.chest_range ~ '^[0-9]+(\.[0-9]+)?$' THEN 
                        CAST(ug.chest_range AS FLOAT)
                    ELSE NULL
                END as chest_value,
                ug.size_label as size,
                ug.owns_garment,
                ug.fit_feedback as fit_type,
                uff.chest_fit as chest_feedback,
                ug.chest_range
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
            WHERE ug.user_id = %s
            AND ug.owns_garment = true
            AND ug.chest_range IS NOT NULL
        """, (user_id,))
        
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def save_fit_zone(user_id: str, category: str, fit_zone: dict):
    """Save the calculated fit zone to the database"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Category must be 'Tops' per database constraint
        normalized_category = 'Tops'
        
        cur.execute("""
            INSERT INTO user_fit_zones 
            (user_id, category, tight_min, tight_max, good_min, good_max, relaxed_min, relaxed_max)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, category) 
            DO UPDATE SET 
                tight_min = EXCLUDED.tight_min,
                tight_max = EXCLUDED.tight_max,
                good_min = EXCLUDED.good_min,
                good_max = EXCLUDED.good_max,
                relaxed_min = EXCLUDED.relaxed_min,
                relaxed_max = EXCLUDED.relaxed_max
        """, (
            user_id, 
            normalized_category,
            fit_zone.get('tight_min'),
            fit_zone.get('tight_max'),
            fit_zone.get('good_min'),
            fit_zone.get('good_max'),
            fit_zone.get('relaxed_min'),
            fit_zone.get('relaxed_max')
        ))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def format_measurements_response(garments: list, fit_zone: dict) -> dict:
    """Format the measurements response for the API"""
    return {
        "measurementType": "chest",
        "preferredRange": {
            "min": fit_zone['good_min'],
            "max": fit_zone['good_max']
        },
        "measurements": [{
            "brand": g["brand"],
            "garmentName": g["garment_name"],
            "value": float(g["chest_value"]) if g["chest_value"] is not None else 0.0,
            "size": g["size"],
            "ownsGarment": bool(g["owns_garment"]),
            "fitType": g["chest_feedback"] or g["fit_type"] or "Unknown",
            "feedback": g["chest_feedback"] or g["fit_type"] or ""
        } for g in garments]
    }

@app.get("/scan_history")
async def get_scan_history(user_id: str):
    """Get user's scan history"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                ug.id,
                b.name as brand,
                ug.category,
                ug.size_label as size,
                ug.chest_range,
                ug.fit_feedback,
                ug.created_at,
                ug.owns_garment
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            WHERE ug.user_id = %s
            ORDER BY ug.created_at DESC
        """, (user_id,))
        
        scans = cur.fetchall()
        
        return [{
            "id": s["id"],
            "brand": s["brand"],
            "category": s["category"],
            "size": s["size"],
            "chestRange": s["chest_range"],
            "fitFeedback": s["fit_feedback"],
            "createdAt": s["created_at"].isoformat() if s["created_at"] else None,
            "ownsGarment": bool(s["owns_garment"])
        } for s in scans]
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",  # Use string format
        host="0.0.0.0",
        port=8005,
        reload=True
    ) 