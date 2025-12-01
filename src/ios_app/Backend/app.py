# New FastAPI application using tailor2 schema
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import asyncpg
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fit_zone_calculator import FitZoneCalculator
import json
import time
from urllib.parse import urlparse
import openai
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from db_config import DB_CONFIG
from sqlalchemy import text

# Simple in-memory cache for user fit zones data
user_fit_zones_cache = {}
CACHE_EXPIRY_MINUTES = 5
import subprocess
import sys
from body_measurement_estimator import BodyMeasurementEstimator
import requests
import re
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key (optional for development)
api_key = os.getenv("OPENAI_API_KEY")
openai_client = None

if api_key and api_key not in ["your-api-key-here", "your-new-api-key-here"]:
    # Initialize OpenAI client only if valid key is provided
    openai_client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.openai.com/v1",  # Explicitly set the base URL
        max_retries=3,  # Add retries
        timeout=30.0  # Increase timeout
    )
else:
    print("Warning: OpenAI API key not set. Chat features will be disabled.")

# Database configuration is centralized in scripts/database/db_config.py

# Global connection pool
pool = None

def get_db_connection():
    """Get a connection to the database"""
    return psycopg2.connect(**DB_CONFIG)



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup - initialize database connection pool
    global pool
    # Disable prepared statements to work with pgbouncer
    pool = await asyncpg.create_pool(**DB_CONFIG, statement_cache_size=0)
    print("✅ Starting FastAPI application")
    yield
    # Cleanup
    if pool:
        await pool.close()
    print("✅ Shutting down FastAPI application")

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
def get_db():
    """Get a database connection"""
    return psycopg2.connect(
        dbname=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        cursor_factory=RealDictCursor
    )

@app.get("/user/{user_id}/closet")
async def get_closet(user_id: int):
    conn = get_db()
    # Ensure dictionary rows for downstream .get() usage
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Try to use materialized view first for better performance.
        # If it doesn't exist, we'll fall back to the base table.
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
                sge.center_back_length,
                ug.fit_feedback,
                ug.created_at,
                ug.owns_garment,
                g.product_name,
                g.image_url,
                g.product_url,
                -- Use materialized view if available, otherwise fall back to subqueries
                COALESCE(ufc.overall_feedback, 
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall'
                     ORDER BY ugf.created_at DESC LIMIT 1)) as overall_feedback,
                COALESCE(ufc.chest_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest'
                     ORDER BY ugf.created_at DESC LIMIT 1)) as chest_feedback,
                COALESCE(ufc.sleeve_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'sleeve'
                     ORDER BY ugf.created_at DESC LIMIT 1)) as sleeve_feedback,
                COALESCE(ufc.neck_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'neck'
                     ORDER BY ugf.created_at DESC LIMIT 1)) as neck_feedback,
                COALESCE(ufc.waist_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'waist'
                     ORDER BY ugf.created_at DESC LIMIT 1)) as waist_feedback,
                COALESCE(ufc.hip_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'hip'
                     ORDER BY ugf.created_at DESC LIMIT 1)) as hip_feedback
            FROM user_garments ug
            LEFT JOIN garments g ON ug.garment_id = g.id
            LEFT JOIN brands b ON g.brand_id = b.id
            LEFT JOIN categories c ON g.category_id = c.id
            LEFT JOIN size_guide_entries_with_brand sge ON 
                ug.size_guide_entry_id = sge.id
            LEFT JOIN user_feedback_current ufc ON ufc.user_garment_id = ug.id
            WHERE ug.user_id = %s 
            AND ug.owns_garment = true
            ORDER BY c.name, ug.created_at DESC
        """, (user_id,))
    except Exception:
        # Fallback: use base table if the materialized view is unavailable
        conn.rollback()
        cur.close()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
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
                sge.center_back_length,
                ug.fit_feedback,
                ug.created_at,
                ug.owns_garment,
                g.product_name,
                g.image_url,
                g.product_url,
                -- Feedback fallbacks from historical table
                (SELECT fc.feedback_text FROM user_garment_feedback ugf
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall'
                 ORDER BY ugf.created_at DESC LIMIT 1) as overall_feedback,
                (SELECT fc.feedback_text FROM user_garment_feedback ugf
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest'
                 ORDER BY ugf.created_at DESC LIMIT 1) as chest_feedback,
                (SELECT fc.feedback_text FROM user_garment_feedback ugf
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'sleeve'
                 ORDER BY ugf.created_at DESC LIMIT 1) as sleeve_feedback,
                (SELECT fc.feedback_text FROM user_garment_feedback ugf
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'neck'
                 ORDER BY ugf.created_at DESC LIMIT 1) as neck_feedback,
                (SELECT fc.feedback_text FROM user_garment_feedback ugf
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'waist'
                 ORDER BY ugf.created_at DESC LIMIT 1) as waist_feedback,
                (SELECT fc.feedback_text FROM user_garment_feedback ugf
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'hip'
                 ORDER BY ugf.created_at DESC LIMIT 1) as hip_feedback
            FROM user_garments ug
            LEFT JOIN garments g ON ug.garment_id = g.id
            LEFT JOIN brands b ON g.brand_id = b.id
            LEFT JOIN categories c ON g.category_id = c.id
            LEFT JOIN size_guide_entries sge ON 
                ug.size_guide_entry_id = sge.id
            WHERE ug.user_id = %s 
            AND ug.owns_garment = true
            ORDER BY c.name, ug.created_at DESC
        """, (user_id,))

    try:
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
                "category": g["category"] or "Unknown",
                "size": g["size"],
                "measurements": measurements,
                "fitFeedback": g["overall_feedback"],
                "chestFit": g["chest_feedback"],
                "sleeveFit": g["sleeve_feedback"],
                "neckFit": g["neck_feedback"],
                "waistFit": g["waist_feedback"],
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
        
        # Check cache first
        cache_key = f"fit_zones_{user_id}"
        current_time = datetime.now()
        
        if cache_key in user_fit_zones_cache:
            cached_data, cache_time = user_fit_zones_cache[cache_key]
            if current_time - cache_time < timedelta(minutes=CACHE_EXPIRY_MINUTES):
                print(f"📦 CACHE HIT: Returning cached fit zones for user {user_id}")
                return cached_data
        
        print(f"📦 CACHE MISS: Loading fresh fit zones for user {user_id}")
        
        # Get database connection for methodology confidence
        conn = get_db()
        
        # Get garments with ALL dimensions
        garments = get_user_garments_with_all_dimensions(user_id)
        print(f"Found garments for measurements: {garments}")  # Debug log
        
        # Use ESTABLISHED fit zones from fitzonetracker.md instead of recalculating
        established_fit_zones = get_established_fit_zones()
        print(f"Using established fit zones: {established_fit_zones}")  # Debug log
        
        # Format and return comprehensive response
        response = format_comprehensive_measurements_response(garments, established_fit_zones['chest'], established_fit_zones['neck'], established_fit_zones['sleeve'])
        print(f"Final response: {response}")  # Debug log
        
        # Cache the response
        user_fit_zones_cache[cache_key] = (response, current_time)
        print(f"📦 CACHED: Stored fit zones for user {user_id}")
        
        return response
    except Exception as e:
        print(f"Error in get_user_measurements: {str(e)}")  # Error log
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

def get_established_fit_zones():
    """Get the established fit zones from database (FAANG-style caching)"""
    try:
        return get_fit_zones_from_database(user_id=1, category_id=1)
    except Exception as e:
        print(f"Error loading fit zones from database: {e}")
        # Fallback to hardcoded values if database fails
        return get_fallback_fit_zones()

def invalidate_user_fit_zones(user_id: int):
    """Mark user's fit zones as needing recalculation (called when new feedback is submitted)"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Mark existing fit zones as invalidated (but don't delete - for audit trail)
        cursor.execute('''
            UPDATE fit_zones 
            SET updated_at = CURRENT_TIMESTAMP,
                notes = CONCAT(COALESCE(notes, ''), ' - Invalidated due to new feedback at ', CURRENT_TIMESTAMP)
            WHERE user_id = %s
        ''', (user_id,))
        
        conn.commit()
        print(f"🔄 Invalidated fit zones for user {user_id} - will recalculate on next request")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error invalidating fit zones: {e}")
    finally:
        cursor.close()
        conn.close()

def get_fit_zones_from_database(user_id: int, category_id: int):
    """Load fit zones from database with proper structure"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute('''
            SELECT dimension, fit_type, min_value, max_value, unit, notes, created_at
            FROM fit_zones 
            WHERE user_id = %s AND category_id = %s
            ORDER BY dimension, fit_type
        ''', (user_id, category_id))
        
        zones_data = cursor.fetchall()
        print(f"📊 Loaded {len(zones_data)} fit zones from database")
        
        # Structure the data properly
        structured_zones = {}
        
        for zone in zones_data:
            dimension = zone['dimension']
            fit_type = zone['fit_type']
            
            if dimension not in structured_zones:
                structured_zones[dimension] = {}
            
            # Database now uses 'good' directly - no mapping needed
            structured_zones[dimension][fit_type] = {
                'min': float(zone['min_value']),
                'max': float(zone['max_value'])
            }
        
        # Add metadata for each dimension
        for dimension in structured_zones:
            structured_zones[dimension]['confidence'] = 0.95
            structured_zones[dimension]['data_points'] = 8 if dimension == 'chest' else 4
        
        print(f"✅ Structured fit zones: {structured_zones}")
        return structured_zones
        
    finally:
        cursor.close()
        conn.close()

def get_fallback_fit_zones():
    """Fallback fit zones if database is unavailable"""
    print("⚠️ Using fallback fit zones")
    return {
        'chest': {
            'tight': {'min': 36.0, 'max': 39.5},
            'good': {'min': 39.5, 'max': 42.5},
            'relaxed': {'min': 43.0, 'max': 45.5},
            'confidence': 0.95,
            'data_points': 8
        },
        'neck': {
            'good': {'min': 16.0, 'max': 16.5},
            'confidence': 1.0,
            'data_points': 4
        },
        'sleeve': {
            'good': {'min': 33.5, 'max': 36.0},
            'confidence': 1.0,
            'data_points': 8
        }
    }

def get_user_garments_with_all_dimensions(user_id: str) -> list:
    """Get all owned garments for a user with ALL dimensions (chest, neck, sleeve)"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                b.name as brand,
                c.name as garment_name,
                sge.chest_min, sge.chest_max,
                sge.neck_min, sge.neck_max,
                sge.sleeve_min, sge.sleeve_max,
                CASE 
                    WHEN sge.chest_min = sge.chest_max THEN sge.chest_min::text
                    ELSE sge.chest_min::text || '-' || sge.chest_max::text
                END as chest_range,
                CASE 
                    WHEN sge.neck_min = sge.neck_max THEN sge.neck_min::text
                    ELSE sge.neck_min::text || '-' || sge.neck_max::text
                END as neck_range,
                CASE 
                    WHEN sge.sleeve_min = sge.sleeve_max THEN sge.sleeve_min::text
                    ELSE sge.sleeve_min::text || '-' || sge.sleeve_max::text
                END as sleeve_range,
                ug.size_label as size,
                ug.owns_garment,
                -- Optimized feedback retrieval using window functions instead of subqueries
                MAX(CASE WHEN ugf.dimension = 'overall' THEN fc.feedback_text END) as fit_feedback,
                MAX(CASE WHEN ugf.dimension = 'chest' THEN fc.feedback_text END) as chest_feedback,
                MAX(CASE WHEN ugf.dimension = 'neck' THEN fc.feedback_text END) as neck_feedback,
                MAX(CASE WHEN ugf.dimension = 'sleeve' THEN fc.feedback_text END) as sleeve_feedback
            FROM user_garments ug
            LEFT JOIN garments g ON ug.garment_id = g.id
            LEFT JOIN brands b ON g.brand_id = b.id
            LEFT JOIN categories c ON g.category_id = c.id
            LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
            LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
            LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
            WHERE ug.user_id = %s AND ug.owns_garment = true
            GROUP BY ug.id, b.name, c.name, sge.chest_min, sge.chest_max, sge.neck_min, sge.neck_max, 
                     sge.sleeve_min, sge.sleeve_max, ug.size_label, ug.owns_garment, ug.created_at
            ORDER BY ug.created_at DESC
        """, (user_id,))
        
        results = cur.fetchall()
        print(f"DEBUG: Raw database results: {results}")
        
        # Convert RealDictRow objects to regular dictionaries
        garments = []
        for row in results:
            garment_dict = dict(row)
            print(f"DEBUG: Garment dict: {garment_dict}")
            garments.append(garment_dict)
        
        return garments
        
    finally:
        cur.close()
        conn.close()

def format_comprehensive_measurements_response(garments, chest_fit_zone, neck_fit_zone, sleeve_fit_zone):
    """Format comprehensive response with all dimensions"""
    def get_zone_range(zone_data, default_min, default_max):
        if zone_data and 'min' in zone_data and zone_data['min'] is not None:
            return {
                "min": zone_data['min'],
                "max": zone_data['max']
            }
        else:
            return {"min": default_min, "max": default_max}
    
    def safe_parse_range(range_str):
        """Safely parse a range string, returning None if invalid"""
        if not range_str or not isinstance(range_str, str):
            return None
        try:
            if '-' in range_str:
                parts = range_str.split('-')
                return float(parts[0].strip())
            else:
                return float(range_str.strip())
        except (ValueError, IndexError):
            return None
    
    print(f"DEBUG: Formatting response with {len(garments)} garments")
    print(f"DEBUG: First garment: {garments[0] if garments else 'No garments'}")
    
    return {
        "Tops": {
            "chest": {
                "tightRange": get_zone_range(chest_fit_zone.get('tight') if chest_fit_zone else None, 36.0, 39.0),
                "goodRange": get_zone_range(chest_fit_zone.get('good') if chest_fit_zone else None, 39.5, 42.0),
                "relaxedRange": get_zone_range(chest_fit_zone.get('relaxed') if chest_fit_zone else None, 46.0, 48.5),
                "garments": [
                    {
                        "brand": g.get("brand", "Unknown"),
                        "garmentName": g.get("garment_name", "Unknown"),
                        "range": g.get("chest_range", ""),
                        "value": safe_parse_range(g.get("chest_range")),
                        "size": g.get("size", "Unknown"),
                        "fitFeedback": g.get("fit_feedback", "") or "",
                        "feedback": g.get("chest_feedback", "") or "",
                        "ownsGarment": g.get("owns_garment", True)
                    } for g in garments if g.get("chest_range")
                ]
            },
            "neck": {
                "goodRange": get_zone_range(neck_fit_zone.get('good') if neck_fit_zone else None, 16.0, 16.5),
                "garments": [
                    {
                        "brand": g.get("brand", "Unknown"),
                        "garmentName": g.get("garment_name", "Unknown"),
                        "range": g.get("neck_range", ""),
                        "value": safe_parse_range(g.get("neck_range")),
                        "size": g.get("size", "Unknown"),
                        "fitFeedback": g.get("fit_feedback", "") or "",
                        "feedback": g.get("neck_feedback", "") or "",
                        "ownsGarment": g.get("owns_garment", True)
                    } for g in garments if g.get("neck_range")
                ]
            },
            "sleeve": {
                "goodRange": get_zone_range(sleeve_fit_zone.get('good') if sleeve_fit_zone else None, 33.5, 36.0),
                "garments": [
                    {
                        "brand": g.get("brand", "Unknown"),
                        "garmentName": g.get("garment_name", "Unknown"),
                        "range": g.get("sleeve_range", ""),
                        "value": safe_parse_range(g.get("sleeve_range")),
                        "size": g.get("size", "Unknown"),
                        "fitFeedback": g.get("fit_feedback", "") or "",
                        "feedback": g.get("sleeve_feedback", "") or "",
                        "ownsGarment": g.get("owns_garment", True)
                    } for g in garments if g.get("sleeve_range")
                ]
            }
        }
    }

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
            LEFT JOIN garments g ON ug.garment_id = g.id
            LEFT JOIN brands b ON g.brand_id = b.id
            LEFT JOIN categories c ON g.category_id = c.id
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
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get scan actions from user_actions table with enhanced metadata and deduplication
        cur.execute("""
            WITH ranked_scans AS (
                SELECT 
                    ua.id,
                    ua.metadata,
                    ua.created_at,
                    -- Use brand_name from metadata if available, otherwise extract from URL
                    COALESCE(ua.metadata->>'brand_name', 
                        CASE 
                            WHEN ua.metadata->>'product_url' LIKE '%%jcrew%%' THEN 'J.Crew'
                            WHEN ua.metadata->>'product_url' LIKE '%%uniqlo%%' THEN 'Uniqlo'
                            WHEN ua.metadata->>'product_url' LIKE '%%banana%%' THEN 'Banana Republic'
                            WHEN ua.metadata->>'product_url' LIKE '%%theory%%' THEN 'Theory'
                            WHEN ua.metadata->>'product_url' LIKE '%%patagonia%%' THEN 'Patagonia'
                            WHEN ua.metadata->>'product_url' LIKE '%%lululemon%%' THEN 'Lululemon'
                            ELSE 'Unknown Brand'
                        END
                    ) as brand,
                    -- Use real product name from metadata, fallback to extracted name
                    COALESCE(ua.metadata->>'product_name', 'Product Name Not Found') as name,
                    -- Create a unique key for deduplication: normalized_product_url + recommended_size
                    -- Extract product ID from URL for better deduplication (e.g., pid=704275052)
                    CONCAT(
                        CASE 
                            WHEN ua.metadata->>'product_url' ~ 'pid=([0-9]+)' THEN 
                                CONCAT('pid=', (regexp_match(ua.metadata->>'product_url', 'pid=([0-9]+)'))[1])
                            ELSE ua.metadata->>'product_url'
                        END,
                        '|', 
                        COALESCE(ua.metadata->>'recommended_size', 'unknown')
                    ) as unique_key,
                    -- Rank by creation time (most recent first)
                    ROW_NUMBER() OVER (
                        PARTITION BY CONCAT(
                            CASE 
                                WHEN ua.metadata->>'product_url' ~ 'pid=([0-9]+)' THEN 
                                    CONCAT('pid=', (regexp_match(ua.metadata->>'product_url', 'pid=([0-9]+)'))[1])
                                ELSE ua.metadata->>'product_url'
                            END,
                            '|', 
                            COALESCE(ua.metadata->>'recommended_size', 'unknown')
                        )
                        ORDER BY ua.created_at DESC
                    ) as rn
                FROM user_actions ua
                WHERE ua.user_id = %s 
                AND ua.action_type = 'scan_item'
                AND ua.metadata->>'product_url' IS NOT NULL
            )
                    SELECT
            id,
            metadata,
            created_at,
            brand,
            name,
            COALESCE(metadata->>'product_image', '') as image_url
        FROM ranked_scans
        WHERE rn = 1  -- Only the most recent scan for each unique product+size combination
        ORDER BY created_at DESC
        LIMIT 50
        """, (user_id,))
        
        scan_actions = cur.fetchall()
        
        # Convert to scan history format
        history_items = []
        for action in scan_actions:
            metadata = action['metadata'] if isinstance(action['metadata'], dict) else {}
            
            # Get recommended size from metadata
            recommended_size = metadata.get('recommended_size')
            confidence_tier = metadata.get('confidence_tier')
            
            # Use clean product name without redundant recommendation text
            display_name = action['name']
            
            history_items.append({
                "id": action['id'],
                "productCode": "SCAN_" + str(action['id']),
                "scannedSize": recommended_size,  # Now includes recommended size
                "scannedPrice": None,  # We don't track price in scan actions yet
                "scannedAt": action['created_at'].isoformat() + "Z",
                "name": display_name,
                "category": "Tops",
                "imageUrl": action.get('image_url') or get_brand_placeholder_image(action['brand']),
                "productUrl": metadata.get('product_url', ''),
                "brand": action['brand']
            })
        
        # Add mock data if no real scans exist
        if not history_items:
            history_items = [
                {
                    "id": 1,
                    "productCode": "475352",
                    "scannedSize": "L",
                    "scannedPrice": 29.90,
                    "scannedAt": "2024-02-24T10:30:00Z",
                    "name": "Waffle Crew Neck T-Shirt",
                    "category": "Tops",
                    "imageUrl": "https://example.com/image.jpg",
                    "productUrl": "https://uniqlo.com/product/475352",
                    "brand": "Uniqlo"
                }
            ]
        
        return history_items
            
    except Exception as e:
        print(f"Error getting scan history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

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
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # First verify the brand exists
        cur.execute("SELECT name FROM brands WHERE id = %s", (brand_id,))
        brand = cur.fetchone()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")

        # Get all available measurements for this brand
        cur.execute("""
            SELECT 
                chest_range,
                neck_range,
                sleeve_range,
                waist_range
            FROM size_guides 
            WHERE brand_id = %s 
            LIMIT 1
        """, (brand_id,))
        size_guide = cur.fetchone()

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
    finally:
        cur.close()
        conn.close()

@app.post("/garments/submit")
async def submit_garment_and_feedback(submission: GarmentSubmission):
    """Submit a new garment with feedback"""
    try:
        print(f"Received submission: {submission}")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # First check if this garment already exists
        cur.execute("""
            SELECT id FROM user_garments 
            WHERE user_id = %s 
            AND brand_id = (
                SELECT id FROM brands 
                WHERE name = 'Banana Republic'
            )
            AND category = 'Tops'
            AND size_label = %s
            AND created_at > NOW() - INTERVAL '1 hour'
        """, (submission.userId, submission.sizeLabel))
        
        existing_garment = cur.fetchone()
        if existing_garment:
            return {
                "garment_id": existing_garment['id'],
                "status": "existing"
            }
        
        # Get brand_id for Banana Republic
        cur.execute("SELECT id FROM brands WHERE name = 'Banana Republic'")
        brand_result = cur.fetchone()
        brand_id = brand_result['id'] if brand_result else None
        
        # If no recent duplicate, proceed with insert
        cur.execute("""
            INSERT INTO user_garments (
                user_id, 
                brand_id,
                category,
                size_label,
                chest_range,
                product_link,
                owns_garment
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            submission.userId,
            brand_id,
            'Tops',
            submission.sizeLabel,
            'N/A',
            submission.productLink,
            True
        ))
        
        garment_result = cur.fetchone()
        garment_id = garment_result['id']
        conn.commit()
        
        return {
            "garment_id": garment_id,
            "status": "success"
        }
            
    except Exception as e:
        print(f"Error submitting garment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

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

@app.post("/tryon/start")
async def start_tryon_session(request: dict):
    """
    Start a try-on session - extract product info and prepare for feedback collection
    This is separate from size recommendations - focused on collecting user feedback
    """
    try:
        product_url = request.get("product_url")
        user_id = request.get("user_id", "1")
        
        if not product_url:
            raise HTTPException(status_code=400, detail="Product URL is required")
        
        print(f"🎯 Starting try-on session for: {product_url}")
        
        # Extract brand from URL
        brand_info = extract_brand_from_url(product_url)
        if not brand_info:
            raise HTTPException(status_code=400, detail="Could not identify brand from URL")
        
        # Initialize variables
        product_data = None
        fit_variations = {}
        
        # For J.Crew, use the dynamic fetcher that returns fit variations
        if brand_info["brand_name"] == "J.Crew" and "jcrew.com" in product_url.lower():
            # Import here to avoid circular imports
            # Using dynamic fetcher to get fit-specific variations
            from jcrew_dynamic_fetcher import JCrewDynamicFetcher
            
            fetcher = JCrewDynamicFetcher()
            product_data = fetcher.fetch_product(product_url)
            
            if product_data:
                # Use base product name (without fit prefix) like J.Crew app
                product_name = product_data.get('base_product_name', product_data.get('product_name', ''))
                product_image = product_data.get('product_image', '')
                size_options = product_data.get('sizes_available', ['XS', 'S', 'M', 'L', 'XL', 'XXL'])
                fit_options = product_data.get('fit_options', [])
                
                # Get fit variations for dynamic UI updates
                fit_variations = product_data.get('fit_variations', {})
                
                print(f"✅ J.Crew product fetched: {product_name}")
                if fit_options:
                    print(f"🎯 Available fit options: {fit_options}")
                    if fit_variations:
                        print(f"📊 Fit variations available for dynamic updates")
                else:
                    print(f"📝 No fit options (single-fit product)")
            else:
                # Product not in cache
                raise HTTPException(status_code=404, 
                    detail="This J.Crew product is not available in our database. Please try a different product or contact support to add this item.")
        else:
            # Use existing logic for other brands
            product_name = extract_product_name_from_url(product_url)
            product_image = extract_product_image_from_url(product_url)
            size_options = await get_brand_size_options(brand_info["brand_id"])
            fit_options = []  # Other brands don't have fit options yet
            fit_variations = {}  # No fit variations for non-J.Crew brands
        
        # Get available measurements for this brand
        brand_measurements = await get_brand_measurements_for_feedback(brand_info["brand_id"])
        
        # Get available colors for this product
        available_colors = []
        if brand_info["brand_name"] == "J.Crew" and "jcrew.com" in product_url.lower():
            if product_data and 'colors_available' in product_data:
                available_colors = product_data['colors_available']
        
        # Extract current color from URL if specified
        current_color = ""
        if 'color_name=' in product_url:
            import urllib.parse
            parsed = urllib.parse.urlparse(product_url)
            params = urllib.parse.parse_qs(parsed.query)
            if 'color_name' in params:
                current_color = params['color_name'][0].replace('+', ' ').replace('%20', ' ').title()
        
        # Build response
        response = {
            "session_id": f"tryon_{user_id}_{int(time.time())}",
            "brand": brand_info["brand_name"],
            "brand_id": brand_info["brand_id"],
            "product_name": product_name,
            "product_url": product_url,
            "product_image": product_image,
            "available_measurements": brand_measurements["measurements"],
            "feedback_options": brand_measurements["feedbackOptions"],
            "size_options": size_options,
            "fit_options": fit_options,
            "color_options": available_colors,
            "current_color": current_color,
            "next_step": "size_selection_and_feedback"
        }
        
        # Add fit variations for J.Crew to enable dynamic UI updates
        if brand_info["brand_name"] == "J.Crew" and fit_variations:
            response["fit_variations"] = fit_variations
            response["current_fit"] = 'Classic'  # Always default to Classic like J.Crew app
            response["base_product_name"] = product_data.get('base_product_name', product_name)
        
        return response
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        print(f"Error starting try-on session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tryon/submit")
async def submit_tryon_feedback(request: dict):
    """
    Submit try-on feedback - this is where the user provides their fit experience
    """
    try:
        user_id = request.get("user_id", "1")
        session_id = request.get("session_id")
        product_url = request.get("product_url")
        brand_id = request.get("brand_id")
        size_tried = request.get("size_tried")
        feedback = request.get("feedback")  # {chest: 3, neck: 2, sleeve: 4, overall: 3}
        fit_type = request.get("fit_type")  # For J.Crew: Classic, Slim, Tall, etc.
        selected_color = request.get("selected_color")  # Color user tried on
        notes = request.get("notes", "")
        try_on_location = request.get("try_on_location", "Store")
        
        if not all([session_id, product_url, brand_id, size_tried, feedback]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Map fit_type to database-allowed values
        fit_type_mapping = {
            "Classic": "Regular",
            "Regular": "Regular", 
            "Slim": "Slim",
            "Tall": "Tall",
            "Unknown": "Unknown"
        }
        db_fit_type = fit_type_mapping.get(fit_type, "Unknown") if fit_type else "Unknown"
        
        fit_info = f" ({fit_type})" if fit_type else ""
        print(f"📝 Submitting try-on feedback: {size_tried}{fit_info} - {feedback}")
        
        # Extract product name
        product_name = extract_product_name_from_url(product_url)
        
        async with pool.acquire() as conn:
            # Extract product image
            product_image = ""
            if 'jcrew.com' in product_url.lower():
                # For J.Crew, fetch the product image
                from jcrew_fetcher import JCrewProductFetcher
                fetcher = JCrewProductFetcher()
                product_data = fetcher.fetch_product(product_url)
                if product_data:
                    product_image = product_data.get('product_image', '')
                    print(f"📸 Retrieved J.Crew product image: {product_image}")
            else:
                # For other brands, try to extract from URL
                product_image = extract_product_image_from_url(product_url)
            
            # First, create or find the garments entry
            garment_entry_id = await conn.fetchval("""
                INSERT INTO garments (
                    brand_id, category_id, product_name, product_url, image_url, fit_type,
                    created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
                ON CONFLICT (brand_id, product_name, category_id, subcategory_id) 
                DO UPDATE SET 
                    updated_at = NOW(), 
                    fit_type = COALESCE($6, garments.fit_type),
                    image_url = COALESCE($5, garments.image_url),
                    product_url = COALESCE($4, garments.product_url)
                RETURNING id
            """, brand_id, 1, product_name, product_url, product_image, db_fit_type)
            
            # Create try-on garment entry (NOT owned) - using correct schema
            garment_id = await conn.fetchval("""
                INSERT INTO user_garments (
                    user_id, garment_id, size_label, owns_garment,
                    input_method, link_provided, color, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                RETURNING id
            """, int(user_id), garment_entry_id, size_tried, False, 
                'link', product_url, selected_color)
            
            # Get size measurements for this brand/size
            measurements = await conn.fetchrow("""
                SELECT sge.* FROM size_guide_entries sge
                JOIN size_guides sg ON sge.size_guide_id = sg.id
                WHERE sg.brand_id = $1 AND sge.size_label = $2
                LIMIT 1
            """, brand_id, size_tried)
            
            # Store feedback for each dimension
            feedback_stored = []
            overall_feedback = None
            
            for dimension, rating in feedback.items():
                # Convert dimension name to lowercase for database constraint
                dimension_lower = dimension.lower()
                
                if dimension_lower == 'overall' and rating is not None:
                    # Store overall feedback in user_garments table
                    overall_feedback = {
                        1: "Too Tight",
                        2: "Tight but I Like It", 
                        3: "Good Fit",
                        4: "Loose but I Like It",
                        5: "Too Loose"
                    }.get(rating, "Good Fit")
                elif dimension_lower != 'overall' and rating is not None:
                    # Map rating to feedback text
                    feedback_text = {
                        1: "Too Tight",
                        2: "Tight but I Like It", 
                        3: "Good Fit",
                        4: "Loose but I Like It",
                        5: "Too Loose"
                    }.get(rating, "Good Fit")
                    
                    # Get feedback code ID
                    feedback_code_id = await conn.fetchval("""
                        SELECT id FROM feedback_codes 
                        WHERE feedback_text = $1
                    """, feedback_text)
                    
                    if feedback_code_id:
                        await conn.execute("""
                            INSERT INTO user_garment_feedback 
                            (user_garment_id, dimension, feedback_code_id, created_at)
                            VALUES ($1, $2, $3, NOW())
                        """, garment_id, dimension_lower, feedback_code_id)
                        
                        feedback_stored.append({
                            "dimension": dimension,
                            "rating": rating,
                            "feedback_text": feedback_text
                        })
            
            # Update user_garments with overall feedback
            if overall_feedback:
                await conn.execute("""
                    UPDATE user_garments 
                    SET fit_feedback = $1, feedback_timestamp = NOW()
                    WHERE id = $2
                """, overall_feedback, garment_id)
            
            # Generate immediate insights
            insights = await generate_tryon_insights(
                user_id, brand_id, size_tried, feedback, measurements, feedback_stored
            )
            
            # Log the try-on action
            await conn.execute("""
                INSERT INTO user_actions (
                    user_id, action_type, target_table, target_id, metadata, created_at
                ) VALUES ($1, $2, $3, $4, $5, NOW())
            """, int(user_id), 'submit_feedback', 'user_garments', garment_id, json.dumps({
                'session_id': session_id,
                'brand_id': brand_id,
                'size_tried': size_tried,
                'feedback_summary': feedback,
                'insights_generated': True
            }))
            
            return {
                "garment_id": garment_id,
                "status": "success",
                "insights": insights,
                "feedback_stored": feedback_stored,
                "message": "Try-on feedback saved successfully"
            }
    
    except Exception as e:
        print(f"Error submitting try-on feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/garment/{garment_id}/photos")
async def upload_garment_photo(
    garment_id: int,
    photo_data: dict
):
    """
    Upload a photo for a user garment.
    Accepts base64 encoded image data or a URL.
    """
    try:
        user_id = photo_data.get("user_id", "1")
        photo_type = photo_data.get("photo_type", "camera")  # camera, gallery, or tag
        caption = photo_data.get("caption", "")
        metadata = photo_data.get("metadata", {})
        is_primary = photo_data.get("is_primary", False)
        
        # Handle photo data - either base64 or URL
        if "photo_base64" in photo_data:
            # For base64 images, we'll store them locally and return a URL
            # In production, you'd upload to S3 or similar
            import base64
            import uuid
            
            photo_base64 = photo_data["photo_base64"]
            # Remove data:image prefix if present
            if "," in photo_base64:
                photo_base64 = photo_base64.split(",")[1]
            
            # Generate unique filename
            photo_id = str(uuid.uuid4())
            photo_filename = f"tryon_photos/{user_id}/{garment_id}/{photo_id}.jpg"
            
            # Create directory if it doesn't exist
            photo_dir = f"tryon_photos/{user_id}/{garment_id}"
            os.makedirs(photo_dir, exist_ok=True)
            
            # Save the image
            with open(photo_filename, "wb") as f:
                f.write(base64.b64decode(photo_base64))
            
            photo_url = f"/static/{photo_filename}"  # In production, this would be an S3 URL
        elif "photo_url" in photo_data:
            photo_url = photo_data["photo_url"]
        else:
            raise HTTPException(status_code=400, detail="Either photo_base64 or photo_url must be provided")
        
        async with pool.acquire() as conn:
            # If setting as primary, unset other primary photos
            if is_primary:
                await conn.execute("""
                    UPDATE user_garment_photos 
                    SET is_primary = FALSE 
                    WHERE user_garment_id = $1
                """, garment_id)
            
            # Insert the new photo
            photo_id = await conn.fetchval("""
                INSERT INTO user_garment_photos (
                    user_garment_id, photo_url, photo_type, caption, 
                    metadata, is_primary, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
                RETURNING id
            """, garment_id, photo_url, photo_type, caption, 
                json.dumps(metadata) if metadata else None, is_primary)
            
            # Log the action
            await conn.execute("""
                INSERT INTO user_actions (
                    user_id, action_type, target_table, target_id, 
                    new_values, metadata, created_at
                ) VALUES ($1, 'add_photo', 'user_garment_photos', $2, $3, $4, NOW())
            """, int(user_id), photo_id, json.dumps({
                "photo_url": photo_url,
                "photo_type": photo_type
            }), json.dumps({
                "garment_id": garment_id,
                "caption": caption
            }))
        
        return {
            "photo_id": photo_id,
            "photo_url": photo_url,
            "status": "success",
            "message": "Photo uploaded successfully"
        }
        
    except Exception as e:
        print(f"Error uploading photo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/garment/{garment_id}/photos")
async def get_garment_photos(garment_id: int):
    """
    Get all photos for a user garment.
    """
    try:
        async with pool.acquire() as conn:
            photos = await conn.fetch("""
                SELECT 
                    id,
                    photo_url,
                    photo_type,
                    caption,
                    metadata,
                    is_primary,
                    created_at
                FROM user_garment_photos
                WHERE user_garment_id = $1
                ORDER BY is_primary DESC, created_at DESC
            """, garment_id)
            
            return {
                "garment_id": garment_id,
                "photos": [dict(photo) for photo in photos],
                "total_photos": len(photos)
            }
            
    except Exception as e:
        print(f"Error getting photos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/photo/{photo_id}")
async def delete_garment_photo(photo_id: int, user_id: str = "1"):
    """
    Delete a garment photo.
    """
    try:
        async with pool.acquire() as conn:
            # Get photo info before deleting
            photo_info = await conn.fetchrow("""
                SELECT user_garment_id, photo_url 
                FROM user_garment_photos 
                WHERE id = $1
            """, photo_id)
            
            if not photo_info:
                raise HTTPException(status_code=404, detail="Photo not found")
            
            # Delete the photo record
            await conn.execute("""
                DELETE FROM user_garment_photos WHERE id = $1
            """, photo_id)
            
            # Log the action
            await conn.execute("""
                INSERT INTO user_actions (
                    user_id, action_type, target_table, target_id,
                    previous_values, metadata, created_at
                ) VALUES ($1, 'delete_photo', 'user_garment_photos', $2, $3, $4, NOW())
            """, int(user_id), photo_id, json.dumps({
                "photo_url": photo_info["photo_url"]
            }), json.dumps({
                "garment_id": photo_info["user_garment_id"]
            }))
            
            # TODO: Delete actual file if stored locally
            
            return {
                "status": "success",
                "message": "Photo deleted successfully"
            }
            
    except Exception as e:
        print(f"Error deleting photo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/garment/size-recommendation")
async def get_garment_size_recommendation(request: dict):
    """
    🎯 ENHANCED: Process product URL and return ALL sizes that match user's fit zones
    
    Returns format like: ["Good Fit - L", "Tight Fit - S", "Relaxed Fit - XL"]
    This captures the original Sies vision: scan a shirt tag and see ALL your size options
    """
    try:
        product_url = request.get("product_url")
        user_id = request.get("user_id", "1")  # Default to user 1
        user_fit_preference = request.get("fit_preference", "Standard")  # NEW: User's current preference
        
        if not product_url:
            raise HTTPException(status_code=400, detail="Product URL is required")
        
        print(f"🎯 Getting ALL matching sizes for user {user_id}, URL: {product_url}, preference: {user_fit_preference}")
        
        # Step 0: Extract real product name and log the scan action
        scan_action_id = None
        try:
            # Extract the actual product name and image from the webpage
            real_product_name = extract_product_name_from_url(product_url)
            real_product_image = extract_product_image_from_url(product_url)
            print(f"📦 Extracted product name: {real_product_name}")
            print(f"🖼️  Extracted product image: {real_product_image}")
            
            async with pool.acquire() as conn:
                import json
                scan_action_id = await conn.fetchval("""
                    INSERT INTO user_actions (
                        user_id, action_type, target_table, metadata, created_at
                    ) VALUES ($1, $2, $3, $4, NOW())
                    RETURNING id
                """, int(user_id), 'scan_item', 'garment_recommendations', json.dumps({
                    'product_url': product_url,
                    'user_fit_preference': user_fit_preference,
                    'scan_source': 'ios_app',
                    'product_name': real_product_name,
                    'product_image': real_product_image
                }))
                print(f"✅ Logged scan action for user {user_id}, action_id: {scan_action_id}")
        except Exception as e:
            print(f"⚠️ Failed to log scan action: {str(e)}")
        
        # Step 1: Extract brand from URL
        brand_info = extract_brand_from_url(product_url)
        if not brand_info:
            raise HTTPException(status_code=400, detail="Could not identify brand from URL")
        
        print(f"📊 Identified brand: {brand_info['brand_name']} (ID: {brand_info['brand_id']})")
        
        # Step 2: Use the Simple Multi-Dimensional Analyzer (practical approach)
        from simple_multi_dimensional_analyzer import SimpleMultiDimensionalAnalyzer
        
        db_config = {
            "database": os.getenv("DB_NAME", "postgres"),
            "user": os.getenv("DB_USER", "fs_core_rw"),
            "password": os.getenv("DB_PASSWORD", "CHANGE_ME"),
            "host": os.getenv("DB_HOST", "aws-1-us-east-1.pooler.supabase.com"),
            "port": os.getenv("DB_PORT", "5432")
        }
        
        analyzer = SimpleMultiDimensionalAnalyzer(db_config)
        
        # Get ALL sizes analyzed across all available dimensions
        size_analyses = analyzer.analyze_all_sizes(
            user_id=int(user_id),
            brand_name=brand_info['brand_name'],
            category="Tops",
            user_fit_preference=user_fit_preference
        )
        
        # Get fit zone recommendations in desired format
        fit_zone_recommendations = analyzer.get_fit_zone_recommendations(
            user_id=int(user_id),
            brand_name=brand_info['brand_name'],
            category="Tops",
            user_fit_preference=user_fit_preference
        )
        
        if not size_analyses:
            raise HTTPException(status_code=404, detail=f"No size recommendations available for {brand_info['brand_name']}. Try adding more garments to your closet for better recommendations.")
        
        print(f"🎯 Found {len(size_analyses)} analyzed sizes with {len(fit_zone_recommendations)} fit zone matches: {fit_zone_recommendations}")
        
        # Convert to API response format (enhanced with multi-dimensional analysis)
        api_recommendations = []
        for analysis in size_analyses:
            # Build dimension details
            dimension_details = {}
            measurement_summary = []
            
            for dimension, dim_analysis in analysis.dimension_analysis.items():
                if dimension == 'chest' and 'fit_zone' in dim_analysis:
                    # Chest with fit zone
                    dimension_details[dimension] = {
                        "type": "fit_zone",
                        "fit_zone": dim_analysis['fit_zone'],
                        "garment_measurement": dim_analysis['garment_measurement'],
                        "garment_range": dim_analysis.get('garment_range', f"{dim_analysis['garment_measurement']}\""),  # Add actual range
                        "zone_range": dim_analysis['zone_range'],
                        "matches_preference": dim_analysis['matches_preference'],
                        "fit_score": round(dim_analysis['score'], 3),
                        "explanation": dim_analysis['explanation']
                    }
                else:
                    # Other dimensions with good fit range
                    dimension_details[dimension] = {
                        "type": "good_fit_range",
                        "fits_well": dim_analysis['fits_well'],
                        "garment_measurement": dim_analysis['garment_measurement'],
                        "garment_range": dim_analysis.get('garment_range', f"{dim_analysis['garment_measurement']}\""),  # Add actual range
                        "good_fit_range": dim_analysis['good_fit_range'],
                        "fit_score": round(dim_analysis['score'], 3),
                        "confidence": round(dim_analysis['confidence'], 3),
                        "data_points": dim_analysis['data_points'],
                        "explanation": dim_analysis['explanation']
                    }
                
                # Use actual range from size guide instead of averaged value
                garment_range = dim_analysis.get('garment_range', f"{dim_analysis['garment_measurement']}\"")
                measurement_summary.append(f"{dimension}: {garment_range}")
            
            # Create fit zone display for this size
            if analysis.chest_fit_zone:
                zone_display = {
                    'tight': 'Tight Fit',
                    'standard': 'Good Fit',
                    'relaxed': 'Relaxed Fit'
                }.get(analysis.chest_fit_zone, 'Good Fit')
                size_with_fit_label = f"{zone_display} - {analysis.size_label}"
            else:
                zone_display = 'Good Fit'
                size_with_fit_label = f"Good Fit - {analysis.size_label}"
            
            api_recommendations.append({
                "size": analysis.size_label,
                "chest_fit_zone": analysis.chest_fit_zone,
                "fit_zone_display": zone_display,
                "size_with_fit_label": size_with_fit_label,  # 🎯 KEY ENHANCEMENT
                "overall_fit_score": round(analysis.overall_fit_score, 3),
                "confidence": round(analysis.overall_fit_score, 3),  # iOS expects confidence field
                "fits_all_dimensions": analysis.fits_all_dimensions,
                "fit_type": "excellent" if analysis.overall_fit_score >= 0.8 else 
                           "good" if analysis.overall_fit_score >= 0.6 else
                           "acceptable" if analysis.overall_fit_score >= 0.4 else "fair",
                "available_dimensions": list(analysis.dimension_analysis.keys()),
                "dimension_analysis": dimension_details,
                "measurement_summary": ", ".join(measurement_summary),
                "reasoning": analysis.reasoning,
                "primary_concerns": analysis.concerns,
                "fit_description": f"{zone_display} fit for size {analysis.size_label}",
                "matches_user_preference": analysis.chest_fit_zone == user_fit_preference.lower() if analysis.chest_fit_zone else False
            })
        
        # Best analysis is first in the sorted list
        best_analysis = size_analyses[0] if size_analyses else None
        
        # Get reference garments summary for confidence calculation
        reference_garments = {}
        if size_analyses:
            # Extract reference garments from the first analysis
            for analysis in size_analyses[:3]:  # Top 3 analyses
                if hasattr(analysis, 'reference_garments') and analysis.reference_garments:
                    reference_garments.update(analysis.reference_garments)
                    break
        
        # Calculate enhanced confidence tier and human explanations
        if best_analysis:
            confidence_info = calculate_confidence_tier(
                best_analysis.overall_fit_score,
                reference_garments if reference_garments else {},
                len(best_analysis.dimension_analysis) if hasattr(best_analysis, 'dimension_analysis') else 1,
                brand_info["brand_name"]
            )
            
            human_explanation = generate_human_readable_explanation(
                best_analysis, 
                reference_garments, 
                brand_info["brand_name"]
            )
            
            # Use confidence tier for fit label instead of technical scoring
            recommended_fit_label = f"{confidence_info['icon']} {confidence_info['label']} - {best_analysis.size_label}"
        else:
            confidence_info = {
                "tier": "poor",
                "label": "No Match",
                "icon": "❓",
                "color": "red",
                "description": "Not enough data"
            }
            human_explanation = "Add more garments to your closet for better recommendations"
            recommended_fit_label = "No match"
        
        # Generate alternative size explanations
        alternative_explanations = generate_alternative_size_explanations(size_analyses, best_analysis.size_label if best_analysis else "")
        
        # Step 6: Update scan action with actual product information
        if scan_action_id and best_analysis:
            try:
                async with pool.acquire() as conn:
                    import json
                    updated_metadata = {
                        'product_url': product_url,
                        'user_fit_preference': user_fit_preference,
                        'scan_source': 'ios_app',
                        'product_name': real_product_name,
                        'product_image': real_product_image,
                        'brand_name': brand_info["brand_name"],
                        'recommended_size': best_analysis.size_label,
                        'confidence_tier': confidence_info["label"],
                        'fit_score': round(best_analysis.overall_fit_score, 3)
                    }
                    await conn.execute("""
                        UPDATE user_actions 
                        SET metadata = $1
                        WHERE id = $2
                    """, json.dumps(updated_metadata), scan_action_id)
                    print(f"✅ Updated scan action {scan_action_id} with product info")
            except Exception as e:
                print(f"⚠️ Failed to update scan action: {str(e)}")

        # Enhanced response with ALL matching sizes and multi-dimensional analysis
        return {
            "product_url": product_url,
            "brand": brand_info["brand_name"],
            "analysis_type": "simple_multi_dimensional_analyzer",  # Updated analysis type
            "user_fit_preference": user_fit_preference,
            
            # 🎯 NEW: Enhanced confidence and explanation system
            "confidence_tier": confidence_info,
            "human_explanation": human_explanation,
            "alternative_explanations": alternative_explanations,
            
            # iOS app expects this field at root level (kept for compatibility)
            "confidence": round(confidence_info["confidence_score"], 2) if best_analysis else 0.5,
            "reasoning": human_explanation,  # Now uses human-readable explanation
            "primary_concerns": best_analysis.concerns if best_analysis else [],
            
            # 🎯 KEY ENHANCEMENT: All matching sizes with fit zone labels
            "all_matching_sizes": fit_zone_recommendations,  # ["Good Fit - L", "Tight Fit - S", etc.]
            "total_matches": len(fit_zone_recommendations),
            
            # Best single recommendation (for compatibility)
            "recommended_size": best_analysis.size_label if best_analysis else "Unknown",
            "recommended_fit_label": recommended_fit_label,
            "recommended_fit_score": round(best_analysis.overall_fit_score, 3) if best_analysis else 0,
            
            # Analysis details
            "dimensions_analyzed": list(best_analysis.dimension_analysis.keys()) if best_analysis else [],
            "fits_all_dimensions": best_analysis.fits_all_dimensions if best_analysis else False,
            "total_concerns": len(best_analysis.concerns) if best_analysis else 0,
            
            # Reference garments (required by iOS app)
            "reference_garments": _get_reference_garments_summary(size_analyses, int(user_id), brand_info["brand_name"]),
            
            # Summary and detailed breakdown
            "recommendation_summary": f"Found {len(size_analyses)} sizes analyzed across {len(list(best_analysis.dimension_analysis.keys()) if best_analysis else [])} dimensions",
            "comprehensive_analysis": True,
            "multi_dimensional_analysis": True,
            "all_sizes": api_recommendations,  # iOS expects "all_sizes"
            "all_sizes_detailed": api_recommendations,  # Keep for backwards compatibility
            
            # User guidance
            "user_guidance": _generate_simple_user_guidance(size_analyses, fit_zone_recommendations, user_fit_preference),
            "next_steps": [
                "Choose your preferred fit from the matching sizes above",
                "All dimensions (chest, neck, sleeve) have been analyzed based on your closet",
                "Sizes with concerns may still work depending on your preferences"
            ]
        }
        
    except Exception as e:
        print(f"Error getting enhanced size recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_user_guidance(recommendation, user_fit_preference: str) -> str:
    """Generate user-friendly guidance for the scan results"""
    if not recommendation.matching_sizes:
        return f"No sizes found that match your fit zones. Consider adding more garments to your closet for better recommendations."
    
    # Count matches by fit zone
    zone_counts = {}
    for match in recommendation.matching_sizes:
        zone = match.fit_zone_display
        zone_counts[zone] = zone_counts.get(zone, 0) + 1
    
    guidance_parts = []
    
    # Main message based on matches
    if len(recommendation.matching_sizes) == 1:
        match = recommendation.matching_sizes[0]
        guidance_parts.append(f"Found 1 size that fits your preferences: {match.fit_zone_display} - {match.size_label}")
    else:
        guidance_parts.append(f"Found {len(recommendation.matching_sizes)} sizes that could work for you!")
    
    # Zone-specific guidance
    if zone_counts:
        zone_summary = []
        for zone, count in zone_counts.items():
            if count == 1:
                zone_summary.append(f"1 {zone}")
            else:
                zone_summary.append(f"{count} {zone}")
        guidance_parts.append(f"Options: {', '.join(zone_summary)}")
    
    # Preference-specific advice
    user_pref_matches = [m for m in recommendation.matching_sizes if m.fit_zone == user_fit_preference.lower()]
    if user_pref_matches:
        guidance_parts.append(f"Your preferred {user_fit_preference} fit is available!")
    else:
        guidance_parts.append(f"No {user_fit_preference} fit available, but other options shown match your closet data.")
    
    return " ".join(guidance_parts)

# Enhanced confidence and explanation system for better UX
def calculate_confidence_tier(overall_fit_score: float, reference_garments: dict, dimensions_analyzed: int, brand_name: str) -> dict:
    """
    Calculate confidence tier with sophisticated weighting based on todoAug.md plan
    Returns dict with tier, label, icon, and description
    """
    # Base confidence from fit score
    base_confidence = overall_fit_score
    
    # Enhanced reference garment weighting (per todoAug.md)
    reference_boost = 0.0
    reference_count = len(reference_garments)
    
    if reference_count > 0:
        # Weight reference garments by quality factors
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for ref_key, ref_data in reference_garments.items():
            weight = 1.0
            
            # Same brand gets highest weight (per todoAug.md)
            if ref_data.get('brand', '').lower() == brand_name.lower():
                weight *= 2.0
            
            # Same category gets high weight (assuming shirts/tops)
            # In real implementation, would check category match
            weight *= 1.5
            
            # User satisfaction (high confidence = loved item)
            ref_confidence = ref_data.get('confidence', 0.5)
            if ref_confidence > 0.8:
                weight *= 1.3  # Loved items
            elif ref_confidence < 0.4:
                weight *= 0.7  # Returned/disliked items
            
            # Recent items weighted higher (would need timestamp in real implementation)
            # For now, assume all items are reasonably recent
            
            weighted_confidence += ref_confidence * weight
            total_weight += weight
        
        # Calculate reference boost (up to 30% boost for excellent references)
        if total_weight > 0:
            avg_weighted_confidence = weighted_confidence / total_weight
            reference_boost = min(avg_weighted_confidence * 0.3, 0.3)
    
    # Boost confidence based on dimensions analyzed (more data = higher confidence)  
    dimension_boost = min(dimensions_analyzed * 0.05, 0.15)  # Max 15% boost
    
    # Calculate final confidence
    final_confidence = min(base_confidence + reference_boost + dimension_boost, 1.0)
    
    # Determine tier
    if final_confidence >= 0.9:
        return {
            "tier": "excellent",
            "confidence_score": final_confidence,
            "label": "Perfect Fit",
            "icon": "✅",
            "color": "green",
            "description": "This will fit you perfectly"
        }
    elif final_confidence >= 0.7:
        return {
            "tier": "good", 
            "confidence_score": final_confidence,
            "label": "Great Fit",
            "icon": "✅",
            "color": "green", 
            "description": "This will fit you well"
        }
    elif final_confidence >= 0.5:
        return {
            "tier": "fair",
            "confidence_score": final_confidence, 
            "label": "Good Fit",
            "icon": "⚠️",
            "color": "orange",
            "description": "This should work for you"
        }
    else:
        return {
            "tier": "poor",
            "confidence_score": final_confidence,
            "label": "Uncertain Fit", 
            "icon": "❓",
            "color": "red",
            "description": "Not enough data for a confident recommendation"
        }

def generate_human_readable_explanation(size_analysis, reference_garments: dict, brand_name: str) -> str:
    """
    Generate anxiety-reducing, confidence-building explanations based on todoAug.md plan
    Uses contextual reference garments and human language instead of technical jargon
    """
    if not size_analysis:
        return "Add more garments to your closet for better recommendations"
    
    # Get confidence tier with enhanced weighting
    confidence = calculate_confidence_tier(
        size_analysis.overall_fit_score,
        reference_garments,
        len(size_analysis.dimension_analysis) if hasattr(size_analysis, 'dimension_analysis') else 1,
        brand_name
    )
    
    ref_count = len(reference_garments) if reference_garments else 0
    
    # Priority 1: Same brand references (highest confidence per todoAug.md)
    same_brand_refs = []
    other_brand_refs = []
    
    for ref_key, ref_data in reference_garments.items():
        if isinstance(ref_data, dict) and 'brand' in ref_data:
            if ref_data['brand'].lower() == brand_name.lower():
                same_brand_refs.append(ref_data)
            else:
                other_brand_refs.append(ref_data)
    
    # Generate contextual explanations based on confidence tier
    if confidence["tier"] == "excellent":
        if same_brand_refs:
            if len(same_brand_refs) > 1:
                return f"Perfect match - same measurements as your other {brand_name} shirts"
            else:
                return f"Just like your {brand_name} shirt that fits perfectly"
        elif len(other_brand_refs) >= 2:
            # Multiple different brands
            brands = list(set([ref['brand'] for ref in other_brand_refs[:3]]))  # Top 3 brands
            if len(brands) == 2:
                return f"Same measurements as your {brands[0]} and {brands[1]} shirts"
            else:
                return f"Same measurements as your favorite shirts from {brands[0]}, {brands[1]}, and others"
        elif len(other_brand_refs) == 1:
            return f"Same measurements as your {other_brand_refs[0]['brand']} shirt"
        else:
            return "Perfect fit based on your body measurements"
    
    elif confidence["tier"] == "good":
        if same_brand_refs:
            return f"Should fit well - similar to your {brand_name} shirts"
        elif other_brand_refs:
            best_ref = max(other_brand_refs, key=lambda x: x.get('confidence', 0))
            return f"Should fit well - similar to your {best_ref['brand']} shirt"
        else:
            return "Good fit based on your measurements"
    
    elif confidence["tier"] == "fair":
        if same_brand_refs:
            return f"Try your usual {brand_name} size - you can always exchange if needed"
        elif other_brand_refs:
            return f"Based on your closet, this should work - similar fit to your other shirts"
        else:
            return "This might work based on typical sizing for your measurements"
    
    else:  # poor confidence
        if brand_name:
            return f"Not enough data - consider ordering your usual {brand_name} size"
        else:
            return "Limited data available - consider adding more garments to your closet"


def generate_alternative_size_explanations(size_analyses, recommended_size: str) -> list:
    """
    Generate clear, non-contradictory explanations for why other sizes aren't recommended.
    Uses dimension-level details when available instead of generic labels.
    """
    explanations = []

    # Get the recommended analysis for comparison
    recommended_analysis = next((a for a in size_analyses if a.size_label == recommended_size), None)
    if not recommended_analysis:
        return explanations

    # Helper to extract a friendly range string
    def _get_range_str(dim):
        d = dim or {}
        return d.get('garment_range') or d.get('good_fit_range') or 'N/A'

    # Helper to extract good range min/max from the stored string "X-Y\""
    def _parse_good_range(dim):
        try:
            rng = (dim or {}).get('good_fit_range') or ''
            rng = rng.replace('"', '')
            parts = [p.strip() for p in rng.split('-')]
            if len(parts) == 2:
                return float(parts[0]), float(parts[1])
        except Exception:
            pass
        return None, None

    # Analyze other sizes
    for analysis in size_analyses[:3]:  # Top 3 sizes only
        if analysis.size_label == recommended_size:
            continue

        size_label = analysis.size_label

        chest = analysis.dimension_analysis.get('chest') if hasattr(analysis, 'dimension_analysis') else None
        neck = analysis.dimension_analysis.get('neck') if hasattr(analysis, 'dimension_analysis') else None
        sleeve = analysis.dimension_analysis.get('sleeve') if hasattr(analysis, 'dimension_analysis') else None

        chest_msg = None
        if chest:
            # Prefer explicit zone/range message over a vague "too tight"
            zone = chest.get('fit_zone')
            zone_range = chest.get('zone_range')
            chest_range = _get_range_str(chest)
            if zone == 'tight':
                chest_msg = f"Chest {chest_range} is slimmer than your Good zone ({zone_range})"
            elif zone == 'relaxed':
                chest_msg = f"Chest {chest_range} is roomier than your Good zone ({zone_range})"

        neck_msg = None
        if neck:
            gmin, gmax = _parse_good_range(neck)
            neck_range = _get_range_str(neck)
            gm = neck.get('garment_measurement')
            if gmin is not None and gm is not None:
                if gm < gmin:
                    neck_msg = f"Neck {neck_range} is below your preferred {gmin:.1f}-{gmax:.1f}"
                elif gmax is not None and gm > gmax:
                    neck_msg = f"Neck {neck_range} is above your preferred {gmin:.1f}-{gmax:.1f}"

        sleeve_msg = None
        if sleeve and not sleeve.get('fits_well', True):
            sleeve_range = _get_range_str(sleeve)
            smin, smax = _parse_good_range(sleeve)
            if smin is not None and smax is not None:
                sleeve_msg = f"Sleeve {sleeve_range} is outside your preferred {smin:.1f}-{smax:.1f}"

        # Compose ordered explanation emphasizing neck, then chest, then sleeve
        parts = [p for p in [neck_msg, chest_msg, sleeve_msg] if p]
        if not parts:
            if analysis.overall_fit_score < recommended_analysis.overall_fit_score:
                parts = ["Not as good overall fit"]
            else:
                parts = ["Alternative option"]

        explanations.append({
            "size": size_label,
            "explanation": "; ".join(parts),
            "fit_score": analysis.overall_fit_score
        })

    return explanations

def _generate_simple_user_guidance(size_analyses, fit_zone_recommendations, user_fit_preference: str) -> str:
    """Generate user-friendly guidance for the simple multi-dimensional analyzer results"""
    if not size_analyses:
        return "No sizes found that work well across your established fit preferences. Consider adding more garments with feedback to your closet."
    
    guidance_parts = []
    
    # Main message
    if len(fit_zone_recommendations) == 1:
        guidance_parts.append(f"Found 1 size that matches your preferences: {fit_zone_recommendations[0]}")
    elif len(fit_zone_recommendations) > 1:
        guidance_parts.append(f"Found {len(fit_zone_recommendations)} sizes that could work for you!")
    else:
        guidance_parts.append(f"Analyzed {len(size_analyses)} sizes across multiple dimensions.")
    
    # Count dimensions analyzed
    if size_analyses:
        dimensions_count = len(size_analyses[0].dimension_analysis.keys())
        if dimensions_count > 1:
            dimensions_list = list(size_analyses[0].dimension_analysis.keys())
            guidance_parts.append(f"Analysis included {dimensions_count} dimensions: {', '.join(dimensions_list)}.")
    
    # Check for user preference matches
    if fit_zone_recommendations:
        pref_matches = [rec for rec in fit_zone_recommendations if user_fit_preference.lower() in rec.lower()]
        if pref_matches:
            guidance_parts.append(f"Your preferred {user_fit_preference} fit is available!")
        else:
            guidance_parts.append(f"No exact {user_fit_preference} fit found, but alternatives shown are based on your closet data.")
    
    return " ".join(guidance_parts)

def _get_reference_garments_summary(size_analyses, user_id: int = 1, target_brand: str = None) -> dict:
    """Generate reference garments summary from actual user garments with brand prioritization"""
    if not size_analyses:
        return {}
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user's actual garments with measurements and feedback, prioritizing same brand
        query = """
            SELECT DISTINCT
                b.name as brand,
                ug.product_name,
                ug.size_label,
                sge.chest_min, sge.chest_max, sge.chest_range,
                sge.neck_min, sge.neck_max, sge.neck_range,
                sge.sleeve_min, sge.sleeve_max, sge.sleeve_range,
                -- Get latest feedback for each dimension
                (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as chest_feedback,
                (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as overall_feedback,
                -- Brand priority for sorting
                CASE WHEN b.name = %s THEN 1 ELSE 2 END as brand_priority,
                ug.created_at
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
            WHERE ug.user_id = %s 
            AND ug.owns_garment = true
            AND sge.id IS NOT NULL
            ORDER BY 
                brand_priority,  -- Same brand first
                ug.created_at DESC
            LIMIT 3
        """
        
        print(f"🔍 Querying reference garments for user {user_id}, target_brand: '{target_brand}'")
        cur.execute(query, (target_brand or '', user_id))
        user_garments = cur.fetchall()
        print(f"📊 Found {len(user_garments)} user garments in database")
        
        reference_garments = {}
        
        for idx, garment in enumerate(user_garments):
            print(f"🔍 Processing garment {idx+1}: {garment['brand']} - {garment['product_name']} - Size {garment['size_label']}")
            garment_key = f"user_garment_{idx + 1}"
            
            # Determine fit relationship to target
            if garment['brand'] == target_brand:
                if garment['size_label'] == size_analyses[0].size_label if size_analyses else None:
                    fit_description = "Same brand, same size!"
                else:
                    fit_description = "Same brand, different size"
            else:
                if garment['size_label'] == size_analyses[0].size_label if size_analyses else None:
                    fit_description = "Same size, similar fit"
                else:
                    # Compare chest measurements for fit description
                    if garment.get('chest_min') and garment.get('chest_max'):
                        chest_avg = (garment['chest_min'] + garment['chest_max']) / 2
                        if 40 <= chest_avg <= 44:  # Assuming target is in this range
                            fit_description = "Good chest match"
                        else:
                            fit_description = "Different fit profile"
                    else:
                        fit_description = "Reference garment"
            
            reference_garments[garment_key] = {
                "brand": garment['brand'],
                "product_name": garment['product_name'] or "Garment",
                "size": garment['size_label'],
                "size_label": garment['size_label'],
                "measurements": {
                    "chest": f"{garment['chest_min']}-{garment['chest_max']}" if garment.get('chest_min') and garment.get('chest_max') else "N/A",
                    "neck": f"{garment['neck_min']}-{garment['neck_max']}" if garment.get('neck_min') and garment.get('neck_max') else "N/A",
                    "sleeve": f"{garment['sleeve_min']}-{garment['sleeve_max']}" if garment.get('sleeve_min') and garment.get('sleeve_max') else "N/A"
                },
                "feedback": {
                    "overall": garment['overall_feedback'] or "Good Fit",
                    "chest": garment['chest_feedback'] or "Good Fit",
                    "fit_assessment": "Reference"
                },
                "fit_feedback": garment['overall_feedback'] or "Good Fit",
                "confidence": 0.9 if garment['brand'] == target_brand else 0.7,
                "fit_description": fit_description,
                "is_same_brand": garment['brand'] == target_brand
            }
        
        cur.close()
        conn.close()
        
        # If no actual garments found, fall back to generic profile
        if not reference_garments:
            reference_garments["user_profile"] = {
                "brand": "User Profile",
                "product_name": "Fit Analysis",
                "size": "Various",
                "size_label": "Various",
                "measurements": {"overall": "Multi-dimensional analysis"},
                "feedback": {"overall": "Analyzed", "fit_assessment": "Profile-based"},
                "fit_feedback": "Profile-based analysis",
                "confidence": 0.6,
                "fit_description": "Based on your closet data",
                "is_same_brand": False
            }
        
        print(f"🎯 Final reference_garments being returned: {reference_garments}")
        return reference_garments
        
    except Exception as e:
        print(f"Error getting reference garments: {str(e)}")
        # Fallback to empty dict
        return {}

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

@app.get("/user/{user_id}/tryons")
async def get_user_tryons(user_id: str):
    """Get user's try-on history"""
    try:
        async with pool.acquire() as conn:
            tryons = await conn.fetch("""
                SELECT 
                    ug.id,
                    b.name as brand,
                    b.id as brand_id,
                    g.product_name,
                    g.product_url,
                    g.image_url,
                    g.fit_type,
                    ug.size_label as size_tried,
                    ug.color as color_tried,
                    ug.fit_feedback as overall_feedback,
                    ug.created_at as try_on_date,
                    -- Get dimensional feedback
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest' 
                     LIMIT 1) as chest_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'waist' 
                     LIMIT 1) as waist_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'sleeve' 
                     LIMIT 1) as sleeve_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'neck' 
                     LIMIT 1) as neck_feedback
                FROM user_garments ug
                JOIN garments g ON ug.garment_id = g.id
                JOIN brands b ON g.brand_id = b.id
                WHERE ug.user_id = $1 
                AND ug.owns_garment = false  -- Only try-on sessions, not owned garments
                AND ug.fit_feedback IS NOT NULL  -- Only completed try-ons with feedback
                ORDER BY ug.created_at DESC
            """, int(user_id))
            
            # Format the response
            result = []
            for tryon in tryons:
                # Get size guide measurements for this brand/size
                measurements = {}
                try:
                    size_measurements = await conn.fetch("""
                        SELECT m.measurement_type, m.min_value, m.max_value, m.unit
                        FROM measurements m
                        JOIN measurement_sets ms ON m.set_id = ms.id
                        WHERE ms.brand_id = $1 
                        AND m.size_label = $2
                        AND ms.scope = 'size_guide'
                        AND m.measurement_category = 'body'
                    """, tryon['brand_id'], tryon['size_tried'])
                    
                    for measurement in size_measurements:
                        measurement_name = measurement['measurement_type'].replace('body_', '').title()
                        if measurement['min_value'] == measurement['max_value']:
                            measurements[measurement_name] = f"{measurement['min_value']} {measurement['unit']}"
                        else:
                            measurements[measurement_name] = f"{measurement['min_value']}-{measurement['max_value']} {measurement['unit']}"
                except:
                    # If measurement lookup fails, continue without measurements
                    pass
                
                # Get image URL - check J.Crew cache first, then garments table, then fetch on-demand
                image_url = tryon['image_url']
                if not image_url and tryon['product_url'] and 'jcrew.com' in tryon['product_url'].lower():
                    # Check J.Crew cache first - try exact match, then base URL match
                    try:
                        # First try exact URL match
                        cached_result = await conn.fetchrow("""
                            SELECT product_image 
                            FROM jcrew_product_cache 
                            WHERE product_url = $1 AND product_image IS NOT NULL AND product_image != ''
                        """, tryon['product_url'])
                        
                        if not cached_result:
                            # Try base URL match (without query parameters)
                            from urllib.parse import urlparse, urlunparse
                            parsed_url = urlparse(tryon['product_url'])
                            base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
                            
                            cached_result = await conn.fetchrow("""
                                SELECT product_image 
                                FROM jcrew_product_cache 
                                WHERE product_url = $1 AND product_image IS NOT NULL AND product_image != ''
                            """, base_url)
                        
                        if cached_result and cached_result['product_image']:
                            image_url = cached_result['product_image']
                            print(f"🖼️ Using cached J.Crew image for {tryon['product_name']}: {image_url}")
                    except Exception as e:
                        print(f"Cache lookup failed: {e}")
                    
                    # If still no image, try to fetch on-demand
                    if not image_url:
                        try:
                            image_url = extract_product_image_from_url(tryon['product_url'])
                            print(f"🖼️ Fetched image for {tryon['product_name']}: {image_url}")
                        except Exception as e:
                            print(f"Image fetch failed: {e}")
                
                result.append({
                    "id": tryon['id'],
                    "brand": tryon['brand'],
                    "product_name": tryon['product_name'],
                    "product_url": tryon['product_url'],
                    "image_url": image_url,
                    "fit_type": tryon['fit_type'],
                    "size_tried": tryon['size_tried'],
                    "color_tried": tryon['color_tried'],
                    "overall_feedback": tryon['overall_feedback'] or "No feedback",
                    "chest_feedback": tryon['chest_feedback'],
                    "waist_feedback": tryon['waist_feedback'],
                    "sleeve_feedback": tryon['sleeve_feedback'],
                    "neck_feedback": tryon['neck_feedback'],
                    "try_on_date": tryon['try_on_date'].isoformat(),
                    "measurements": measurements
                })
            
            return result
            
    except Exception as e:
        print(f"Error fetching user try-ons: {str(e)}")
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
        
        # Brand detection logic (IDs match database brands table)
        if "uniqlo.com" in domain:
            return {"brand_name": "Uniqlo", "brand_id": 1}  # No Uniqlo in DB yet
        elif "jcrew.com" in domain:
            return {"brand_name": "J.Crew", "brand_id": 4}  # J.Crew = ID 4 in DB
        elif "bananarepublic.com" in domain or "bananarepublic.gap.com" in domain:
            return {"brand_name": "Banana Republic", "brand_id": 5}  # Banana Republic = ID 5 in DB
        elif "theory.com" in domain:
            return {"brand_name": "Theory", "brand_id": 9}  # Theory = ID 9 in DB
        elif "patagonia.com" in domain:
            return {"brand_name": "Patagonia", "brand_id": 2}  # Patagonia = ID 2 in DB
        elif "lululemon.com" in domain:
            return {"brand_name": "Lululemon", "brand_id": 1}  # Lululemon = ID 1 in DB
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
    try:
        # Use synchronous database connection since pool might not be available
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Try new measurement system first
        cur.execute("""
            SELECT DISTINCT m.measurement_type
            FROM measurements m
            JOIN measurement_sets ms ON m.set_id = ms.id
            WHERE ms.brand_id = %s 
            AND ms.scope = 'size_guide'
            AND m.measurement_category = 'body'
        """, (brand_id,))
        
        measurement_types = cur.fetchall()
        measurements = ['overall']  # Always include overall
        
        if measurement_types:
            # Convert measurement types to feedback categories
            for row in measurement_types:
                measurement_type = row['measurement_type']
                if 'chest' in measurement_type:
                    measurements.append('chest')
                elif 'neck' in measurement_type:
                    measurements.append('neck')
                elif 'sleeve' in measurement_type or 'arm' in measurement_type:
                    measurements.append('sleeve')
                elif 'waist' in measurement_type:
                    measurements.append('waist')
        else:
            # Fallback to old system for backward compatibility
            cur.execute("""
                SELECT 
                    chest_min, chest_max,
                    neck_min, neck_max,
                    sleeve_min, sleeve_max,
                    waist_min, waist_max
                FROM size_guides_v2 
                WHERE brand_id = %s 
                LIMIT 1
            """, (brand_id,))
            
            size_guide = cur.fetchone()
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
    except Exception as e:
        print(f"Error getting brand measurements: {e}")
        # Return default measurements if database query fails
        return {
            "measurements": ['overall', 'chest', 'neck', 'sleeve'],
            "feedbackOptions": [
                {"value": 1, "label": "Too tight"},
                {"value": 2, "label": "Tight but I like it"},
                {"value": 3, "label": "Good"},
                {"value": 4, "label": "Loose but I like it"},
                {"value": 5, "label": "Too loose"}
            ]
        }
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

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
    """Provide fit feedback options for dropdown (legacy endpoint for backward compatibility)"""
    return {
        "feedbackOptions": [
            {"value": 1, "label": "Too tight"},
            {"value": 2, "label": "Tight but I like it"},
            {"value": 3, "label": "Good"},
            {"value": 4, "label": "Loose but I like it"},
            {"value": 5, "label": "Too loose"}
        ]
    }

@app.get("/fit_feedback_options/{dimension}")
async def get_fit_feedback_options_by_dimension(dimension: str):
    """Get appropriate feedback codes for a specific dimension"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Use the database function to get dimension-specific options
        cur.execute("""
            SELECT get_feedback_options(%s) as options
        """, (dimension,))
        
        result = cur.fetchone()
        
        if result and result['options']:
            return {"feedbackOptions": result['options']}
        else:
            # Fallback to default options if dimension not found
            return await get_fit_feedback_options()
            
    except Exception as e:
        print(f"Error getting feedback options for {dimension}: {e}")
        # Return default options on error
        return await get_fit_feedback_options()
    finally:
        cur.close()
        conn.close()

@app.get("/garment/{garment_id}/measurements")
async def get_garment_measurements(garment_id: int):
    """Get garment measurements for feedback UI"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get garment measurements from size guide entries
        cur.execute("""
            SELECT 
                'chest' as measurement_type,
                CASE 
                    WHEN sge.chest_min = sge.chest_max THEN sge.chest_min::text
                    ELSE sge.chest_min::text || '-' || sge.chest_max::text
                END as measurement_value,
                'inches' as unit,
                'size_guide' as measurement_source
            FROM user_garments ug
            LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
            WHERE ug.id = %s AND sge.chest_min IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'neck' as measurement_type,
                CASE 
                    WHEN sge.neck_min = sge.neck_max THEN sge.neck_min::text
                    ELSE sge.neck_min::text || '-' || sge.neck_max::text
                END as measurement_value,
                'inches' as unit,
                'size_guide' as measurement_source
            FROM user_garments ug
            LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
            WHERE ug.id = %s AND sge.neck_min IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'sleeve' as measurement_type,
                CASE 
                    WHEN sge.sleeve_min = sge.sleeve_max THEN sge.sleeve_min::text
                    ELSE sge.sleeve_min::text || '-' || sge.sleeve_max::text
                END as measurement_value,
                'inches' as unit,
                'size_guide' as measurement_source
            FROM user_garments ug
            LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
            WHERE ug.id = %s AND sge.sleeve_min IS NOT NULL
            
            ORDER BY measurement_type
        """, (garment_id, garment_id, garment_id))
        
        measurements_data = cur.fetchall()
        
        # Format measurements for the UI
        measurements = {}
        for row in measurements_data:
            # Format the measurement value with unit
            value_str = f"{row['measurement_value']}\""
            measurements[row['measurement_type']] = value_str
        
        return {
            "garment_id": garment_id,
            "measurements": measurements,
            "count": len(measurements)
        }
        
    except Exception as e:
        print(f"Error getting garment measurements: {str(e)}")
        return {
            "garment_id": garment_id,
            "measurements": {},
            "count": 0,
            "error": str(e)
        }
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.post("/garment/{garment_id}/feedback")
async def update_garment_feedback(garment_id: int, request: dict):
    """Update feedback with action tracking and undo support - Enhanced for body + garment measurements"""
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
                SELECT ug.id, g.brand_id, ug.size_label 
                FROM user_garments ug
                LEFT JOIN garments g ON ug.garment_id = g.id
                WHERE ug.id = $1 AND ug.user_id = $2
            """, garment_id, user_id)
            
            if not garment:
                raise HTTPException(status_code=404, detail="Garment not found or doesn't belong to user")
            
            # Separate body and garment feedback
            body_feedback = {}
            garment_feedback = {}
            
            for key, value in feedback.items():
                if key.startswith('garment_'):
                    # Remove 'garment_' prefix for the measurement type
                    measurement_type = key.replace('garment_', '')
                    garment_feedback[measurement_type] = value
                else:
                    body_feedback[key] = value
            
            # Get current body feedback values BEFORE changing them (for undo)
            current_body_feedback = await conn.fetch("""
                SELECT ugf.dimension, fc.feedback_text, ugf.id
                FROM user_garment_feedback ugf
                JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                WHERE ugf.user_garment_id = $1
            """, garment_id)
            
            # Get current garment feedback values BEFORE changing them (for undo)
            current_garment_feedback = await conn.fetch("""
                SELECT ugf.dimension as measurement_type, fc.feedback_text, ugf.id
                FROM user_garment_feedback ugf
                JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                WHERE ugf.user_garment_id = $1
            """, garment_id)
            
            # Store previous values for undo
            previous_values = {
                'body': {
                    row['dimension']: {
                        'feedback_text': row['feedback_text'],
                        'feedback_id': row['id']
                    }
                    for row in current_body_feedback
                },
                'garment': {
                    row['measurement_type']: {
                        'feedback_text': row['feedback_text'],
                        'feedback_id': row['id']
                    }
                    for row in current_garment_feedback
                }
            }
            
            new_values = {'body': {}, 'garment': {}}
            
            # Process body measurements (existing logic)
            if body_feedback:
                # Convert numeric feedback values to text descriptions
                body_feedback_text = convert_feedback_to_text(body_feedback)
                
                # Delete old body feedback entries
                await conn.execute("""
                    DELETE FROM user_garment_feedback 
                    WHERE user_garment_id = $1
                """, garment_id)
                
                # Insert new body feedback entries
                for dimension, feedback_text_value in body_feedback_text.items():
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
                            
                            new_values['body'][dimension] = {
                                'feedback_text': feedback_text_value,
                                'feedback_id': new_id
                            }
            
            # Process garment measurements (new logic)
            if garment_feedback:
                # Delete old garment feedback entries
                await conn.execute("""
                    DELETE FROM user_garment_feedback 
                    WHERE user_garment_id = $1
                """, garment_id)
                
                # Convert garment feedback values to text
                garment_feedback_text = convert_garment_feedback_to_text(garment_feedback)
                
                # Insert new garment feedback entries
                for measurement_type, feedback_text_value in garment_feedback_text.items():
                    if feedback_text_value:
                        # Get feedback code ID
                        feedback_code = await conn.fetchrow("""
                            SELECT id FROM feedback_codes 
                            WHERE feedback_text = $1
                        """, feedback_text_value)
                        
                        if feedback_code:
                            # Insert new garment feedback
                            new_id = await conn.fetchval("""
                                INSERT INTO user_garment_feedback (
                                    user_garment_id,
                                    dimension,
                                    feedback_code_id
                                ) VALUES ($1, $2, $3) RETURNING id
                            """, 
                                garment_id,
                                measurement_type,
                                feedback_code['id']
                            )
                            
                            new_values['garment'][measurement_type] = {
                                'feedback_text': feedback_text_value,
                                'feedback_id': new_id
                            }
            
            # Update fit_feedback in user_garments (only if body feedback exists)
            if body_feedback:
                body_feedback_text = convert_feedback_to_text(body_feedback)
                await conn.execute("""
                    UPDATE user_garments
                    SET fit_feedback = $1
                    WHERE id = $2
                """, body_feedback_text.get('overall'), garment_id)
            
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
                    'body_dimensions_changed': list(body_feedback.keys()) if body_feedback else [],
                    'garment_dimensions_changed': list(garment_feedback.keys()) if garment_feedback else [],
                    'screen': 'garment_detail'
                })
            )
        
        trigger_db_snapshot()
        
        return {
            "status": "success",
            "message": f"Feedback updated successfully - Body: {len(body_feedback)} dimensions, Garment: {len(garment_feedback)} dimensions",
            "action_id": action_id,
            "can_undo": True,
            "body_feedback_count": len(body_feedback),
            "garment_feedback_count": len(garment_feedback)
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

def convert_garment_feedback_to_text(garment_feedback: dict) -> dict:
    """Convert numeric garment feedback values to text descriptions."""
    # Mapping for garment measurements based on your specifications
    garment_mapping = {
        'center_back_length': {  # Body length back
            30: "Too Long (Garment)",
            31: "Too Short (Garment)", 
            32: "Right Length"
        },
        'shoulder_width': {  # Shoulder width
            33: "Too Wide",
            34: "Too Narrow",
            35: "Right Width"
        },
        'chest_width': {  # Body width (laid flat)
            36: "Too Wide (Body)",
            37: "Too Narrow (Body)",
            38: "Right Width (Body)"
        },
        'sleeve_length': {  # Sleeve length (center back)
            39: "Too Long (Sleeve)",
            40: "Too Short (Sleeve)",
            41: "Right Length (Sleeve)"
        }
    }
    
    result = {}
    for measurement_type, feedback_value in garment_feedback.items():
        if measurement_type in garment_mapping:
            measurement_codes = garment_mapping[measurement_type]
            if feedback_value in measurement_codes:
                result[measurement_type] = measurement_codes[feedback_value]
    
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
    Get personalized shopping recommendations based on user's fit analysis.
    Uses MultiDimensionalFitAnalyzer to provide real fit scores for actual products.
    """
    try:
        user_id = request.get("user_id")
        category = request.get("category")
        filters = request.get("filters", {})
        fit_zone = filters.get("fit_zone", "Standard")  # Default to Standard if not specified
        limit = request.get("limit", 20)
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
            
        print(f"🎯 Shop recommendations request: user_id={user_id}, category={category}, fit_zone={fit_zone}")

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user's fit zones for filtering (FAST database lookup)
        selected_zone_range = None
        if category == "Tops" and fit_zone != "All":
            try:
                from fit_zone_service import FitZoneService
                
                fit_zone_service = FitZoneService(DB_CONFIG)
                stored_fit_zones = fit_zone_service.get_stored_fit_zones(user_id, category)
                
                if stored_fit_zones and 'chest' in stored_fit_zones:
                    chest_zones = stored_fit_zones['chest']
                    if fit_zone.lower() in chest_zones:
                        selected_zone_range = chest_zones[fit_zone.lower()]
                        print(f"⚡ Using stored fit zones for {fit_zone}: {selected_zone_range}")
                    else:
                        print(f"⚠️ Fit zone '{fit_zone}' not found in stored zones: {list(chest_zones.keys()) if chest_zones else 'None'}")
                else:
                    print(f"⚠️ No stored fit zones found for user {user_id}, category {category}")
                    # TODO: Trigger background fit zone calculation for this user
                    
            except Exception as e:
                print(f"⚠️ Could not retrieve stored fit zones: {str(e)}, proceeding without fit zone filtering")
        
        # Get available products from our products table
        category_filter = ""
        if category and category != "All":
            category_filter = "AND c.name = %s"
            
        cur.execute(f"""
            SELECT p.id, p.name, p.price, p.image_url, p.product_url, p.description,
                   b.id as brand_id, b.name as brand_name, c.name as category
            FROM products p
            JOIN brands b ON p.brand_id = b.id
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = true
            {category_filter}
            ORDER BY p.created_at DESC
            LIMIT {limit * 2}
        """, (category,) if category and category != "All" else ())
        
        products = cur.fetchall()
        
        if not products:
            cur.close()
            conn.close()
            return {
                "recommendations": [],
                "total_count": 0,
                "has_more": False
            }

        # Initialize the MultiDimensionalFitAnalyzer
        from multi_dimensional_fit_analyzer import MultiDimensionalFitAnalyzer
        analyzer = MultiDimensionalFitAnalyzer(DB_CONFIG)
        
        recommendations = []
        
        # Get fit analysis for each product (with timeout protection)
        processed_count = 0
        filtered_count = 0  # Track how many products were filtered out by fit zones
        max_processing_time = 10  # seconds
        start_time = datetime.now()
        
        for product in products:
            # Check if we've spent too much time processing
            if (datetime.now() - start_time).total_seconds() > max_processing_time:
                print(f"Processing timeout reached, returning {len(recommendations)} recommendations")
                break
                
            try:
                # Get comprehensive size recommendations for this brand/category
                fit_result = analyzer.get_comprehensive_size_recommendations(
                    user_id=user_id,
                    brand_name=product['brand_name'],
                    category='Tops'  # We only have Tops category for now
                )
                
                if fit_result and len(fit_result) > 0:
                    # Find the best recommendation from the fit analysis
                    best_rec = None
                    best_score = 0
                    
                    for size_rec in fit_result:
                        if size_rec.overall_fit_score > best_score:
                            best_score = size_rec.overall_fit_score
                            best_rec = size_rec
                    
                    if best_rec:
                        # Apply fit zone filtering if requested
                        should_include_product = True
                        if selected_zone_range:
                            zone_min = selected_zone_range.get("min", 0)
                            zone_max = selected_zone_range.get("max", 999)
                            
                            # Get chest measurement from the recommended size
                            chest_measurement = None
                            if "chest" in best_rec.dimension_scores:
                                chest_measurement = best_rec.dimension_scores["chest"]["garment_measurement"]
                            
                            # Check if garment falls within user's selected fit zone
                            if chest_measurement is not None:
                                if not (zone_min <= chest_measurement <= zone_max):
                                    should_include_product = False
                                    filtered_count += 1
                                    print(f"🚫 Filtered out {product['name']} - chest {chest_measurement:.1f}\" outside {fit_zone} range [{zone_min:.1f}\"-{zone_max:.1f}\"]")
                                else:
                                    print(f"✅ Including {product['name']} - chest {chest_measurement:.1f}\" fits {fit_zone} range [{zone_min:.1f}\"-{zone_max:.1f}\"]")
                        
                        if should_include_product:
                            # Convert fit analysis to recommendation format (matching iOS ShopItem model)
                            recommendation = {
                                "id": f"product_{product['id']}",
                                "name": product['name'],
                                "brand": product['brand_name'],
                                "price": float(product['price']) if product['price'] else 0.0,
                                "image_url": product['image_url'] or "",
                                "product_url": product['product_url'] or "#",
                                "category": product['category'],
                                "fit_confidence": round(best_rec.overall_fit_score, 2),
                                "recommended_size": best_rec.size_label,
                                "measurements": {dim: f"{scores['garment_measurement']:.1f}\"" for dim, scores in best_rec.dimension_scores.items()},
                                "available_sizes": [sr.size_label for sr in fit_result],
                                "description": product['description'] or f"Recommended based on your measurement profile"
                            }
                            
                            recommendations.append(recommendation)
                            processed_count += 1
                            
                            # Return early if we have enough good recommendations
                            if len(recommendations) >= limit:
                                break
                        
            except Exception as e:
                print(f"Error analyzing product {product['id']}: {str(e)}")
                # Fallback: add product with basic info but no fit analysis (only if we need more)
                if len(recommendations) < limit:
                     recommendation = {
                         "id": f"product_{product['id']}",
                         "name": product['name'],
                         "brand": product['brand_name'],
                         "price": float(product['price']) if product['price'] else 0.0,
                         "image_url": product['image_url'] or "",
                         "product_url": product['product_url'] or "#",
                         "category": product['category'],
                         "fit_confidence": 0.5,
                         "recommended_size": "M",  # Default fallback
                         "measurements": {"chest": "40.0\"", "sleeve": "34.0\""},  # Default measurements
                         "available_sizes": ["XS", "S", "M", "L", "XL"],
                         "description": product['description'] or "Product available for purchase"
                     }
                     recommendations.append(recommendation)

        cur.close()
        conn.close()
        
        # Sort recommendations by fit confidence (best first)
        recommendations.sort(key=lambda x: x['fit_confidence'], reverse=True)
        
        # Limit results
        limited_recommendations = recommendations[:limit]
        
        # Summary logging
        total_products_analyzed = len(products)
        if selected_zone_range:
            print(f"🎯 FIT ZONE FILTERING SUMMARY:")
            print(f"   User: {user_id}, Category: {category}, Fit Zone: {fit_zone}")
            print(f"   Zone Range: {selected_zone_range.get('min', 0):.1f}\" - {selected_zone_range.get('max', 999):.1f}\"")
            print(f"   Products analyzed: {total_products_analyzed}")
            print(f"   Products filtered out: {filtered_count}")
            print(f"   Products included: {len(limited_recommendations)}")
        else:
            print(f"🎯 NO FIT ZONE FILTERING APPLIED - returning {len(limited_recommendations)} products")

        return {
            "recommendations": limited_recommendations,
            "total_count": len(limited_recommendations),
            "has_more": len(recommendations) > limit
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

def extract_product_name_from_url(product_url: str) -> str:
    """
    Extract the actual product name from a product webpage
    Returns the real product name or a fallback if extraction fails
    """
    try:
        # Add headers to mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        response = requests.get(product_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for product name extraction
        product_name_selectors = [
            'h1[data-testid="product-title"]',  # Banana Republic
            'h1.product-title',
            'h1[class*="title"]',
            'h1[class*="product"]',
            'h1',  # J.Crew uses simple h1
            '[data-testid="product-name"]',
            '.product-name',
            '.product-title',
            # J.Crew specific selectors
            'h1[data-testid="product-hero-title"]',
            '.product-hero-title',
            '.product-details h1'
        ]
        
        for selector in product_name_selectors:
            element = soup.select_one(selector)
            if element:
                product_name = element.get_text().strip()
                if product_name and len(product_name) > 3:  # Basic validation
                    return product_name
        
        # Fallback: try to extract from page title
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            # Remove brand name and common suffixes
            title_text = re.sub(r'\|.*$', '', title_text)  # Remove everything after |
            title_text = re.sub(r'-.*$', '', title_text)   # Remove everything after -
            title_text = title_text.strip()
            if title_text and len(title_text) > 3:
                return title_text
        
        # Fallback: extract from URL path
        return extract_product_name_from_url_path(product_url)
        
    except Exception as e:
        print(f"⚠️ Failed to extract product name from {product_url}: {str(e)}")
        return extract_product_name_from_url_path(product_url)

def extract_product_name_from_url_path(product_url: str) -> str:
    """Extract product name from URL path as fallback"""
    try:
        from urllib.parse import urlparse, unquote
        parsed = urlparse(product_url)
        path_parts = parsed.path.strip('/').split('/')
        
        # For J.Crew URLs like: /p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996
        if 'jcrew.com' in product_url.lower():
            # Look for the product name part (usually the last meaningful part before the product code)
            for part in reversed(path_parts):
                if part and not part.isdigit() and len(part) > 3 and not part.isupper():
                    # Decode URL encoding and format nicely
                    name = unquote(part).replace('-', ' ').title()
                    return name
        
        # Generic fallback
        for part in reversed(path_parts):
            if part and not part.isdigit() and len(part) > 3:
                name = unquote(part).replace('-', ' ').title()
                return name
        
        return "Product Name Not Found"
    except:
        return "Product Name Not Found"

def get_brand_placeholder_image(brand_name: str) -> str:
    """Generate a brand-specific placeholder image URL"""
    # Return empty string to let iOS handle placeholder with SF Symbols
    return ""

def extract_product_image_from_url(product_url: str) -> str:
    """
    Extract the main product image from a product webpage
    Returns the image URL or a fallback if extraction fails
    """
    # First check if we have this product cached (for J.Crew)
    if 'jcrew.com' in product_url.lower():
        try:
            async def get_cached_image():
                async with pool.acquire() as conn:
                    result = await conn.fetchrow("""
                        SELECT product_image, product_name 
                        FROM jcrew_product_cache 
                        WHERE product_url = $1
                    """, product_url)
                    return result
            
            import asyncio
            loop = asyncio.new_event_loop()
            cached = loop.run_until_complete(get_cached_image())
            loop.close()
            
            if cached and cached['product_image']:
                print(f"✅ Using cached J.Crew image for: {cached['product_name']}")
                return cached['product_image']
        except Exception as e:
            print(f"Cache lookup failed: {e}")
    
    # If not cached or not J.Crew, try real-time extraction
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(product_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for product image extraction
        image_selectors = [
            # Banana Republic specific
            'img[data-testid="product-image"]',
            'img[class*="product-image"]',
            'img[class*="product-img"]',
            'img[data-testid="hero-image"]',
            # J.Crew specific
            'img[data-testid="product-hero-image"]',
            'img[class*="hero-image"]',
            'img[class*="product-hero"]',
            'img[class*="product-image"]',
            'img[class*="main-image"]',
            # Generic
            'img[class*="main-image"]',
            'img[class*="primary-image"]',
            'img[class*="product"]',
            # Meta tags (often more reliable)
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            'meta[property="og:image:secure_url"]',
            # Any img with product in class or id
            'img[id*="product"]',
            'img[class*="product"]',
            # Look for any image with reasonable dimensions
            'img[width*="300"]',
            'img[height*="400"]',
            'img[width*="400"]',
            'img[height*="300"]'
        ]
        
        for selector in image_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    image_url = element.get('content')
                else:
                    image_url = element.get('src') or element.get('data-src') or element.get('data-lazy-src')
                
                if image_url:
                    # Handle relative URLs
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif image_url.startswith('/'):
                        parsed_url = urlparse(product_url)
                        image_url = f"{parsed_url.scheme}://{parsed_url.netloc}{image_url}"
                    elif not image_url.startswith('http'):
                        parsed_url = urlparse(product_url)
                        image_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{image_url}"
                    
                    # Basic validation - check if it's likely an image
                    if any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                        return image_url
        
        # Fallback: look for any image that might be a product image
        images = soup.find_all('img')
        for img in images:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src and any(keyword in src.lower() for keyword in ['product', 'item', 'main', 'hero', 'image']):
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    parsed_url = urlparse(product_url)
                    src = f"{parsed_url.scheme}://{parsed_url.netloc}{src}"
                elif not src.startswith('http'):
                    parsed_url = urlparse(product_url)
                    src = f"{parsed_url.scheme}://{parsed_url.netloc}/{src}"
                
                if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                    return src
        
        # Return empty string to let iOS handle placeholder
        return ""
        
    except Exception as e:
        print(f"⚠️ Failed to extract product image from {product_url}: {str(e)}")
        # Return empty string to let iOS handle placeholder
        return ""

if __name__ == "__main__":
    import uvicorn
    import os
    # Allow disabling auto-reload to avoid request timeouts during development on device
    reload_env = os.getenv("APP_RELOAD", "1").lower()
    reload_enabled = not (reload_env in ("0", "false", "no"))
    uvicorn.run(
        "app:app",  # Use string format
        host="0.0.0.0",
        port=8006,  # Backend API port
        reload=reload_enabled
    ) 

# Helper functions for try-on flow
async def get_brand_size_options(brand_id: int) -> list:
    """Get available size options for a brand"""
    async with pool.acquire() as conn:
        sizes = await conn.fetch("""
            SELECT DISTINCT sge.size_label,
                CASE sge.size_label
                    WHEN 'XS' THEN 1
                    WHEN 'S' THEN 2
                    WHEN 'M' THEN 3
                    WHEN 'L' THEN 4
                    WHEN 'XL' THEN 5
                    WHEN 'XXL' THEN 6
                    ELSE 99
                END as size_order
            FROM size_guide_entries sge
            JOIN size_guides sg ON sge.size_guide_id = sg.id
            WHERE sg.brand_id = $1
            ORDER BY size_order
        """, brand_id)
        
        return [size['size_label'] for size in sizes]

async def generate_tryon_insights(user_id, brand_id, size_tried, feedback, measurements, feedback_stored):
    """
    AI-powered try-on insights generator
    Analyzes user feedback and gives immediate insights about their preferences
    """
    if not openai_client:
        # Fallback to basic insights if OpenAI not available
        return await generate_basic_tryon_insights(user_id, brand_id, size_tried, feedback, measurements, feedback_stored)
    
    try:
        # Get user's try-on history for context
        async with pool.acquire() as conn:
            # Get brand name
            brand_name = await conn.fetchval("SELECT name FROM brands WHERE id = $1", brand_id)
            
            # Get user's previous try-ons at this brand
            previous_tryons = await conn.fetch("""
                SELECT ug.size_label, ug.fit_feedback, g.product_name,
                       array_agg(ugf.dimension || ':' || fc.feedback_text) as dimension_feedback
                FROM user_garments ug
                JOIN garments g ON ug.garment_id = g.id
                LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
                LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                WHERE ug.user_id = $1 AND g.brand_id = $2 AND ug.owns_garment = false
                GROUP BY ug.id, ug.size_label, ug.fit_feedback, g.product_name
                ORDER BY ug.created_at DESC
                LIMIT 5
            """, int(user_id), brand_id)
            
            # Get user's owned garments for broader context
            owned_garments = await conn.fetch("""
                SELECT ug.size_label, ug.fit_feedback, g.product_name, b.name as brand_name
                FROM user_garments ug
                JOIN garments g ON ug.garment_id = g.id
                JOIN brands b ON g.brand_id = b.id
                WHERE ug.user_id = $1 AND ug.owns_garment = true
                ORDER BY ug.created_at DESC
                LIMIT 10
            """, int(user_id))
            
            # Get product details from cache if available
            product_details = await conn.fetchrow("""
                SELECT product_description, fit_details, product_name
                FROM jcrew_product_cache 
                WHERE product_name ILIKE $1 OR product_name ILIKE '%t-shirt%' OR product_name ILIKE '%tee%'
                ORDER BY created_at DESC
                LIMIT 1
            """, f"%{brand_name}%")

        # Convert feedback numbers to text for AI
        feedback_text = {}
        for dimension, rating in feedback.items():
            if rating is not None:
                feedback_text[dimension] = {
                    1: "Too Tight",
                    2: "Tight but I Like It", 
                    3: "Good Fit",
                    4: "Loose but I Like It",
                    5: "Too Loose"
                }.get(rating, "Good Fit")

        # Create AI prompt
        system_prompt = """You are a clothing fit analyst helping users understand their size and style preferences. 
        Analyze their try-on feedback and give them immediate, actionable insights about what they learned.
        
        Focus on:
        1. What this try-on tells them about their measurements/preferences
        2. Patterns with this brand specifically  
        3. How this compares to their other garments
        4. Practical insights for future shopping
        5. IMPORTANT: If the product has specific features (like "rib trim at neck", "heavyweight cotton", 
           "relaxed fit", "7.4-ounce fabric", etc.), ask the user about those features to learn their 
           style preferences beyond just size. This helps filter future recommendations.
        
        Be conversational, encouraging, and specific. Use emojis sparingly but effectively.
        Keep responses under 250 words and focus on the most valuable insights.
        
        When asking about specific features, phrase it naturally like:
        - "How did you feel about the rib trim at the neck?"
        - "Did you like the heavyweight cotton feel?"
        - "What did you think of the relaxed fit through the shoulders?"
        
        This helps us learn what design elements you prefer, not just sizing."""

        # Build context for the prompt
        context_info = ""
        if previous_tryons:
            context_info += f"\nPrevious {brand_name} try-ons: "
            for tryon in previous_tryons:
                context_info += f"Size {tryon['size_label']} ({tryon['fit_feedback']}), "
        
        if owned_garments:
            context_info += f"\nOwned garments: "
            for garment in owned_garments[:3]:  # Limit to avoid token overflow
                context_info += f"{garment['brand_name']} {garment['size_label']} ({garment['fit_feedback']}), "

        # Include product details if available
        product_info = ""
        if product_details and product_details['product_description']:
            product_info = f"\nProduct Details: {product_details['product_description'][:300]}..."
            print(f"🔍 Found product details: {product_details['product_name']}")
            print(f"📝 Description: {product_details['product_description'][:100]}...")
        else:
            print("❌ No product details found")
        
        user_prompt = f"""
        I just tried on a {brand_name} size {size_tried} and here's my feedback:
        {json.dumps(feedback_text, indent=2)}
        {product_info}
        {context_info}
        
        What insights can you give me about my fit preferences based on this try-on?
        If this product has specific design features, please ask me about them to help learn my style preferences.
        """

        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        ai_insights = response.choices[0].message.content

        # Structure the response
        insights = {
            "summary": ai_insights,
            "ai_generated": True,
            "context_used": {
                "previous_tryons_count": len(previous_tryons),
                "owned_garments_count": len(owned_garments),
                "brand_history": len([t for t in previous_tryons if t]) > 0
            },
            "raw_feedback": feedback_text,
            "confidence": "high" if len(owned_garments) > 3 else "medium"
        }

        print(f"🤖 AI Insights generated for {brand_name} {size_tried}: {ai_insights[:100]}...")
        return insights

    except Exception as e:
        print(f"Error generating AI insights: {str(e)}")
        # Fallback to basic insights
        return await generate_basic_tryon_insights(user_id, brand_id, size_tried, feedback, measurements, feedback_stored)

async def generate_basic_tryon_insights(user_id, brand_id, size_tried, feedback, measurements, feedback_stored):
    """Fallback function for when AI is not available"""
    insights = {
        "summary": "",
        "key_findings": [],
        "measurement_analysis": {},
        "recommendations": [],
        "confidence": "low",
        "ai_generated": False
    }
    
    # Analyze feedback patterns
    tight_areas = [dim for dim, rating in feedback.items() if rating <= 2 and dim != 'overall']
    loose_areas = [dim for dim, rating in feedback.items() if rating >= 4 and dim != 'overall']
    good_areas = [dim for dim, rating in feedback.items() if rating == 3 and dim != 'overall']
    
    # Get brand name
    async with pool.acquire() as conn:
        brand_name = await conn.fetchval("SELECT name FROM brands WHERE id = $1", brand_id)
    
    # Generate summary
    if not tight_areas and not loose_areas:
        insights["summary"] = f"✅ {brand_name} size {size_tried} fits you well! This suggests you're consistently a {size_tried} at {brand_name}."
        insights["confidence"] = "high"
    elif len(tight_areas) == 1 and not loose_areas:
        insights["summary"] = f"🔶 {brand_name} {size_tried} is close - just tight in {tight_areas[0]}. You might prefer {get_next_size_up(size_tried)} at {brand_name} for comfort."
        insights["confidence"] = "medium"
    elif len(loose_areas) == 1 and not tight_areas:
        insights["summary"] = f"🔶 {brand_name} {size_tried} is close - just loose in {loose_areas[0]}. You might prefer {get_next_size_down(size_tried)} at {brand_name} for a fitted look."
        insights["confidence"] = "medium"
    else:
        insights["summary"] = f"⚠️ {brand_name} {size_tried} has mixed fit - this helps us learn your preferences for future recommendations."
        insights["confidence"] = "low"
    
    return insights

def get_next_size_up(size):
    size_map = {'XS': 'S', 'S': 'M', 'M': 'L', 'L': 'XL', 'XL': 'XXL'}
    return size_map.get(size, size)

def get_next_size_down(size):
    size_map = {'S': 'XS', 'M': 'S', 'L': 'M', 'XL': 'L', 'XXL': 'XL'}
    return size_map.get(size, size)

@app.post("/tryon/test-insights")
async def test_ai_insights(request: dict):
    """
    Test endpoint to see AI insights in action
    """
    try:
        user_id = request.get("user_id", "1")
        brand_id = request.get("brand_id", 4)  # J.Crew
        size_tried = request.get("size_tried", "M")
        feedback = request.get("feedback", {
            "chest": 3,
            "neck": 2,
            "sleeve": 4,
            "overall": 3
        })
        
        insights = await generate_tryon_insights(
            user_id, brand_id, size_tried, feedback, None, []
        )
        
        return {
            "status": "success",
            "insights": insights,
            "test_data": {
                "user_id": user_id,
                "brand_id": brand_id,
                "size_tried": size_tried,
                "feedback": feedback
            }
        }
        
    except Exception as e:
        print(f"Error in test insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))