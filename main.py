from fastapi import FastAPI, HTTPException

import psycopg2
from psycopg2.extras import RealDictCursor

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
