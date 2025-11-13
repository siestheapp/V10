#!/usr/bin/env python3
"""
Complete SQL Dump Script for tailor3 Database
Exports all tables, data, and schema with timestamp
"""

import psycopg2
import os
from datetime import datetime
import subprocess
import sys

# Database configuration - Supabase tailor3
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def get_timestamp():
    """Get current timestamp for filename"""
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def create_sql_dump():
    """Create a complete SQL dump of the database"""
    timestamp = get_timestamp()
    filename = f"tailor3_dump_{timestamp}.sql"
    
    # Create dumps directory if it doesn't exist
    dumps_dir = "database_dumps"
    os.makedirs(dumps_dir, exist_ok=True)
    
    filepath = os.path.join(dumps_dir, filename)
    
    print(f"Creating SQL dump: {filepath}")
    print("This may take a few minutes...")
    
    # Use pg_dump to create the SQL dump
    # Note: We'll use psql to connect and export since we're using Supabase pooled connection
    try:
        # Connect to database and get all tables
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        # Create the SQL dump file
        with open(filepath, 'w') as f:
            f.write(f"-- V10 tailor3 Database Dump\n")
            f.write(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Database: tailor3 (Supabase)\n\n")
            
            # Connect and dump each table
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            for table in tables:
                print(f"Dumping table: {table}")
                
                # Get table schema
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                
                # Write table creation
                f.write(f"\n-- Table: {table}\n")
                f.write(f"DROP TABLE IF EXISTS {table} CASCADE;\n")
                f.write(f"CREATE TABLE {table} (\n")
                
                column_definitions = []
                for col in columns:
                    col_name, data_type, nullable, default_val = col
                    nullable_str = "" if nullable == "YES" else " NOT NULL"
                    default_str = f" DEFAULT {default_val}" if default_val else ""
                    column_definitions.append(f"    {col_name} {data_type}{nullable_str}{default_str}")
                
                f.write(",\n".join(column_definitions))
                f.write("\n);\n\n")
                
                # Get and write data
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                if rows:
                    f.write(f"-- Data for table: {table}\n")
                    f.write(f"INSERT INTO {table} VALUES\n")
                    
                    insert_values = []
                    for row in rows:
                        # Handle NULL values and string escaping
                        formatted_row = []
                        for val in row:
                            if val is None:
                                formatted_row.append("NULL")
                            elif isinstance(val, str):
                                # Escape single quotes
                                escaped_val = val.replace("'", "''")
                                formatted_row.append(f"'{escaped_val}'")
                            elif isinstance(val, datetime):
                                formatted_row.append(f"'{val.isoformat()}'")
                            else:
                                formatted_row.append(str(val))
                        
                        insert_values.append(f"({', '.join(formatted_row)})")
                    
                    # Write in batches to avoid memory issues
                    batch_size = 100
                    for i in range(0, len(insert_values), batch_size):
                        batch = insert_values[i:i + batch_size]
                        f.write(",\n".join(batch))
                        if i + batch_size < len(insert_values):
                            f.write(",\n")
                        else:
                            f.write(";\n")
                    f.write("\n")
            
            cursor.close()
            conn.close()
        
        print(f"✅ SQL dump completed successfully!")
        print(f"📁 File saved to: {filepath}")
        print(f"📊 Total tables dumped: {len(tables)}")
        
        # Get file size
        file_size = os.path.getsize(filepath)
        print(f"📏 File size: {file_size / 1024:.1f} KB")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Error creating SQL dump: {str(e)}")
        return None

def create_schema_only_dump():
    """Create a schema-only dump (structure without data)"""
    timestamp = get_timestamp()
    filename = f"tailor3_schema_{timestamp}.sql"
    
    dumps_dir = "database_dumps"
    os.makedirs(dumps_dir, exist_ok=True)
    
    filepath = os.path.join(dumps_dir, filename)
    
    print(f"Creating schema-only dump: {filepath}")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        with open(filepath, 'w') as f:
            f.write(f"-- V10 tailor3 Database Schema Dump\n")
            f.write(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Database: tailor3 (Supabase)\n\n")
            
            for table in tables:
                print(f"Dumping schema for table: {table}")
                
                # Get table schema
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                
                f.write(f"\n-- Table: {table}\n")
                f.write(f"DROP TABLE IF EXISTS {table} CASCADE;\n")
                f.write(f"CREATE TABLE {table} (\n")
                
                column_definitions = []
                for col in columns:
                    col_name, data_type, nullable, default_val = col
                    nullable_str = "" if nullable == "YES" else " NOT NULL"
                    default_str = f" DEFAULT {default_val}" if default_val else ""
                    column_definitions.append(f"    {col_name} {data_type}{nullable_str}{default_str}")
                
                f.write(",\n".join(column_definitions))
                f.write("\n);\n\n")
        
        cursor.close()
        conn.close()
        
        print(f"✅ Schema dump completed successfully!")
        print(f"📁 File saved to: {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Error creating schema dump: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 V10 tailor3 Database Dump Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--schema-only":
        create_schema_only_dump()
    else:
        create_sql_dump()
    
    print("\n✨ Done!") 