"""
Mock database configuration for contractor testing
Use this for local testing only
"""

# Mock configuration - contractor should use their own local database
DB_CONFIG = {
    "database": "v10_test",
    "user": "postgres",
    "password": "localtest123",  # Change this for your local setup
    "host": "localhost",
    "port": "5432"
}

print("⚠️ Using mock db_config - contractor should set up local test database")
