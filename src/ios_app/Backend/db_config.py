#!/usr/bin/env python3
"""
Database configuration for V10 backend
Uses environment variables set in Render deployment
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration - using environment variables from Render
DB_CONFIG = {
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

# For psql commands - export these environment variables
PSQL_ENV = {
    "PGPASSWORD": DB_CONFIG["password"],
    "PGHOST": DB_CONFIG["host"],
    "PGPORT": str(DB_CONFIG["port"]),
    "PGUSER": DB_CONFIG["user"],
    "PGDATABASE": DB_CONFIG["database"]
}

# Connection string for SQLAlchemy
def get_database_url():
    return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

if __name__ == "__main__":
    print(f"Database configuration loaded")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Port: {DB_CONFIG['port']}")
