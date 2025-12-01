#!/usr/bin/env python3
"""
Example script showing how to use the DatabaseChangeLogger in future operations
This template can be copied for any future database modifications
"""

from database_change_logger import DatabaseChangeLogger, DB_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor

def example_database_operation():
    """Example of how to log database changes in future scripts"""
    
    # Initialize logger
    logger = DatabaseChangeLogger(DB_CONFIG)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.log_change(
            operation="STARTED",
            table="OPERATION",
            details="Example database operation started"
        )
        
        # Example: Adding a new brand
        # Before adding, log what we're about to do
        logger.log_change(
            operation="PLANNING",
            table="brands",
            details="About to add new brand: Example Brand"
        )
        
        # Simulate the database operation (commented out)
        # cur.execute("INSERT INTO brands (name, region) VALUES (%s, %s) RETURNING id", 
        #            ("Example Brand", "US"))
        # new_brand = cur.fetchone()
        
        # Log the successful insertion
        # logger.log_insert(
        #     table="brands",
        #     record_data=f"Example Brand (ID: {new_brand['id']}) - US region",
        #     description="Added new brand for testing"
        # )
        
        # Example: Updating a record
        # Get current data first
        # cur.execute("SELECT * FROM brands WHERE id = %s", (new_brand['id'],))
        # old_data = cur.fetchone()
        
        # Make the update
        # cur.execute("UPDATE brands SET notes = %s WHERE id = %s", 
        #            ("This is an example brand", new_brand['id']))
        
        # Log the update
        # logger.log_update(
        #     table="brands",
        #     old_data=f"Notes: {old_data['notes']}",
        #     new_data="Notes: This is an example brand",
        #     description="Added notes to example brand"
        # )
        
        # Commit changes
        # conn.commit()
        
        logger.log_session_end("Example operation completed successfully")
        
        cur.close()
        conn.close()
        
        print(f"✅ Example logged to: {logger.log_file}")
        
    except Exception as e:
        logger.log_change(
            operation="ERROR",
            table="SYSTEM",
            details=f"Operation failed: {e}"
        )
        if 'conn' in locals():
            conn.rollback()
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    example_database_operation()
