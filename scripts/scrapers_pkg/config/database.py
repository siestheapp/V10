"""Database configuration for scrapers."""

import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self):
        self.config = {
            "host": os.getenv("DB_HOST", "aws-1-us-east-1.pooler.supabase.com"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "postgres"),
            "user": os.getenv("DB_USER", "fs_core_rw"),
            "password": os.getenv("DB_PASSWORD", "CHANGE_ME"),
        }
    
    def get_connection(self):
        """Get a database connection with RealDictCursor."""
        return psycopg2.connect(
            **self.config,
            cursor_factory=RealDictCursor
        )
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] == 1
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

# Global database config instance
db_config = DatabaseConfig()
