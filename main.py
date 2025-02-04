from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from urllib.parse import urlparse
from statistics import mean
from typing import List, Optional

# Database connection
DB_CONFIG = {
    "dbname": "v10_app",
    "user": "v10_user",
    "password": "securepassword",
    "host": "localhost"
}

def get_db():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# API Models
class GarmentInfo(BaseModel):
    productCode: str
    name: str | None = None
    size: str | None = None
    color: str | None = None
    price: float | None = None
    materials: dict | None = None
    measurements: dict | None = None
    rawText: str | None = None

class GarmentRequest(BaseModel):
    product_code: str
    scanned_price: float | None = None
    scanned_size: str | None = None

class MeasurementRange(BaseModel):
    min: float
    max: float
    confidence: float

class UserMeasurement(BaseModel):
    brand: str
    garment_name: str
    measurement_type: str  # e.g., "chest", "sleeve_length"
    value_min: float
    value_max: float
    size: str
    owns_garment: bool
    fit_type: Optional[str]  # "tight", "regular", "relaxed"
    garment_type: Optional[str]
    feedback: Optional[str]

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Sies!"}

from pydantic import BaseModel

# Define a User model for validation
class User(BaseModel):
    email: str
    password: str
    name: str

# Endpoint for user registration
@app.post("/register")
def register(user: User):
    conn = get_db()
    cur = conn.cursor()

    try:
        # Insert the user data into the database
        cur.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (%s, %s, %s)",
            (user.email, user.password, user.name)
        )
        conn.commit()
        return {"message": f"User {user.name} registered successfully!"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def is_valid_uniqlo_url(url: str) -> bool:
    try:
        # Check URL format
        parsed = urlparse(url)
        
        # Basic validation
        if not all([parsed.scheme, parsed.netloc]):
            return False
            
        # Uniqlo-specific validation
        if not parsed.netloc.endswith("uniqlo.com"):
            return False
            
        # Product code validation
        if not "/products/E" in parsed.path:
            return False
            
        return True
    except:
        return False

@app.post("/process_garment")
async def process_garment(request: GarmentRequest):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # First check if this is an alternate code
        cur.execute("""
            SELECT primary_code 
            FROM product_codes 
            WHERE alternate_code = %s
        """, (request.product_code,))
        
        result = cur.fetchone()
        product_code = result['primary_code'] if result else request.product_code
        
        # Then get product info using the primary code
        cur.execute("""
            SELECT p.*, m.measurements 
            FROM products p 
            LEFT JOIN measurements m ON p.product_code = m.product_code
            WHERE p.product_code = %s
        """, (product_code,))
        
        product = cur.fetchone()
        
        if product:
            # Record the scan in history
            print(f"Recording scan: {request.product_code}, size: {request.scanned_size}")  # Debug
            cur.execute("""
                INSERT INTO scan_history 
                (product_code, scanned_size, scanned_price)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (request.product_code, request.scanned_size, request.scanned_price))
            scan_id = cur.fetchone()["id"]
            print(f"Created scan history entry: {scan_id}")  # Debug
            conn.commit()
            
            measurements = product["measurements"]
            # Only return measurements for scanned size if available
            if request.scanned_size and measurements["sizes"].get(request.scanned_size):
                size_measurements = {
                    "units": measurements["units"],
                    "sizes": {
                        request.scanned_size: measurements["sizes"][request.scanned_size]
                    }
                }
            else:
                size_measurements = measurements  # Fallback to all sizes if size not found
                
            # Generate URL if not stored
            product_url = product["product_url"]
            if not product_url:
                product_url = f"https://www.uniqlo.com/us/en/products/E{request.product_code}-000"
                # Validate before storing
                if is_valid_uniqlo_url(product_url):
                    cur.execute("""
                        UPDATE products 
                        SET product_url = %s 
                        WHERE product_code = %s
                    """, (product_url, request.product_code))
                    conn.commit()
                else:
                    print(f"Warning: Generated invalid URL: {product_url}")
            
            return {
                "id": product["product_code"],
                "name": product["name"],
                "category": product["category"],
                "subcategory": product["subcategory"],
                "price": request.scanned_price,
                "scanned_size": request.scanned_size,
                "measurements": size_measurements,
                "imageUrl": product["image_url"],
                "productUrl": product_url
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found")
            
    finally:
        cur.close()
        conn.close()

def create_tables():
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Drop old table
        cur.execute("DROP TABLE IF EXISTS uniqlo_garments CASCADE")
        
        # Create new products table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_code VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                category VARCHAR NOT NULL,
                subcategory VARCHAR,
                brand VARCHAR,
                image_url VARCHAR,
                product_url VARCHAR
            )
        """)
        
        # Create measurements table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                product_code VARCHAR PRIMARY KEY,
                measurements JSONB NOT NULL,
                FOREIGN KEY (product_code) REFERENCES products(product_code)
            )
        """)
        
        # Create click tracking table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS click_tracking (
                id SERIAL PRIMARY KEY,
                product_code VARCHAR NOT NULL,
                user_id VARCHAR,
                scanned_size VARCHAR,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_code) REFERENCES products(product_code)
            )
        """)
        
        # Create scan history table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR,
                product_code VARCHAR NOT NULL,
                scanned_size VARCHAR,
                scanned_price DECIMAL(10,2),
                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_code) REFERENCES products(product_code)
            )
        """)
        
        # Insert sample product
        cur.execute("""
            INSERT INTO products (
                product_code, name, category, subcategory, brand, image_url
            ) VALUES (
                '475296',
                '3D KNIT CREW NECK SWEATER',
                'Sweaters',
                'Crew Neck',
                'Uniqlo',
                'https://image.uniqlo.com/UQ/ST3/us/imagesgoods/475296/item/goods_09_475296.jpg'
            ) ON CONFLICT (product_code) DO NOTHING
        """)
        
        # Insert sample measurements
        cur.execute("""
            INSERT INTO measurements (product_code, measurements) VALUES (
                '475296',
                '{
                    "units": "inches",
                    "sizes": {
                        "XS": {"body_length": "25", "body_width": "17", "sleeve_length": "23"},
                        "S": {"body_length": "26", "body_width": "18", "sleeve_length": "24"},
                        "M": {"body_length": "27", "body_width": "19", "sleeve_length": "25"},
                        "L": {"body_length": "28", "body_width": "20", "sleeve_length": "26"},
                        "XL": {"body_length": "29", "body_width": "21", "sleeve_length": "27"}
                    }
                }'::jsonb
            ) ON CONFLICT (product_code) DO NOTHING
        """)
        
        # Create product_codes table for alternate codes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_codes (
                alternate_code VARCHAR PRIMARY KEY,
                primary_code VARCHAR REFERENCES products(product_code)
            )
        """)
        
        # Add TSIN column to products
        cur.execute("""
            ALTER TABLE products 
            ADD COLUMN IF NOT EXISTS tsin VARCHAR(20)
        """)
        
        # Create TSIN generation function
        cur.execute("""
            CREATE OR REPLACE FUNCTION generate_tsin() 
            RETURNS trigger AS $$
            BEGIN
                WITH item_count AS (
                    SELECT COUNT(*) + 1 as next_num 
                    FROM products 
                    WHERE brand = NEW.brand 
                    AND department = NEW.department
                )
                SELECT INTO NEW.tsin
                    CASE NEW.brand
                        WHEN 'Uniqlo' THEN 'U'
                    END ||
                    CASE NEW.department
                        WHEN 'Mens' THEN 'M'
                        WHEN 'Womens' THEN 'W'
                    END ||
                    CASE 
                        WHEN NEW.category IN ('Sweaters', 'T-Shirts', 'Shirts', 'Tops') THEN 'T'
                    END ||
                    COALESCE((SELECT next_num FROM item_count), 1)::text;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Create trigger for TSIN
        cur.execute("""
            DROP TRIGGER IF EXISTS set_tsin ON products;
            CREATE TRIGGER set_tsin
                BEFORE INSERT ON products
                FOR EACH ROW
                EXECUTE FUNCTION generate_tsin();
        """)
        
        # Update existing product with TSIN
        cur.execute("""
            UPDATE products 
            SET tsin = 'UMT1'
            WHERE product_code = '475296';
        """)
        
        conn.commit()
        print("Tables created successfully")
        
    finally:
        cur.close()
        conn.close()

# Call this when app starts
create_tables()

@app.post("/track_click")
async def track_click(product_code: str, user_id: str | None = None, scanned_size: str | None = None):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO click_tracking 
            (product_code, user_id, scanned_size)
            VALUES (%s, %s, %s)
        """, (product_code, user_id, scanned_size))
        conn.commit()
        return {"status": "success"}
    finally:
        cur.close()
        conn.close()

@app.get("/scan_history")
async def get_scan_history(user_id: str | None = None, limit: int = 50):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                h.id,
                h.product_code as "productCode",
                h.scanned_size as "scannedSize",
                h.scanned_price as "scannedPrice",
                h.scanned_at as "scannedAt",
                p.name,
                p.category,
                p.brand,
                p.image_url as "imageUrl",
                p.product_url as "productUrl"
            FROM scan_history h
            JOIN products p ON h.product_code = p.product_code
            ORDER BY h.scanned_at DESC
            LIMIT %s
        """, (limit,))
        
        history = cur.fetchall()
        print(f"Found {len(history)} history items")  # Debug print
        print(f"First item: {history[0] if history else None}")  # Debug print
        return history
    finally:
        cur.close()
        conn.close()

def standardize_sleeve_measurement(value: float, measurement_name: str) -> dict:
    """Standardize sleeve measurements to CBL format"""
    
    # If value is under 30, assume it's SWL and needs conversion
    is_likely_swl = value < 30
    
    # Get the mapping
    mapping = conn.execute("""
        SELECT 
            mt.name as standard_name,
            mm.measurement_method,
            mm.conversion_factor
        FROM measurement_mappings mm
        JOIN measurement_types mt ON mm.measurement_type_id = mt.id
        WHERE mm.original_name ILIKE $1
    """, measurement_name).fetchone()
    
    if mapping:
        if mapping.measurement_method == 'shoulder_to_wrist' or is_likely_swl:
            # Convert to CBL
            converted_value = value * 1.18  # Approximate conversion factor
            return {
                "standard_value": converted_value,
                "original_value": value,
                "measurement_method": "shoulder_to_wrist",
                "converted_to_cbl": True
            }
        else:
            # Already CBL
            return {
                "standard_value": value,
                "original_value": value,
                "measurement_method": "center_back",
                "converted_to_cbl": False
            }

@app.get("/user/{user_id}/measurements")
async def get_user_measurements(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Get all chest measurements for user
        cur.execute("""
            SELECT 
                m.brand_name,
                m.garment_name,
                m.value,
                m.original_value,
                m.size,
                m.owns_garment,
                f.fit_type,
                f.garment_type,
                f.custom_feedback
            FROM user_measurements m
            LEFT JOIN fit_feedback f ON 
                m.brand_name = f.brand 
                AND m.garment_name = f.garment_name
                AND m.size = f.size
            WHERE m.user_id = %s
            AND m.measurement_type_id = (
                SELECT id FROM measurement_types WHERE name = 'chest_circumference'
            )
        """, (user_id,))
        
        measurements = cur.fetchall()
        
        # Calculate preferred range
        def calculate_range(measurements: List[dict]) -> MeasurementRange:
            values = []
            for m in measurements:
                # Convert any half measurements
                value = m['value'] * 2 if m['original_name'].lower().startswith('half') else m['value']
                
                # Weight the measurement based on fit feedback
                confidence = 1.0
                if m['fit_type'] == 'tight':
                    confidence = 0.7  # Less weight for tight fits
                elif m['fit_type'] == 'relaxed':
                    confidence = 0.8  # Less weight for relaxed fits
                
                values.append({
                    'value': value,
                    'confidence': confidence
                })
            
            # Calculate weighted average
            weighted_values = [v['value'] * v['confidence'] for v in values]
            weights = [v['confidence'] for v in values]
            avg = sum(weighted_values) / sum(weights)
            
            # Calculate range (±5% from weighted average)
            return MeasurementRange(
                min=avg * 0.95,
                max=avg * 1.05,
                confidence=mean([v['confidence'] for v in values])
            )
        
        preferred_range = calculate_range(measurements)
        
        return {
            "measurement_type": "chest",
            "preferred_range": preferred_range,
            "measurements": [
                {
                    "brand": m['brand_name'],
                    "garment_name": m['garment_name'],
                    "value_min": m['value'],
                    "value_max": m['value'],
                    "size": m['size'],
                    "owns_garment": m['owns_garment'],
                    "fit_type": m['fit_type'],
                    "garment_type": m['garment_type'],
                    "feedback": m['custom_feedback']
                }
                for m in measurements
            ]
        }
        
    finally:
        cur.close()
        conn.close()
