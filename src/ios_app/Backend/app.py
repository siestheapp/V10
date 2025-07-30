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
import openai
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from sqlalchemy import text
import subprocess
import sys
from body_measurement_estimator import BodyMeasurementEstimator

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key (optional for development)
api_key = os.getenv("OPENAI_API_KEY")
openai_client = None

if api_key and api_key != "your-api-key-here":
    # Initialize OpenAI client only if valid key is provided
    openai_client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.openai.com/v1",  # Explicitly set the base URL
        max_retries=3,  # Add retries
        timeout=30.0  # Increase timeout
    )
else:
    print("Warning: OpenAI API key not set. Chat features will be disabled.")

# Database configuration
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def get_db_connection():
    """Get a connection to the database"""
    return psycopg2.connect(**DB_CONFIG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    global pool
    pool = await asyncpg.create_pool(**DB_CONFIG, statement_cache_size=0)
    print("Connected to database")
    yield
    # Cleanup
    if pool:
        await pool.close()
        print("Closed database connection")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ChatRequest(BaseModel):
    message: str
    user_id: int

class ChatMessage(BaseModel):
    user_id: int
    message: str

# Connection Functions
async def get_pool():
    return await asyncpg.create_pool(**DB_CONFIG, statement_cache_size=0)

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

@app.get("/user/{user_id}/closet")
async def get_closet(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                ug.id as garment_id,
                b.name as brand_name,
                c.name as category,
                ug.size_label as size,
                sge.chest_min,
                sge.chest_max,
                sge.sleeve_min,
                sge.sleeve_max,
                sge.waist_min,
                sge.waist_max,
                sge.neck_min,
                sge.neck_max,
                sge.hip_min,
                sge.hip_max,
                sge.center_back_length,
                ug.fit_feedback,
                ug.created_at,
                ug.owns_garment,
                ug.product_name,
                ug.image_url,
                ug.product_url,
                (SELECT feedback_code_id FROM user_garment_feedback 
                 WHERE user_garment_id = ug.id AND dimension = 'overall' 
                 ORDER BY created_at DESC LIMIT 1) as overall_feedback_code,
                (SELECT feedback_code_id FROM user_garment_feedback 
                 WHERE user_garment_id = ug.id AND dimension = 'chest' 
                 ORDER BY created_at DESC LIMIT 1) as chest_feedback_code,
                (SELECT feedback_code_id FROM user_garment_feedback 
                 WHERE user_garment_id = ug.id AND dimension = 'sleeve' 
                 ORDER BY created_at DESC LIMIT 1) as sleeve_feedback_code,
                (SELECT feedback_code_id FROM user_garment_feedback 
                 WHERE user_garment_id = ug.id AND dimension = 'neck' 
                 ORDER BY created_at DESC LIMIT 1) as neck_feedback_code,
                (SELECT feedback_code_id FROM user_garment_feedback 
                 WHERE user_garment_id = ug.id AND dimension = 'waist' 
                 ORDER BY created_at DESC LIMIT 1) as waist_feedback_code,
                (SELECT feedback_code_id FROM user_garment_feedback 
                 WHERE user_garment_id = ug.id AND dimension = 'hip' 
                 ORDER BY created_at DESC LIMIT 1) as hip_feedback_code
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN categories c ON ug.category_id = c.id
            LEFT JOIN size_guide_entries_with_brand sge ON 
                ug.size_guide_entry_id = sge.id
            WHERE ug.user_id = %s 
            AND ug.owns_garment = true
            ORDER BY c.name, ug.created_at DESC
        """, (user_id,))
        
        garments = cur.fetchall()
        print(f"Raw SQL results: {garments}")  # Debug log
        
        # Get feedback codes for mapping
        cur.execute("SELECT id, feedback_text FROM feedback_codes")
        feedback_codes = {row['id']: row['feedback_text'] for row in cur.fetchall()}
        
        def format_measurement(value):
            """Format a measurement value without trailing .00 for integers"""
            if isinstance(value, (int, float)):
                return str(int(value)) if value.is_integer() else f"{value:.2f}"
            return str(value)
        
        def get_feedback_text(feedback_code_id):
            """Get feedback text from feedback code ID"""
            if feedback_code_id and feedback_code_id in feedback_codes:
                return feedback_codes[feedback_code_id]
            return None
        
        formatted_garments = []
        for g in garments:
            measurements = {}
            
            # Build measurements dictionary for all possible dimensions
            dimension_columns = [
                ("chest", "chest_min", "chest_max"),
                ("waist", "waist_min", "waist_max"),
                ("sleeve", "sleeve_min", "sleeve_max"),
                ("neck", "neck_min", "neck_max"),
                ("hip", "hip_min", "hip_max"),
                ("length", "center_back_length", "center_back_length")
            ]
            for dim, min_col, max_col in dimension_columns:
                min_val = g.get(min_col)
                max_val = g.get(max_col)
                if min_val is not None and max_val is not None:
                    measurements[dim] = f"{format_measurement(float(min_val))}-{format_measurement(float(max_val))}"
                elif min_val is not None:
                    measurements[dim] = format_measurement(float(min_val))
                elif max_val is not None:
                    measurements[dim] = format_measurement(float(max_val))
            
            garment = {
                "id": g["garment_id"],
                "brand": g["brand_name"],
                "category": g["category"],
                "size": g["size"],
                "measurements": measurements,
                "fitFeedback": get_feedback_text(g["overall_feedback_code"]),
                "chestFit": get_feedback_text(g["chest_feedback_code"]),
                "sleeveFit": get_feedback_text(g["sleeve_feedback_code"]),
                "neckFit": get_feedback_text(g["neck_feedback_code"]),
                "waistFit": get_feedback_text(g["waist_feedback_code"]),
                "createdAt": g["created_at"].isoformat() if g["created_at"] else None,
                "ownsGarment": bool(g["owns_garment"]),
                "productName": g["product_name"],
                "imageUrl": g["image_url"],
                "productUrl": g["product_url"]
            }
            formatted_garments.append(garment)
        
        print(f"Formatted response: {formatted_garments}")  # Debug log
        return formatted_garments
        
    finally:
        cur.close()
        conn.close()

@app.get("/user/{user_id}/measurements")
async def get_user_measurements(user_id: str):
    conn = None
    try:
        print(f"🔍 API CALLED: /user/{user_id}/measurements")
        
        # Get database connection for methodology confidence
        conn = get_db()
        
        # Get garments
        garments = get_user_garments(user_id)
        print(f"Found garments for measurements: {garments}")  # Debug log
        
        # Calculate fit zones with measurement methodology awareness
        calculator = FitZoneCalculator(user_id, conn)
        fit_zone = calculator.calculate_chest_fit_zone(garments)
        print(f"Calculated fit zone: {fit_zone}")  # Debug log
        
        # Format and return response
        response = format_measurements_response(garments, fit_zone)
        print(f"Final response: {response}")  # Debug log
        return response
    except Exception as e:
        print(f"Error in get_user_measurements: {str(e)}")  # Error log
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

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

# Add these helper functions
def get_user_garments(user_id: str) -> list:
    """Get all owned garments for a user with detailed feedback as primary source"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                b.name as brand,
                c.name as garment_name,
                sge.chest_min,
                sge.chest_max,
                CASE 
                    WHEN sge.chest_min = sge.chest_max THEN sge.chest_min::text
                    ELSE sge.chest_min::text || '-' || sge.chest_max::text
                END as chest_range,
                ug.size_label as size,
                ug.owns_garment,
                -- Get detailed feedback for all dimensions
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as fit_feedback,
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as chest_feedback,
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'sleeve' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as sleeve_feedback,
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'neck' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as neck_feedback
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN categories c ON ug.category_id = c.id
            LEFT JOIN size_guide_entries_with_brand sge ON 
                ug.size_guide_entry_id = sge.id
            WHERE ug.user_id = %s
            AND ug.owns_garment = true
            AND sge.chest_min IS NOT NULL
        """, (user_id,))
        
        garments = cur.fetchall()
        print(f"Found garments with detailed feedback: {garments}")
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
    # Handle new statistical zone format
    def get_zone_range(zone_key, default_min, default_max):
        if zone_key in fit_zone and fit_zone[zone_key]['min'] is not None:
            return {
                "min": fit_zone[zone_key]['min'],
                "max": fit_zone[zone_key]['max']
            }
        else:
            return {"min": default_min, "max": default_max}
    
    return {
        "Tops": {
            "tightRange": get_zone_range('tight', 36.0, 39.0),
            "goodRange": get_zone_range('good', 39.0, 41.0),
            "relaxedRange": get_zone_range('relaxed', 41.0, 47.0),
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
            LEFT JOIN user_garment_feedback uff ON ug.id = uff.user_garment_id
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

@app.post("/chat/measurements")
async def chat_measurements(request: ChatRequest):
    try:
        # Get user context
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get available measurements for the category
                cur.execute("""
                    SELECT DISTINCT category, measurements_available
                    FROM size_guides_v2
                    WHERE category ILIKE %s
                """, ('%' + request.message.split()[0] + '%',))
                measurements = cur.fetchall()

                # Get user's measurements
                cur.execute("""
                    SELECT measurement_type, value
                    FROM user_measurements
                    WHERE user_id = %s
                """, (request.user_id,))
                user_measurements = cur.fetchall()

        # Format system context
        system_context = """You are a helpful clothing measurement assistant. 
        Your goal is to help users find the right measurements for their garments.
        Be specific about which measurements are needed and how to take them accurately."""

        if openai_client:
            try:
                print("Attempting to call OpenAI API...")
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_context},
                        {"role": "user", "content": request.message}
                    ]
                )
                return {"response": response.choices[0].message.content}
            except Exception as e:
                print(f"OpenAI API error: {str(e)}")
                # Fall through to fallback response
        else:
            print("OpenAI client not available, using fallback response")
        
        # Provide a helpful fallback response based on database info
        if measurements:
            fallback_response = f"For {measurements[0]['category']}, you will need the following measurements: {', '.join(measurements[0]['measurements_available'])}."
        else:
            fallback_response = "To get accurate measurements, please specify the type of garment (e.g., shirt, pants, jacket) and I can tell you which measurements you need."
        return {"response": fallback_response}
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        # Always return a valid response format even in error cases
        return {"response": "I apologize, but I encountered an error. Please try again."}

def format_measurement_guides(guides):
    formatted = []
    for category, measurements in guides:
        formatted.append(f"- {category}: {', '.join(measurements)}")
    return "\n".join(formatted)

def format_user_measurements(measurements):
    if not measurements:
        return "No measurements recorded yet"
    formatted = []
    for type_, value in measurements:
        formatted.append(f"- {type_}: {value}")
    return "\n".join(formatted)

def format_recent_garments(garments):
    if not garments:
        return "No previous garments recorded"
    formatted = []
    for brand, category, size, feedback in garments:
        formatted.append(f"- {brand} {category}, Size {size}" + (f" (Feedback: {feedback})" if feedback else ""))
    return "\n".join(formatted)

@app.post("/garment/process-url")
async def process_garment_url(request: dict):
    """Process a garment URL to extract brand and product information"""
    try:
        product_url = request.get("product_url")
        user_id = request.get("user_id")
        
        if not product_url:
            raise HTTPException(status_code=400, detail="Product URL is required")
        
        # Extract brand from URL
        brand_info = extract_brand_from_url(product_url)
        if not brand_info:
            raise HTTPException(status_code=400, detail="Could not identify brand from URL")
        
        # Get brand size guide information
        brand_measurements = await get_brand_measurements_for_feedback(brand_info["brand_id"])
        
        return {
            "brand": brand_info["brand_name"],
            "brand_id": brand_info["brand_id"],
            "product_url": product_url,
            "available_measurements": brand_measurements["measurements"],
            "feedback_options": brand_measurements["feedbackOptions"],
            "next_step": "size_selection"
        }
        
    except Exception as e:
        print(f"Error processing garment URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/garment/size-recommendation")
async def get_garment_size_recommendation(request: dict):
    """Process product URL and return comprehensive size recommendation across all dimensions"""
    try:
        product_url = request.get("product_url")
        user_id = request.get("user_id", "1")  # Default to user 1
        
        if not product_url:
            raise HTTPException(status_code=400, detail="Product URL is required")
        
        print(f"🔍 Getting comprehensive size recommendation for user {user_id}, URL: {product_url}")
        
        # Step 1: Extract brand from URL
        brand_info = extract_brand_from_url(product_url)
        if not brand_info:
            raise HTTPException(status_code=400, detail="Could not identify brand from URL")
        
        print(f"📊 Identified brand: {brand_info['brand_name']} (ID: {brand_info['brand_id']})")
        
        # Step 2: Use direct garment-to-garment comparison (simpler and more accurate)
        from direct_garment_comparator import DirectGarmentComparator
        
        db_config = {
            "database": "postgres",
            "user": "postgres.lbilxlkchzpducggkrxx",
            "password": "efvTower12",
            "host": "aws-0-us-east-2.pooler.supabase.com",
            "port": "6543"
        }
        
        comparator = DirectGarmentComparator(db_config)
        
        # Get direct size recommendations by comparing to user's existing garments
        recommendations = comparator.get_direct_size_recommendations(
            user_id=int(user_id),
            brand_name=brand_info['brand_name'],
            category="Tops"  # Use "Tops" to match database category name
        )
        
        if not recommendations:
            raise HTTPException(status_code=404, detail=f"No size recommendations available for {brand_info['brand_name']}")
        
        print(f"📏 Generated {len(recommendations)} direct comparison recommendations")
        
        # Convert recommendations to API response format
        api_recommendations = []
        for rec in recommendations:
            # Build reference garment details
            reference_summary = []
            dimension_details = {}
            
            for dimension, comparison in rec.dimension_comparisons.items():
                dimension_details[dimension] = {
                    "predicted_fit": comparison['predicted_fit'],
                    "target_measurement": comparison['target_measurement'],
                    "reference_measurement": comparison['reference_measurement'],
                    "reference_brand": comparison['reference_brand'],
                    "reference_size": comparison['reference_size'],
                    "range_comparison": comparison['range_comparison'],
                    "similarity_score": comparison['similarity_score']
                }
                
                # Add to summary for display  
                reference_summary.append(f"{dimension}: {comparison['target_measurement']}")
            
            # Primary concerns are dimensions with concerning fit predictions
            primary_concerns = [
                dim for dim, comp in rec.dimension_comparisons.items() 
                if comp['predicted_fit'] in ['Too Tight', 'Too Loose']
            ]
            
            api_recommendations.append({
                "size": rec.size_label,
                "overall_fit_score": round(rec.overall_fit_score, 3),
                "confidence": round(rec.confidence, 3),
                "fit_type": "excellent" if rec.overall_fit_score >= 0.9 else 
                           "good" if rec.overall_fit_score >= 0.7 else
                           "acceptable" if rec.overall_fit_score >= 0.5 else "poor",
                "available_dimensions": list(rec.dimension_comparisons.keys()),
                "dimension_analysis": dimension_details,
                "measurement_summary": ", ".join(reference_summary),
                "reasoning": rec.reasoning,
                "primary_concerns": primary_concerns,
                "fit_description": _get_direct_fit_description(
                    rec.overall_fit_score, primary_concerns, rec.reference_garments
                )
            })
        
        # Find the best recommendation
        best_rec = recommendations[0]  # Already sorted by fit score
        
        # Get reference garments info for response
        reference_garments = {}
        for ref in best_rec.reference_garments:
            ref_key = f"{ref.brand}_{ref.size_label}"
            reference_garments[ref_key] = {
                "brand": ref.brand,
                "size": ref.size_label,
                "product_name": ref.product_name,
                "measurements": {dim: measurement_range.display_string for dim, measurement_range in ref.measurements.items()},
                "feedback": ref.feedback,
                "confidence": round(ref.confidence, 2)
            }
        
        return {
            "product_url": product_url,
            "brand": brand_info["brand_name"],
            "analysis_type": "direct_comparison",
            "dimensions_analyzed": list(best_rec.dimension_comparisons.keys()),
            "reference_garments": reference_garments,
            "recommended_size": best_rec.size_label,
            "recommended_fit_score": round(best_rec.overall_fit_score, 3),
            "confidence": round(best_rec.confidence, 3),
            "reasoning": best_rec.reasoning,
            "primary_concerns": [
                dim for dim, comp in best_rec.dimension_comparisons.items() 
                if comp['predicted_fit'] in ['Too Tight', 'Too Loose']
            ],
            "comprehensive_analysis": True,
            "all_sizes": api_recommendations
        }
        
    except Exception as e:
        print(f"Error getting comprehensive size recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_direct_fit_description(fit_score: float, concerns: List[str], references: List) -> str:
    """Generate human-readable fit description for direct comparison"""
    if fit_score >= 0.9:
        if concerns:
            return f"Excellent match to your garments with minor concerns in {', '.join(concerns)}"
        else:
            return "Excellent match - very similar to your best-fitting garments"
    elif fit_score >= 0.7:
        if concerns:
            return f"Good match with some concerns in {', '.join(concerns)}"
        else:
            return "Good match - similar to garments you like"
    elif fit_score >= 0.5:
        reference_names = [f"{r.brand} {r.size_label}" for r in references[:2]]
        return f"Acceptable match (compare to your {', '.join(reference_names)})"
    else:
        return f"Poor match - significantly different from your existing garments"

@app.post("/garment/submit-with-feedback")
async def submit_garment_with_feedback(request: dict):
    """Submit a garment with size and feedback to update user's measurement profile"""
    try:
        user_id = request.get("user_id")
        brand_id = request.get("brand_id")
        size_label = request.get("size_label")
        product_url = request.get("product_url")
        feedback = request.get("feedback")  # Dict of measurement -> feedback_value
        
        if not all([user_id, brand_id, size_label, feedback]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Get brand size guide for this size
        size_measurements = await get_size_measurements(brand_id, size_label)
        
        # Create garment entry
        garment_id = await create_garment_entry(user_id, brand_id, size_label, product_url)
        
        # Store feedback for each measurement
        for measurement_name, feedback_value in feedback.items():
            if measurement_name in size_measurements:
                measurement_value = size_measurements[measurement_name]
                await store_measurement_feedback(garment_id, measurement_name, measurement_value, feedback_value)
        
        # Recalculate user's measurement profile
        await recalculate_user_measurement_profile(user_id)
        
        trigger_db_snapshot()
        
        return {
            "garment_id": garment_id,
            "status": "success",
            "message": "Garment and feedback saved successfully"
        }
        
    except Exception as e:
        print(f"Error submitting garment with feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/size-recommendation")
async def get_size_recommendation(user_id: str, brand_id: int, product_url: str):
    """Get size recommendation for a user based on their measurement profile"""
    try:
        # Get user's measurement profile
        user_profile = await get_user_measurement_profile(user_id)
        
        # Get brand size guide
        brand_sizes = await get_brand_size_guide(brand_id)
        
        # Calculate best size match
        recommendation = calculate_size_recommendation(user_profile, brand_sizes)
        
        return {
            "recommended_size": recommendation["size"],
            "confidence": recommendation["confidence"],
            "reasoning": recommendation["reasoning"],
            "alternative_sizes": recommendation["alternatives"]
        }
        
    except Exception as e:
        print(f"Error getting size recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def extract_brand_from_url(url: str) -> dict:
    """Extract brand information from a product URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Brand detection logic
        if "uniqlo.com" in domain:
            return {"brand_name": "Uniqlo", "brand_id": 1}
        elif "jcrew.com" in domain:
            return {"brand_name": "J.Crew", "brand_id": 2}
        elif "bananarepublic.com" in domain:
            return {"brand_name": "Banana Republic", "brand_id": 3}
        elif "theory.com" in domain:
            return {"brand_name": "Theory", "brand_id": 4}
        elif "patagonia.com" in domain:
            return {"brand_name": "Patagonia", "brand_id": 5}
        elif "lululemon.com" in domain:
            return {"brand_name": "Lululemon", "brand_id": 6}
        else:
            # Try to extract from database
            conn = get_db()
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT id, name FROM brands 
                    WHERE LOWER(name) IN (
                        SELECT LOWER(unnest(string_to_array(%s, '.')))
                    )
                """, (domain,))
                result = cur.fetchone()
                if result:
                    return {"brand_name": result["name"], "brand_id": result["id"]}
            finally:
                cur.close()
                conn.close()
        
        return None
    except Exception as e:
        print(f"Error extracting brand from URL: {str(e)}")
        return None

async def get_brand_measurements_for_feedback(brand_id: int) -> dict:
    """Get available measurements for feedback collection"""
    async with pool.acquire() as conn:
        size_guide = await conn.fetchrow("""
            SELECT 
                chest_min, chest_max,
                neck_min, neck_max,
                sleeve_min, sleeve_max,
                waist_min, waist_max
            FROM size_guides_v2 
            WHERE brand_id = $1 
            LIMIT 1
        """, brand_id)
        
        measurements = ['overall']  # Always include overall
        if size_guide:
            if size_guide.get('chest_min') is not None and size_guide.get('chest_max') is not None:
                measurements.append('chest')
            if size_guide.get('neck_min') is not None and size_guide.get('neck_max') is not None:
                measurements.append('neck')
            if size_guide.get('sleeve_min') is not None and size_guide.get('sleeve_max') is not None:
                measurements.append('sleeve')
            if size_guide.get('waist_min') is not None and size_guide.get('waist_max') is not None:
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

async def get_size_measurements(brand_id: int, size_label: str) -> dict:
    """Get measurements for a specific brand and size"""
    async with pool.acquire() as conn:
        measurements = await conn.fetchrow("""
            SELECT 
                chest_min, chest_max,
                neck_min, neck_max,
                sleeve_min, sleeve_max,
                waist_min, waist_max
            FROM size_guides_v2 
            WHERE brand_id = $1 AND size_label = $2
        """, brand_id, size_label)
        
        if not measurements:
            return {}
        
        result = {}
        if measurements.get('chest_min') is not None and measurements.get('chest_max') is not None:
            result['chest'] = f"{measurements['chest_min']}-{measurements['chest_max']}"
        if measurements.get('neck_min') is not None and measurements.get('neck_max') is not None:
            result['neck'] = f"{measurements['neck_min']}-{measurements['neck_max']}"
        if measurements.get('sleeve_min') is not None and measurements.get('sleeve_max') is not None:
            result['sleeve'] = f"{measurements['sleeve_min']}-{measurements['sleeve_max']}"
        if measurements.get('waist_min') is not None and measurements.get('waist_max') is not None:
            result['waist'] = f"{measurements['waist_min']}-{measurements['waist_max']}"
        
        return result

async def create_garment_entry(user_id: int, brand_id: int, size_label: str, product_url: str) -> int:
    """Create a new garment entry for the user"""
    async with pool.acquire() as conn:
        garment_id = await conn.fetchval("""
            INSERT INTO user_garments (
                user_id, 
                brand_id,
                category,
                size_label,
                product_link,
                owns_garment
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """, user_id, brand_id, 'Tops', size_label, product_url, True)
        
        return garment_id

async def store_measurement_feedback(garment_id: int, measurement_name: str, measurement_value: str, feedback_value: int):
    """Store feedback for a specific measurement"""
    async with pool.acquire() as conn:
        # Convert feedback_value to feedback text
        feedback_mapping = {
            1: "Too Tight",
            2: "Tight but I Like It", 
            3: "Good Fit",
            4: "Loose but I Like It",
            5: "Too Loose"
        }
        
        feedback_text = feedback_mapping.get(feedback_value, "Good Fit")
        
        # Get feedback code ID
        feedback_code = await conn.fetchrow("""
            SELECT id FROM feedback_codes 
            WHERE feedback_text = $1
        """, feedback_text)
        
        if feedback_code:
            await conn.execute("""
                INSERT INTO user_garment_feedback (
                    user_garment_id,
                    dimension,
                    feedback_code_id
                ) VALUES ($1, $2, $3)
            """, garment_id, measurement_name, feedback_code['id'])

async def recalculate_user_measurement_profile(user_id: int):
    """Recalculate user's measurement profile based on all feedback"""
    conn = None
    try:
        # Get database connection for methodology confidence
        conn = get_db()
        
        # This would trigger the FitZoneCalculator to recalculate
        # and update the user_fit_zones table
        calculator = FitZoneCalculator(str(user_id), conn)
        garments = get_user_garments(str(user_id))
        fit_zone = calculator.calculate_chest_fit_zone(garments)
        
        # Save updated fit zones
        save_fit_zone(str(user_id), 'Tops', fit_zone)
    finally:
        if conn:
            conn.close()

async def get_user_measurement_profile(user_id: str) -> dict:
    """Get user's current measurement profile"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
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
        
        return {
            "chest": {
                "tight": {"min": float(fit_zones['tight_min']) if fit_zones else 36.0, "max": float(fit_zones['tight_max']) if fit_zones else 39.0},
                "good": {"min": float(fit_zones['good_min']) if fit_zones else 39.0, "max": float(fit_zones['good_max']) if fit_zones else 44.0},
                "relaxed": {"min": float(fit_zones['relaxed_min']) if fit_zones else 44.0, "max": float(fit_zones['relaxed_max']) if fit_zones else 47.0}
            }
        }
    finally:
        cur.close()
        conn.close()

async def get_brand_size_guide(brand_id: int) -> list:
    """Get size guide for a brand"""
    async with pool.acquire() as conn:
        sizes = await conn.fetch("""
            SELECT 
                size_label,
                chest_min, chest_max,
                sleeve_min, sleeve_max,
                waist_min, waist_max,
                neck_min, neck_max
            FROM size_guides_v2 
            WHERE brand_id = $1
            ORDER BY size_label
        """, brand_id)
        
        return [dict(size) for size in sizes]

def calculate_size_recommendation(user_profile: dict, brand_sizes: list) -> dict:
    """Calculate the best size recommendation for a user"""
    user_chest_good = user_profile["chest"]["good"]
    
    best_match = None
    best_confidence = 0
    alternatives = []
    
    for size in brand_sizes:
        if size.get('chest_min') is not None and size.get('chest_max') is not None:
            # Calculate average chest measurement
            avg_val = (float(size['chest_min']) + float(size['chest_max'])) / 2
            
            # Calculate how well this size matches user's good range
            if user_chest_good["min"] <= avg_val <= user_chest_good["max"]:
                confidence = 0.9  # Perfect match
            elif user_chest_good["min"] - 2 <= avg_val <= user_chest_good["max"] + 2:
                confidence = 0.7  # Close match
            else:
                confidence = 0.3  # Poor match
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = size["size_label"]
            
            alternatives.append({
                "size": size["size_label"],
                "confidence": confidence,
                "measurements": {
                    "chest": f"{size['chest_min']}-{size['chest_max']}" if size.get('chest_min') and size.get('chest_max') else None,
                    "sleeve": f"{size['sleeve_min']}-{size['sleeve_max']}" if size.get('sleeve_min') and size.get('sleeve_max') else None,
                    "waist": f"{size['waist_min']}-{size['waist_max']}" if size.get('waist_min') and size.get('waist_max') else None,
                    "neck": f"{size['neck_min']}-{size['neck_max']}" if size.get('neck_min') and size.get('neck_max') else None
                }
            })
    
    # Sort alternatives by confidence
    alternatives.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "size": best_match,
        "confidence": best_confidence,
        "reasoning": f"Based on your chest measurement preference of {user_chest_good['min']}-{user_chest_good['max']} inches",
        "alternatives": alternatives[:3]  # Top 3 alternatives
    }

@app.get("/fit_feedback_options")
async def get_fit_feedback_options():
    """Provide fit feedback options for dropdown"""
    return {
        "feedbackOptions": [
            {"value": 1, "label": "Too tight"},
            {"value": 2, "label": "Tight but I like it"},
            {"value": 3, "label": "Good"},
            {"value": 4, "label": "Loose but I like it"},
            {"value": 5, "label": "Too loose"}
        ]
    }

@app.post("/garment/{garment_id}/feedback")
async def update_garment_feedback(garment_id: int, request: dict):
    """Update feedback with action tracking and undo support"""
    try:
        feedback = request.get("feedback")  # Dict of measurement -> feedback_value
        user_id = request.get("user_id")
        session_id = request.get("session_id")  # Optional session tracking
        
        if not feedback or not user_id:
            raise HTTPException(status_code=400, detail="Missing feedback or user_id")
        
        # Convert user_id to integer if it's a string
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid user_id format")
        
        async with pool.acquire() as conn:
            # Verify the garment belongs to the user
            garment = await conn.fetchrow("""
                SELECT id, brand_id, size_label FROM user_garments 
                WHERE id = $1 AND user_id = $2
            """, garment_id, user_id)
            
            if not garment:
                raise HTTPException(status_code=404, detail="Garment not found or doesn't belong to user")
            
            # Get current feedback values BEFORE changing them (for undo)
            current_feedback = await conn.fetch("""
                SELECT ugf.dimension, fc.feedback_text, ugf.id
                FROM user_garment_feedback ugf
                JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                WHERE ugf.user_garment_id = $1
            """, garment_id)
            
            # Store previous values for undo
            previous_values = {
                row['dimension']: {
                    'feedback_text': row['feedback_text'],
                    'feedback_id': row['id']
                }
                for row in current_feedback
            }
            
            # Convert numeric feedback values to text descriptions
            feedback_text = convert_feedback_to_text(feedback)
            
            # Delete old feedback entries
            await conn.execute("""
                DELETE FROM user_garment_feedback 
                WHERE user_garment_id = $1
            """, garment_id)
            
            # Insert new feedback entries and collect new values
            new_values = {}
            for dimension, feedback_text_value in feedback_text.items():
                if feedback_text_value:
                    # Get feedback code ID
                    feedback_code = await conn.fetchrow("""
                        SELECT id FROM feedback_codes 
                        WHERE feedback_text = $1
                    """, feedback_text_value)
                    
                    if feedback_code:
                        # Insert new feedback
                        new_id = await conn.fetchval("""
                            INSERT INTO user_garment_feedback (
                                user_garment_id,
                                dimension,
                                feedback_code_id
                            ) VALUES ($1, $2, $3) RETURNING id
                        """, 
                            garment_id,
                            dimension,
                            feedback_code['id']
                        )
                        
                        new_values[dimension] = {
                            'feedback_text': feedback_text_value,
                            'feedback_id': new_id
                        }
            
            # Update fit_feedback in user_garments
            await conn.execute("""
                UPDATE user_garments
                SET fit_feedback = $1
                WHERE id = $2
            """, feedback_text.get('overall'), garment_id)
            
            # Log the action for undo support
            action_id = await conn.fetchval("""
                INSERT INTO user_actions (
                    user_id, session_id, action_type, target_table, target_id,
                    previous_values, new_values, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id
            """, 
                user_id, 
                session_id, 
                'update_feedback', 
                'user_garment_feedback', 
                garment_id,
                json.dumps(previous_values),
                json.dumps(new_values),
                json.dumps({
                    'dimensions_changed': list(feedback.keys()),
                    'screen': 'garment_detail'
                })
            )
        
        trigger_db_snapshot()
        
        return {
            "status": "success",
            "message": "Feedback updated successfully",
            "action_id": action_id,
            "can_undo": True
        }
        
    except Exception as e:
        print(f"Error updating garment feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/actions/{action_id}/undo")
async def undo_action(action_id: int, request: dict):
    """Undo a specific user action"""
    try:
        user_id = request.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id")
        
        async with pool.acquire() as conn:
            # Get the action to undo
            action = await conn.fetchrow("""
                SELECT * FROM user_actions 
                WHERE id = $1 AND user_id = $2 AND is_undone = FALSE
            """, action_id, user_id)
            
            if not action:
                raise HTTPException(status_code=404, detail="Action not found or already undone")
            
            # Only support undoing feedback updates for now
            if action['action_type'] != 'update_feedback':
                raise HTTPException(status_code=400, detail="This action type cannot be undone")
            
            target_id = action['target_id']  # garment_id
            previous_values = action['previous_values']
            
            # Parse JSON if it's a string
            if isinstance(previous_values, str):
                previous_values = json.loads(previous_values)
            
            # Delete current feedback
            await conn.execute("""
                DELETE FROM user_garment_feedback 
                WHERE user_garment_id = $1
            """, target_id)
            
            # Restore previous feedback if it existed
            if previous_values:
                for dimension, data in previous_values.items():
                    feedback_code = await conn.fetchrow("""
                        SELECT id FROM feedback_codes 
                        WHERE feedback_text = $1
                    """, data['feedback_text'])
                    
                    if feedback_code:
                        await conn.execute("""
                            INSERT INTO user_garment_feedback (
                                user_garment_id, dimension, feedback_code_id
                            ) VALUES ($1, $2, $3)
                        """, target_id, dimension, feedback_code['id'])
                
                # Update user_garments.fit_feedback to match overall
                overall_feedback = previous_values.get('overall', {}).get('feedback_text')
                await conn.execute("""
                    UPDATE user_garments 
                    SET fit_feedback = $1 
                    WHERE id = $2
                """, overall_feedback, target_id)
            else:
                # No previous feedback existed, clear the field
                await conn.execute("""
                    UPDATE user_garments 
                    SET fit_feedback = NULL 
                    WHERE id = $1
                """, target_id)
            
            # Create undo action record
            undo_action_id = await conn.fetchval("""
                INSERT INTO user_actions (
                    user_id, action_type, target_table, target_id,
                    previous_values, new_values, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
            """, 
                user_id, 
                'undo_action', 
                'user_garment_feedback', 
                target_id,
                action['new_values'],
                action['previous_values'],
                json.dumps({'undoes_action_id': action_id})
            )
            
            # Mark original action as undone
            await conn.execute("""
                UPDATE user_actions 
                SET is_undone = TRUE, 
                    undone_at = CURRENT_TIMESTAMP, 
                    undone_by_action_id = $1
                WHERE id = $2
            """, undo_action_id, action_id)
        
        trigger_db_snapshot()
        
        return {
            "status": "success",
            "message": "Action undone successfully",
            "undo_action_id": undo_action_id
        }
        
    except Exception as e:
        print(f"Error undoing action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/actions/recent")
async def get_recent_actions(user_id: int, limit: int = 10):
    """Get user's recent actions that can be undone"""
    try:
        async with pool.acquire() as conn:
            actions = await conn.fetch("""
                SELECT 
                    ua.id,
                    ua.action_type,
                    ua.target_table,
                    ua.target_id,
                    ua.metadata,
                    ua.created_at,
                    ua.is_undone,
                    -- Get garment info for feedback actions
                    CASE 
                        WHEN ua.action_type = 'update_feedback' THEN
                            (SELECT ug.product_name FROM user_garments ug WHERE ug.id = ua.target_id)
                        ELSE NULL
                    END as garment_name
                FROM user_actions ua
                WHERE ua.user_id = $1 
                AND ua.action_type IN ('update_feedback', 'add_garment', 'delete_garment')
                AND ua.is_undone = FALSE
                ORDER BY ua.created_at DESC
                LIMIT $2
            """, user_id, limit)
            
            return {
                "status": "success",
                "actions": [
                    {
                        "id": action['id'],
                        "action_type": action['action_type'],
                        "target_id": action['target_id'],
                        "garment_name": action['garment_name'],
                        "created_at": action['created_at'].isoformat(),
                        "can_undo": not action['is_undone'],
                        "description": f"Updated feedback for {action['garment_name'] or 'garment'}" if action['action_type'] == 'update_feedback' else action['action_type']
                    }
                    for action in actions
                ]
            }
    
    except Exception as e:
        print(f"Error getting recent actions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def convert_feedback_to_text(feedback: dict) -> dict:
    """Convert numeric feedback values to text descriptions, with special handling for neck_fit."""
    feedback_mapping = {
        1: "Too Tight",
        2: "Tight but I Like It", 
        3: "Good Fit",
        4: "Loose but I Like It",
        5: "Too Loose"
    }
    neck_mapping = {
        1: "Too Tight",
        2: "Too Tight",
        3: "Good Fit",
        4: "Too Loose",
        5: "Too Loose"
    }
    
    result = {}
    for measurement, value in feedback.items():
        if measurement == 'neck':
            if value in neck_mapping:
                result['neck'] = neck_mapping[value]
        elif value in feedback_mapping:
            result[measurement] = feedback_mapping[value]
    
    # Calculate overall feedback based on average
    if result:
        avg_value = sum(feedback.values()) / len(feedback.values())
        if avg_value <= 1.5:
            result['overall'] = "Too Tight"
        elif avg_value <= 2.5:
            result['overall'] = "Tight but I Like It"
        elif avg_value <= 3.5:
            result['overall'] = "Good Fit"
        elif avg_value <= 4.5:
            result['overall'] = "Loose but I Like It"
        else:
            result['overall'] = "Too Loose"
    
    return result

def get_overall_feedback_description(feedback: dict) -> str:
    """Convert feedback values to a human-readable description"""
    if not feedback:
        return ""
    
    # Get the most common feedback value
    values = list(feedback.values())
    if not values:
        return ""
    
    avg_value = sum(values) / len(values)
    
    if avg_value <= 1.5:
        return "Too tight"
    elif avg_value <= 2.5:
        return "Tight but I like it"
    elif avg_value <= 3.5:
        return "Good"
    elif avg_value <= 4.5:
        return "Loose but I like it"
    else:
        return "Too loose"

@app.post("/shop/recommendations")
async def get_shop_recommendations(request: dict):
    """
    Get personalized shopping recommendations based on user's fit feedback and measurements.
    Logic:
      1. Find user's 'Good Fit' garments (from user_garments + user_fit_feedback).
      2. Generate mock recommendations based on those garments.
      3. Return a reason for each recommendation.
    """
    try:
        user_id = request.get("user_id")
        category = request.get("category")
        filters = request.get("filters", {})
        limit = request.get("limit", 20)
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        # 1. Find user's 'Good Fit' garments
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT ug.id, ug.brand_id, b.name as brand_name, ug.size_label, c.name as category, ug.product_name,
                   uff_overall.feedback_code_id as overall_feedback_code,
                   uff_chest.feedback_code_id as chest_feedback_code,
                   uff_sleeve.feedback_code_id as sleeve_feedback_code,
                   uff_neck.feedback_code_id as neck_feedback_code,
                   uff_waist.feedback_code_id as waist_feedback_code
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN categories c ON ug.category_id = c.id
            LEFT JOIN user_garment_feedback uff_overall ON 
                ug.id = uff_overall.user_garment_id AND uff_overall.dimension = 'overall'
            LEFT JOIN user_garment_feedback uff_chest ON 
                ug.id = uff_chest.user_garment_id AND uff_chest.dimension = 'chest'
            LEFT JOIN user_garment_feedback uff_sleeve ON 
                ug.id = uff_sleeve.user_garment_id AND uff_sleeve.dimension = 'sleeve'
            LEFT JOIN user_garment_feedback uff_neck ON 
                ug.id = uff_neck.user_garment_id AND uff_neck.dimension = 'neck'
            LEFT JOIN user_garment_feedback uff_waist ON 
                ug.id = uff_waist.user_garment_id AND uff_waist.dimension = 'waist'
            WHERE ug.user_id = %s AND ug.owns_garment = true
            ORDER BY ug.created_at DESC
        """, (user_id,))
        garments = cur.fetchall()

        # Get feedback codes for mapping
        cur.execute("SELECT id, feedback_text FROM feedback_codes")
        feedback_codes = {row['id']: row['feedback_text'] for row in cur.fetchall()}
        
        # Filter for 'Good Fit' garments
        good_fit_garments = []
        for g in garments:
            overall_feedback = feedback_codes.get(g.get('overall_feedback_code'), '')
            if 'good fit' in overall_feedback.lower():
                good_fit_garments.append(g)
        
        if not good_fit_garments:
            # Fallback: use any owned garment
            good_fit_garments = garments

        recommendations = []
        
        # 2. Generate mock recommendations based on user's good fit garments
        for garment in good_fit_garments[:3]:  # Use up to 3 garments for recommendations
            # Create mock recommendations based on this garment
            mock_recommendations = [
                {
                    "id": f"rec_{garment['id']}_1",
                    "name": f"Classic {garment['category'].rstrip('s')}",
                    "brand": garment['brand_name'],
                    "price": 79.99,
                    "image_url": f"https://via.placeholder.com/300x400/4A90E2/FFFFFF?text={garment['brand_name']}+{garment['category']}",
                    "product_url": f"https://example.com/product/1",
                    "category": garment['category'],
                    "fit_confidence": 0.95,
                    "recommended_size": garment['size_label'],
                    "measurements": {
                        "chest": "40-42\"",
                        "sleeve": "24-25\"",
                        "length": "28-29\""
                    },
                    "available_sizes": ["XS", "S", "M", "L", "XL"],
                    "description": f"Based on your {garment['brand_name']} {garment['size_label']} that fits well"
                },
                {
                    "id": f"rec_{garment['id']}_2",
                    "name": f"Premium {garment['category'].rstrip('s')}",
                    "brand": "Theory" if garment['brand_name'] != "Theory" else "Banana Republic",
                    "price": 129.99,
                    "image_url": f"https://via.placeholder.com/300x400/50C878/FFFFFF?text=Theory+{garment['category']}",
                    "product_url": f"https://example.com/product/2",
                    "category": garment['category'],
                    "fit_confidence": 0.88,
                    "recommended_size": garment['size_label'],
                    "measurements": {
                        "chest": "42-44\"",
                        "sleeve": "25-26\"",
                        "length": "29-30\""
                    },
                    "available_sizes": ["XS", "S", "M", "L", "XL", "XXL"],
                    "description": f"Similar style to your {garment['brand_name']} {garment['size_label']}"
                },
                {
                    "id": f"rec_{garment['id']}_3",
                    "name": f"Casual {garment['category'].rstrip('s')}",
                    "brand": "J.Crew" if garment['brand_name'] != "J.Crew" else "Patagonia",
                    "price": 59.99,
                    "image_url": f"https://via.placeholder.com/300x400/FF6B35/FFFFFF?text=J.Crew+{garment['category']}",
                    "product_url": f"https://example.com/product/3",
                    "category": garment['category'],
                    "fit_confidence": 0.92,
                    "recommended_size": garment['size_label'],
                    "measurements": {
                        "chest": "40-42\"",
                        "sleeve": "24-25\"",
                        "length": "27-28\""
                    },
                    "available_sizes": ["S", "M", "L", "XL"],
                    "description": f"Same size as your {garment['brand_name']} {garment['size_label']}"
                }
            ]
            
            # Filter by category if specified
            if category and category != "All":
                mock_recommendations = [r for r in mock_recommendations if r["category"] == category]
            
            recommendations.extend(mock_recommendations)

        cur.close()
        conn.close()
        
        # Limit results and remove duplicates
        unique_recommendations = []
        seen_ids = set()
        for rec in recommendations:
            if rec["id"] not in seen_ids and len(unique_recommendations) < limit:
                unique_recommendations.append(rec)
                seen_ids.add(rec["id"])

        return {
            "recommendations": unique_recommendations,
            "total_count": len(unique_recommendations),
            "has_more": len(unique_recommendations) >= limit
        }
        
    except Exception as e:
        print(f"Error getting shop recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database/insights")
def get_database_insights():
    """Get database insights and statistics for AI analysis (developer/admin use only)"""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from datetime import datetime
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"]
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Table counts
        table_counts = {}
        tables = [
            'users',
            'user_garments',
            'user_garment_feedback',
            'user_fit_zones',
            'user_body_measurements',
            'product_measurements',
            'brands'
        ]
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            table_counts[table] = list(cur.fetchone().values())[0]
        # User insights
        cur.execute("""
            SELECT 
                COUNT(DISTINCT user_id) as active_users,
                AVG(garment_count) as avg_garments_per_user,
                MAX(garment_count) as max_garments_per_user
            FROM (
                SELECT user_id, COUNT(*) as garment_count 
                FROM user_garments 
                GROUP BY user_id
            ) user_stats
        """)
        user_stats = cur.fetchone()
        # Popular brands
        cur.execute("""
            SELECT brand_id, COUNT(*) as count 
            FROM user_garments 
            GROUP BY brand_id 
            ORDER BY count DESC 
            LIMIT 10
        """)
        popular_brands = cur.fetchall()
        # Fit feedback distribution
        cur.execute("""
            SELECT fc.feedback_text, COUNT(*) as count 
            FROM user_garment_feedback ugf
            JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
            WHERE ugf.dimension = 'overall'
            GROUP BY fc.feedback_text 
            ORDER BY count DESC
        """)
        fit_distribution = cur.fetchall()
        # Measurement ranges (chest)
        cur.execute("""
            SELECT 
                MIN(calculated_min) as min_chest,
                MAX(calculated_max) as max_chest,
                AVG((calculated_min + calculated_max)/2) as avg_chest
            FROM user_body_measurements 
            WHERE measurement_type = 'chest'
        """)
        chest_stats = cur.fetchone()
        insights = {
            "timestamp": datetime.now().isoformat(),
            "table_counts": table_counts,
            "user_insights": {
                "active_users": user_stats["active_users"] if user_stats else 0,
                "avg_garments_per_user": float(user_stats["avg_garments_per_user"]) if user_stats and user_stats["avg_garments_per_user"] else 0,
                "max_garments_per_user": user_stats["max_garments_per_user"] if user_stats else 0
            },
            "popular_brands": popular_brands,
            "fit_feedback_distribution": fit_distribution,
            "measurement_insights": {
                "chest_range": {
                    "min": float(chest_stats["min_chest"]) if chest_stats and chest_stats["min_chest"] else 0,
                    "max": float(chest_stats["max_chest"]) if chest_stats and chest_stats["max_chest"] else 0,
                    "average": float(chest_stats["avg_chest"]) if chest_stats and chest_stats["avg_chest"] else 0
                }
            },
            "recommendations": {
                "data_quality": [],
                "performance": [],
                "features": []
            }
        }
        # Generate AI recommendations based on data
        if table_counts['user_garments'] < 100:
            insights["recommendations"]["data_quality"].append("Consider adding more sample garments for better fit zone calculations")
        if table_counts['brands'] < 10:
            insights["recommendations"]["features"].append("Expand brand catalog for better recommendations")
        if table_counts['user_garment_feedback'] < 50:
            insights["recommendations"]["data_quality"].append("More fit feedback needed for accurate fit zone calculations")
        cur.close()
        conn.close()
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database analysis failed: {str(e)}")

def trigger_schema_evolution():
    """Trigger schema evolution tracking"""
    if os.environ.get("ENV", "development") == "development":
        subprocess.Popen([sys.executable, "scripts/schema_evolution.py"])

def trigger_db_snapshot():
    # Run the snapshot script in the background, only in development
    if os.environ.get("ENV", "development") == "development":
        subprocess.Popen([sys.executable, "scripts/db_snapshot.py"])
        # Also trigger schema evolution
        trigger_schema_evolution()

@app.get("/user/{user_id}/body-measurements")
async def get_user_body_measurements(user_id: str):
    try:
        # Initialize estimator with database config
        estimator = BodyMeasurementEstimator(DB_CONFIG)
        # Estimate chest, neck, and arm length measurements (now returns detailed data)
        chest_data = estimator.estimate_chest_measurement(int(user_id))
        neck_data = estimator.estimate_neck_measurement(int(user_id))
        arm_length_data = estimator.estimate_sleeve_measurement(int(user_id))
        
        # Extract estimates from detailed data
        chest_estimate = chest_data['estimate'] if chest_data else None
        neck_estimate = neck_data['estimate'] if neck_data else None
        arm_length_estimate = arm_length_data['estimate'] if arm_length_data else None
        
        # If all are None, return message
        if chest_estimate is None and neck_estimate is None and arm_length_estimate is None:
            return {
                "estimated_chest": None,
                "estimated_neck": None,
                "estimated_arm_length": None,
                "unit": "in",
                "message": "No sufficient data to estimate body measurements"
            }
        return {
            "estimated_chest": round(chest_estimate, 2) if chest_estimate is not None else None,
            "estimated_neck": round(neck_estimate, 2) if neck_estimate is not None else None,
            "estimated_arm_length": round(arm_length_estimate, 2) if arm_length_estimate is not None else None,
            "unit": "in",
            "chest_details": chest_data['garment_details'] if chest_data else [],
            "neck_details": neck_data['garment_details'] if neck_data else [],
            "arm_length_details": arm_length_data['garment_details'] if arm_length_data else []
        }
    except Exception as e:
        print(f"Error in get_user_body_measurements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/canvas/user/{user_id}")
async def get_canvas_data(user_id: str):
    """Get comprehensive canvas data for debugging and understanding the measurement prediction system"""
    try:
        from canvas_endpoint import CanvasDataGenerator
        
        canvas_generator = CanvasDataGenerator(DB_CONFIG)
        canvas_data = canvas_generator.generate_canvas_data(int(user_id))
        
        return canvas_data
        
    except Exception as e:
        print(f"Error in get_canvas_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",  # Use string format
        host="0.0.0.0",
        port=8006,  # Backend API port
        reload=True
    ) 