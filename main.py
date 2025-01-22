from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Database connection configuration
DB_HOST = "localhost"
DB_NAME = "v10_app"
DB_USER = "v10_user"
DB_PASSWORD = "securepassword"

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Sies!"}

from pydantic import BaseModel, validator

# Define a User model for validation
class User(BaseModel):
    email: str
    password: str
    name: str
    
    @validator('password')
    def password_length(cls, v):
        if len(v) < 4:
            raise HTTPException(status_code=400, detail="Password must be at least 4 characters long")
        return v

# Endpoint for user registration
@app.post("/register")
def register(user: User):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if email already exists
        cur.execute("SELECT * FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Insert the user data into the database
        cur.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (%s, %s, %s) RETURNING id",
            (user.email, user.password, user.name)
        )
        new_user_id = cur.fetchone()['id']
        conn.commit()
        
        return {
            "message": f"User {user.name} registered successfully!",
            "user_id": new_user_id
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

# Create the uniqlo_garments table if it doesn't exist
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uniqlo_garments (
                id VARCHAR(50) PRIMARY KEY,  -- SKU
                product_code VARCHAR(50) NOT NULL,
                name VARCHAR(255) NOT NULL,
                size VARCHAR(10) NOT NULL,
                color VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(50) NOT NULL,
                subcategory VARCHAR(50) NOT NULL,
                materials JSONB,  -- Store materials as JSON
                measurements JSONB,  -- Store measurements as JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert sample data (the sweater from the image)
        cur.execute("""
            INSERT INTO uniqlo_garments (
                id, product_code, name, size, color, price, 
                category, subcategory, materials, measurements
            ) VALUES (
                'S202-4575',
                'HT0018FT-US',
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
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# Call create_tables when the app starts
@app.on_event("startup")
async def startup_event():
    create_tables()

# Add endpoint to fetch garment details
@app.get("/garment/{sku}")
def get_garment(sku: str):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM uniqlo_garments WHERE id = %s", (sku,))
        garment = cur.fetchone()
        
        if not garment:
            raise HTTPException(status_code=404, detail="Garment not found")
            
        return garment
    finally:
        cur.close()
        conn.close()

class ExtractedGarmentInfo(BaseModel):
    productCode: str | None
    name: str | None
    size: str | None
    color: str | None
    materials: dict[str, int]
    price: float | None
    measurements: dict[str, str]
    rawText: str

@app.post("/process_garment")
async def process_garment(info: ExtractedGarmentInfo):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Generate a unique ID (using product code or a combination of fields)
        garment_id = info.productCode or "UNQ-" + info.name.replace(" ", "-")[:20]
        
        # Try to find existing garment first
        cur.execute("SELECT * FROM uniqlo_garments WHERE id = %s OR product_code = %s", 
                   (garment_id, info.productCode))
        existing = cur.fetchone()
        
        if existing:
            # Return existing garment
            return {
                "id": existing["id"],
                "name": existing["name"],
                "brand": "UNIQLO",
                "size": existing["size"],
                "category": existing["category"],
                "subcategory": existing["subcategory"],
                "color": existing["color"],
                "price": float(existing["price"]),
                "imageUrl": f"https://uniqlo.com/images/{existing['id']}.jpg",
                "productUrl": f"https://uniqlo.com/products/{existing['id']}"
            }
        
        # Create new garment entry
        category = "Sweaters" if "SWEATER" in info.name.upper() else "Unknown"
        subcategory = "Crew Neck" if "CREW NECK" in info.name.upper() else "Unknown"
        
        # Insert new garment
        cur.execute("""
            INSERT INTO uniqlo_garments (
                id, product_code, name, size, color, price, 
                category, subcategory, materials, measurements
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
            RETURNING *
        """, (
            garment_id,
            info.productCode,
            info.name,
            info.size,
            info.color,
            info.price,
            category,
            subcategory,
            json.dumps(info.materials),
            json.dumps(info.measurements)
        ))
        
        new_garment = cur.fetchone()
        conn.commit()
        
        # Return formatted garment info
        return {
            "id": new_garment["id"],
            "name": new_garment["name"],
            "brand": "UNIQLO",
            "size": new_garment["size"],
            "category": new_garment["category"],
            "subcategory": new_garment["subcategory"],
            "color": new_garment["color"],
            "price": float(new_garment["price"]),
            "imageUrl": f"https://uniqlo.com/images/{new_garment['id']}.jpg",
            "productUrl": f"https://uniqlo.com/products/{new_garment['id']}"
        }
        
    except Exception as e:
        print(f"Error processing garment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
