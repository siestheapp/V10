from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import json

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

@app.post("/process_garment")
async def process_garment(request: GarmentRequest):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Get product info
        cur.execute("""
            SELECT p.*, m.measurements 
            FROM products p 
            LEFT JOIN measurements m ON p.product_code = m.product_code
            WHERE p.product_code = %s
        """, (request.product_code,))
        
        product = cur.fetchone()
        
        if product:
            return {
                "id": product["product_code"],
                "name": product["name"],
                "category": product["category"],
                "subcategory": product["subcategory"],
                "price": request.scanned_price,  # Use scanned price
                "measurements": product["measurements"],
                "imageUrl": product["image_url"],
                "productUrl": product["product_url"]
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
        # Create tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uniqlo_garments (
                id VARCHAR PRIMARY KEY,
                product_code VARCHAR,
                name VARCHAR NOT NULL,
                size VARCHAR NOT NULL,
                color VARCHAR NOT NULL,
                price DECIMAL(10,2),
                category VARCHAR,
                subcategory VARCHAR,
                materials JSONB,
                measurements JSONB
            )
        """)
        
        # Insert sample data (the sweater from the image)
        cur.execute("""
            INSERT INTO uniqlo_garments (
                id, product_code, name, size, color, price, 
                category, subcategory, materials, measurements
            ) VALUES (
                '475296',
                'HT00189FT-US',
                '3D KNIT CREW NECK SWEATER',
                'L',
                '09 Black',
                49.90,
                'Sweaters',
                'Crew Neck',
                '{"ACRYLIC": 60, "COTTON": 40}'::jsonb,
                '{"chest": "41-44"}'::jsonb
            ) ON CONFLICT (id) DO NOTHING
        """)
        
        conn.commit()
        print("Tables created successfully")
        
    finally:
        cur.close()
        conn.close()

# Call this when app starts
create_tables()
