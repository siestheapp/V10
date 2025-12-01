#!/usr/bin/env python3
"""
Simple database configuration for V10 project
This provides consistent database access for both Python scripts and terminal commands
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration - values must come from environment (no hardcoded defaults)
DB_CONFIG = {
    "database": os.getenv("DB_NAME", ""),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", ""),
    "port": os.getenv("DB_PORT", ""),
}


def validate_db_config() -> None:
    """Ensure every DB setting is present before code tries to connect."""
    missing = [key for key, value in DB_CONFIG.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
        )


validate_db_config()

# For psql commands - export these environment variables
PSQL_ENV = {
    "PGPASSWORD": DB_CONFIG["password"],
    "PGHOST": DB_CONFIG["host"],
    "PGPORT": str(DB_CONFIG["port"]),
    "PGUSER": DB_CONFIG["user"],
    "PGDATABASE": DB_CONFIG["database"]
}

def get_psql_command():
    """Generate the psql command with proper environment variables"""
    env_vars = " ".join([f"{k}={v}" for k, v in PSQL_ENV.items()])
    return f"{env_vars} psql"

def print_connection_info():
    """Print connection information for debugging"""
    print("🔌 Database Connection Info:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Port: {DB_CONFIG['port']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print(f"   Password: {'*' * len(DB_CONFIG['password'])}")
    print()
    print("📝 For psql commands, use:")
    print(f"   {get_psql_command()} -c \"YOUR_SQL_COMMAND\"")
    print()

if __name__ == "__main__":
    print_connection_info()

