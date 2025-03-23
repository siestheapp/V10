# New FastAPI application using tailor2 schema
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import asyncpg
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fit_zone_calculator import FitZoneCalculator
import json
from urllib.parse import urlparse

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

class GarmentSubmission(BaseModel):
    productLink: str
    sizeLabel: str
    userId: int

class FeedbackSubmission(BaseModel):
    garment_id: int
    feedback: Dict[str, int]  # measurement_name -> feedback_value

class GarmentRequest(BaseModel):
    product_code: str
    scanned_price: float
    scanned_size: Optional[str]

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
    pool = await asyncpg.create_pool(**DB_CONFIG)

@app.on_event("shutdown")
async def shutdown():
    global pool
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
                ug.category,
                ug.size_label as size,
                ug.chest_range,
                sg.sleeve_min,
                sg.sleeve_max,
                sg.waist_min,
                sg.waist_max,
                sg.neck_min,
                sg.neck_max,
                ug.fit_feedback,
                ug.created_at,
                ug.owns_garment,
                ug.product_name
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN size_guides_v2 sg ON 
                ug.brand_id = sg.brand_id AND 
                ug.size_label = sg.size_label AND
                ug.category = sg.category
            WHERE ug.user_id = %s 
            AND ug.owns_garment = true
            ORDER BY ug.category, ug.created_at DESC
        """, (user_id,))
        
        garments = cur.fetchall()
        print(f"Raw SQL results: {garments}")  # Debug log
        
        def format_measurement(value):
            """Format a measurement value without trailing .00 for integers"""
            if isinstance(value, (int, float)):
                return str(int(value)) if value.is_integer() else f"{value:.2f}"
            return str(value)
        
        formatted_garments = []
        for g in garments:
            measurements = {}
            
            # Add chest measurement if available
            if g["chest_range"]:
                measurements["chest"] = str(g["chest_range"])
            
            # Add sleeve measurement if available
            if g["sleeve_min"] is not None and g["sleeve_max"] is not None:
                sleeve_min = format_measurement(float(g["sleeve_min"]))
                sleeve_max = format_measurement(float(g["sleeve_max"]))
                measurements["sleeve"] = f"{sleeve_min}-{sleeve_max}"
            
            # Add waist measurement if available
            if g["waist_min"] is not None and g["waist_max"] is not None:
                waist_min = format_measurement(float(g["waist_min"]))
                waist_max = format_measurement(float(g["waist_max"]))
                measurements["waist"] = f"{waist_min}-{waist_max}"
                
            # Add neck measurement if available
            if g["neck_min"] is not None and g["neck_max"] is not None:
                neck_min = format_measurement(float(g["neck_min"]))
                neck_max = format_measurement(float(g["neck_max"]))
                measurements["neck"] = f"{neck_min}-{neck_max}"
            elif g["neck_min"] is not None:
                measurements["neck"] = format_measurement(float(g["neck_min"]))
            
            garment = {
                "id": g["garment_id"],
                "brand": g["brand_name"],
                "category": g["category"],
                "size": g["size"],
                "measurements": measurements,
                "fitFeedback": g["fit_feedback"],
                "createdAt": g["created_at"].isoformat() if g["created_at"] else None,
                "ownsGarment": bool(g["owns_garment"]),
                "productName": g["product_name"]
            }
            formatted_garments.append(garment)
        
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
        print(f"Found garments for measurements: {garments}")  # Debug log
        
        # Calculate fit zones
        calculator = FitZoneCalculator(user_id)
        fit_zone = calculator.calculate_chest_fit_zone(garments)
        print(f"Calculated fit zone: {fit_zone}")  # Debug log
        
        # Format and return response
        response = format_measurements_response(garments, fit_zone)
        print(f"Final response: {response}")  # Debug log
        return response
    except Exception as e:
        print(f"Error in get_user_measurements: {str(e)}")  # Error log
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
                ug.chest_range,
                ug.size_label as size,
                ug.owns_garment,
                ug.fit_feedback,  -- Use the actual column name
                uff.chest_fit as chest_feedback
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
            WHERE ug.user_id = %s
            AND ug.owns_garment = true
            AND ug.chest_range IS NOT NULL
        """, (user_id,))
        
        garments = cur.fetchall()
        print(f"Found garments: {garments}")
        return garments
    except Exception as e:
        print(f"Error getting garments: {str(e)}")
        raise
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

def format_measurements_response(garments, fit_zone):
    return {
        "Tops": {
            "tightRange": {
                "min": fit_zone['tight_range']['min'] or 36.0,
                "max": fit_zone['tight_range']['max'] or 39.0
            },
            "goodRange": {
                "min": fit_zone['good_range']['min'] or 39.0,
                "max": fit_zone['good_range']['max'] or 41.0
            },
            "relaxedRange": {
                "min": fit_zone['relaxed_range']['min'] or 41.0,
                "max": fit_zone['relaxed_range']['max'] or 47.0
            },
            "garments": [
                {
                    "brand": g["brand"],
                    "garmentName": g["garment_name"],
                    "chestRange": g["chest_range"],  # Pass through the original range
                    "chestValue": float(g["chest_range"].split("-")[0]) if "-" in g["chest_range"] else float(g["chest_range"]),
                    "size": g["size"],
                    "fitFeedback": g["fit_feedback"] or "",
                    "feedback": g["chest_feedback"] or ""
                } for g in garments
            ]
        }
    }

@app.get("/scan_history")
async def get_scan_history(user_id: int):
    try:
        return [
            {
                "id": 1,
                "productCode": "475352",  # Changed to camelCase
                "scannedSize": "L",
                "scannedPrice": 29.90,
                "scannedAt": "2024-02-24T10:30:00Z",
                "name": "Waffle Crew Neck T-Shirt",
                "category": "Tops",
                "imageUrl": "https://example.com/image.jpg",
                "productUrl": "https://uniqlo.com/product/475352",
                "brand": "Uniqlo"
            }
            # Add more history items...
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_new_garment(product_link: str, size_label: str, user_id: int):
    # Step 1: Create the garment entry and get measurements
    with db.connection() as conn:
        garment_id = conn.execute(
            "SELECT process_new_garment(%s, %s, %s)",
            (product_link, size_label, user_id)
        ).fetchone()[0]

        # Step 2: Get the brand_id for the newly created garment
        brand_id = conn.execute(
            "SELECT brand_id FROM user_garments WHERE id = %s",
            (garment_id,)
        ).fetchone()[0]

        # Step 3: Get fit feedback questions for this brand
        feedback_ranges = conn.execute(
            "SELECT * FROM get_brand_fit_feedback_ranges(%s)",
            (brand_id,)
        ).fetchall()

        # Step 4: For each feedback range, collect and store feedback
        for range in feedback_ranges:
            # Here you would collect feedback from the user through your API
            feedback_value = get_user_feedback(range)  # This is a placeholder function
            
            conn.execute(
                "SELECT store_fit_feedback(%s, %s, %s)",
                (garment_id, range.measurement_name, feedback_value)
            )

    return garment_id

@app.get("/brands/{brand_id}/measurements")
async def get_brand_measurements(brand_id: int):
    try:
        async with pool.acquire() as conn:
            # First verify the brand exists
            brand = await conn.fetchrow("SELECT name FROM brands WHERE id = $1", brand_id)
            if not brand:
                raise HTTPException(status_code=404, detail="Brand not found")

            # Get all available measurements for this brand
            size_guide = await conn.fetchrow("""
                SELECT 
                    chest_range,
                    neck_range,
                    sleeve_range,
                    waist_range
                FROM size_guides 
                WHERE brand_id = $1 
                LIMIT 1
            """, brand_id)

            if not size_guide:
                print(f"No size guide found for brand {brand_id}")
                measurements = ['overall']  # Default to just overall if no size guide
            else:
                # Build measurements array based on what's available
                measurements = ['overall']  # Always include overall
                if size_guide.get('chest_range'):
                    measurements.append('chest')
                if size_guide.get('neck_range'):
                    measurements.append('neck')
                if size_guide.get('sleeve_range'):
                    measurements.append('sleeve')
                if size_guide.get('waist_range'):
                    measurements.append('waist')

            return {
                "measurements": measurements,
                "feedbackOptions": [
                    {"value": 1, "label": "Too tight"},
                    {"value": 2, "label": "Tight but I like it"},
                    {"value": 3, "label": "Good"},
                    {"value": 4, "label": "Loose but I like it"},
                    {"value": 5, "label": "Too loose"}
                ]
            }
    except Exception as e:
        print(f"Error in get_brand_measurements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/garments/submit")
async def submit_garment_and_feedback(submission: GarmentSubmission):
    """Submit a new garment with feedback"""
    try:
        print(f"Received submission: {submission}")
        
        async with pool.acquire() as conn:
            # First check if this garment already exists
            existing_garment = await conn.fetchrow("""
                SELECT id FROM user_garments 
                WHERE user_id = $1 
                AND brand_id = (
                    SELECT id FROM brands 
                    WHERE name = 'Banana Republic'
                )
                AND category = 'Tops'
                AND size_label = $2
                AND created_at > NOW() - INTERVAL '1 hour'
            """, submission.userId, submission.sizeLabel)
            
            if existing_garment:
                return {
                    "garment_id": existing_garment['id'],
                    "status": "existing"
                }
            
            # If no recent duplicate, proceed with insert
            garment_id = await conn.fetchval("""
                INSERT INTO user_garments (
                    user_id, 
                    brand_id,
                    category,
                    size_label,
                    chest_range,
                    product_link,
                    owns_garment
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """, 
                submission.userId,
                brand_id,
                'Tops',
                submission.sizeLabel,
                'N/A',
                submission.productLink,
                True
            )
            
            return {
                "garment_id": garment_id,
                "status": "success"
            }
            
    except Exception as e:
        print(f"Error submitting garment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_garment")
async def process_garment(garment: GarmentRequest):
    try:
        print(f"Processing garment: {garment}")
        
        async with pool.acquire() as conn:
            # First get the brand and product info
            brand = await conn.fetchrow("""
                SELECT id, name, measurement_type 
                FROM brands 
                WHERE name = 'Uniqlo'
            """)

            if not brand:
                raise HTTPException(status_code=400, detail="Brand not found")

            if brand['measurement_type'] == 'product_level':
                # Get Uniqlo product-specific measurements
                measurements = await conn.fetchrow("""
                    SELECT 
                        product_code,
                        size,
                        chest_range,
                        length_range,
                        sleeve_range,
                        name
                    FROM product_measurements 
                    WHERE product_code = $1 AND size = $2
                """, garment.product_code, garment.scanned_size)
                
                if not measurements:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"No measurements found for product {garment.product_code} size {garment.scanned_size}"
                    )

                return {
                    "id": measurements['product_code'],
                    "brand": "Uniqlo",
                    "name": measurements['name'] or "Waffle Crew Neck T-Shirt",
                    "size": measurements['size'],
                    "price": garment.scanned_price,
                    "measurements": {
                        "chest": measurements['chest_range'],
                        "length": measurements['length_range'],
                        "sleeve": measurements['sleeve_range']
                    },
                    "productUrl": "https://www.uniqlo.com/us/en/products/E460318-000/00?colorDisplayCode=30&sizeDisplayCode=004",
                    "imageUrl": "https://image.uniqlo.com/UQ/ST3/us/imagesgoods/460318/item/usgoods_30_460318.jpg"
                }
            else:
                # Get brand-level measurements from size_guides
                measurements = await conn.fetchrow("""
                    SELECT * FROM size_guides 
                    WHERE brand_id = $1 AND size_label = $2
                """, brand['id'], garment.scanned_size)

                return {
                    "id": garment.product_code,
                    "brand": brand['name'],
                    "name": "Unknown",
                    "size": garment.scanned_size,
                    "price": garment.scanned_price,
                    "measurements": {
                        "chest": measurements['chest_range'] if measurements else None,
                        "length": measurements['length_range'] if measurements else None,
                        "sleeve": measurements['sleeve_range'] if measurements else None
                    }
                }
            
    except Exception as e:
        print(f"Error processing garment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/user/{user_id}")
async def get_test_user_data(user_id: str):
    """Get comprehensive test data for a user"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Get basic user info
        cur.execute("""
            SELECT 
                u.id,
                u.email,
                u.created_at,
                u.gender,
                u.unit_preference,
                (
                    SELECT COUNT(*) 
                    FROM user_garments 
                    WHERE user_id = u.id AND owns_garment = true
                ) as total_garments,
                (
                    SELECT created_at 
                    FROM user_garments 
                    WHERE user_id = u.id 
                    ORDER BY created_at DESC 
                    LIMIT 1
                ) as last_garment_input,
                (
                    SELECT array_agg(DISTINCT brand_name) 
                    FROM user_garments 
                    WHERE user_id = u.id AND owns_garment = true
                ) as brands_owned
            FROM users u
            WHERE u.id = %s
        """, (user_id,))
        
        user_info = cur.fetchone()
        
        # Get fit zones
        cur.execute("""
            SELECT 
                tight_min, tight_max,
                good_min, good_max,
                relaxed_min, relaxed_max
            FROM user_fit_zones
            WHERE user_id = %s AND category = 'Tops'
        """, (user_id,))
        
        fit_zones = cur.fetchone()
        
        # Get recent feedback
        cur.execute("""
            SELECT 
                ug.id,
                COALESCE(ug.product_name, ug.category) as garment_name,
                ug.brand_name,
                ug.size_label,
                COALESCE(uff.overall_fit, ug.fit_feedback) as feedback
            FROM user_garments ug
            LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
            WHERE ug.user_id = %s AND ug.owns_garment = true
            ORDER BY ug.created_at DESC
            LIMIT 5
        """, (user_id,))
        
        feedback = cur.fetchall()
        
        return {
            "id": user_info['id'],
            "email": user_info['email'],
            "createdAt": user_info['created_at'].isoformat(),
            "gender": user_info['gender'],
            "unitPreference": user_info['unit_preference'],
            "totalGarments": user_info['total_garments'],
            "lastGarmentInput": user_info['last_garment_input'].isoformat() if user_info['last_garment_input'] else None,
            "brandsOwned": user_info['brands_owned'] or [],
            "fitZones": {
                "tightMin": float(fit_zones['tight_min']) if fit_zones and fit_zones['tight_min'] else 0.0,
                "tightMax": float(fit_zones['tight_max']) if fit_zones and fit_zones['tight_max'] else 0.0,
                "goodMin": float(fit_zones['good_min']) if fit_zones and fit_zones['good_min'] else 0.0,
                "goodMax": float(fit_zones['good_max']) if fit_zones and fit_zones['good_max'] else 0.0,
                "relaxedMin": float(fit_zones['relaxed_min']) if fit_zones and fit_zones['relaxed_min'] else 0.0,
                "relaxedMax": float(fit_zones['relaxed_max']) if fit_zones and fit_zones['relaxed_max'] else 0.0
            },
            "recentFeedback": [{
                "id": f['id'],
                "garmentName": f['garment_name'],
                "brand": f['brand_name'],
                "size": f['size_label'],
                "feedback": f['feedback'] or "No feedback"
            } for f in feedback]
        }
        
    except Exception as e:
        print(f"Error in get_test_user_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/brands")
async def get_brands():
    """Get all brands with their categories and measurements for men's clothing"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        try:
            # Get brands that have men's size guides
            cur.execute("""
                SELECT DISTINCT b.id, b.name 
                FROM brands b
                INNER JOIN size_guides_v2 sg ON b.id = sg.brand_id
                WHERE sg.gender = 'Men'
                ORDER BY b.name
            """)
            brands = cur.fetchall()
            print(f"Found {len(brands)} men's brands")
            
            formatted_brands = []
            for brand in brands:
                # For each brand, get its categories and measurements from men's size guides
                cur.execute("""
                    SELECT DISTINCT 
                        category,
                        measurements_available
                    FROM size_guides_v2 
                    WHERE brand_id = %s
                    AND gender = 'Men'
                """, (brand["id"],))
                
                size_guides = cur.fetchall()
                
                # Collect unique categories and measurements
                categories = set()
                measurements = set()
                
                for guide in size_guides:
                    if guide["category"]:
                        categories.add(guide["category"])
                    if guide["measurements_available"]:
                        measurements.update(guide["measurements_available"])
                
                formatted_brand = {
                    "id": brand["id"],
                    "name": brand["name"],
                    "categories": list(categories),
                    "measurements": list(measurements)
                }
                print(f"Formatted brand: {formatted_brand}")
                formatted_brands.append(formatted_brand)
            
            print(f"Returning {len(formatted_brands)} formatted men's brands")
            return formatted_brands
            
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        print(f"Error in get_brands: {str(e)}")
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",  # Use string format
        host="0.0.0.0",
        port=8005,
        reload=True
    ) 