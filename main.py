

from fastapi import FastAPI

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

from pydantic import BaseModel

# Define a User model for validation
class User(BaseModel):
    email: str
    password: str
    name: str

# Endpoint for user registration
@app.post("/register")
def register(user: User):
    conn = get_db_connection()
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
