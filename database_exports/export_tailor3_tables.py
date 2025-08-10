#!/usr/bin/env python3
"""
Export script for tailor3 database tables
Exports all specified tables with complete data and column headers for future restoration
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import csv
import json
import os
from datetime import datetime
import sys

# Database configuration
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx", 
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

# Tables to export
TABLES_TO_EXPORT = [
    'size_guides',
    'size_guide_entries', 
    'garment_guides',
    'garment_guide_entries',
    'products',
    'user_garments',
    'admin_activity_log',
    'audit_log',
    'brands',
    'garment_measurement_feedback',
    'user_garment_feedback'
]

def get_db_connection():
    """Get a connection to the database"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def export_table_to_csv(table_name, output_dir):
    """Export a table to CSV format with all data and headers"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get table structure first
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """)
        
        columns_info = cur.fetchall()
        if not columns_info:
            print(f"⚠️  Table '{table_name}' not found or has no columns")
            return False
            
        print(f"📋 Table '{table_name}' has {len(columns_info)} columns")
        
        # Get all data from the table
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        
        print(f"📊 Table '{table_name}' has {len(rows)} rows")
        
        # Write to CSV
        csv_file = os.path.join(output_dir, f"{table_name}.csv")
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            if rows:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            else:
                # Even if no data, write headers from column info
                fieldnames = [col['column_name'] for col in columns_info]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        
        print(f"✅ Exported {table_name} to {csv_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting table '{table_name}': {e}")
        return False
    finally:
        cur.close()
        conn.close()

def export_table_to_sql(table_name, output_dir):
    """Export a table to SQL format with CREATE TABLE and INSERT statements"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get table structure
        cur.execute(f"""
            SELECT column_name, data_type, character_maximum_length, 
                   is_nullable, column_default, ordinal_position
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """)
        
        columns_info = cur.fetchall()
        if not columns_info:
            print(f"⚠️  Table '{table_name}' not found")
            return False
        
        # Get constraints and indexes
        cur.execute(f"""
            SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = '{table_name}'
        """)
        
        constraints = cur.fetchall()
        
        # Get all data
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        
        # Write SQL file
        sql_file = os.path.join(output_dir, f"{table_name}.sql")
        with open(sql_file, 'w', encoding='utf-8') as sqlfile:
            # Write header comment
            sqlfile.write(f"-- Export of table '{table_name}' from tailor3 database\n")
            sqlfile.write(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            sqlfile.write(f"-- Total rows: {len(rows)}\n\n")
            
            # Write DROP TABLE statement
            sqlfile.write(f"DROP TABLE IF EXISTS {table_name} CASCADE;\n\n")
            
            # Write CREATE TABLE statement
            sqlfile.write(f"CREATE TABLE {table_name} (\n")
            
            column_defs = []
            for col in columns_info:
                col_def = f"    {col['column_name']} {col['data_type']}"
                
                if col['character_maximum_length']:
                    col_def += f"({col['character_maximum_length']})"
                
                if col['is_nullable'] == 'NO':
                    col_def += " NOT NULL"
                
                if col['column_default']:
                    col_def += f" DEFAULT {col['column_default']}"
                    
                column_defs.append(col_def)
            
            sqlfile.write(",\n".join(column_defs))
            sqlfile.write("\n);\n\n")
            
            # Write INSERT statements
            if rows:
                column_names = list(rows[0].keys())
                sqlfile.write(f"-- Data for table '{table_name}'\n")
                
                for row in rows:
                    values = []
                    for col_name in column_names:
                        value = row[col_name]
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, str):
                            # Escape single quotes
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        elif isinstance(value, (dict, list)):
                            # Handle JSON data
                            json_str = json.dumps(value).replace("'", "''")
                            values.append(f"'{json_str}'")
                        else:
                            values.append(str(value))
                    
                    values_str = ", ".join(values)
                    columns_str = ", ".join(column_names)
                    sqlfile.write(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});\n")
            
            sqlfile.write(f"\n-- End of export for table '{table_name}'\n")
        
        print(f"✅ Exported {table_name} to {sql_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting table '{table_name}' to SQL: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def export_table_metadata(table_name, output_dir):
    """Export table metadata including structure, constraints, and indexes"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        metadata = {
            'table_name': table_name,
            'export_date': datetime.now().isoformat(),
            'columns': [],
            'constraints': [],
            'indexes': []
        }
        
        # Get column information
        cur.execute(f"""
            SELECT column_name, data_type, character_maximum_length,
                   is_nullable, column_default, ordinal_position
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """)
        
        metadata['columns'] = cur.fetchall()
        
        # Get constraints
        cur.execute(f"""
            SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = '{table_name}'
        """)
        
        metadata['constraints'] = cur.fetchall()
        
        # Get row count
        cur.execute(f"SELECT COUNT(*) as row_count FROM {table_name}")
        result = cur.fetchone()
        metadata['row_count'] = result['row_count'] if result else 0
        
        # Write metadata to JSON
        metadata_file = os.path.join(output_dir, f"{table_name}_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(metadata, jsonfile, indent=2, default=str)
        
        print(f"📋 Exported metadata for {table_name} to {metadata_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting metadata for '{table_name}': {e}")
        return False
    finally:
        cur.close()
        conn.close()

def main():
    """Main export function"""
    print("🚀 Starting tailor3 database export...")
    print(f"📅 Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create timestamped output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f"tailor3_export_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    
    # Test database connection
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"🔗 Connected to: {version[0]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    
    # Export each table
    successful_exports = 0
    failed_exports = 0
    
    for table_name in TABLES_TO_EXPORT:
        print(f"\n📊 Exporting table: {table_name}")
        
        # Export to CSV
        if export_table_to_csv(table_name, output_dir):
            successful_exports += 1
        else:
            failed_exports += 1
            continue
            
        # Export to SQL
        export_table_to_sql(table_name, output_dir)
        
        # Export metadata
        export_table_metadata(table_name, output_dir)
    
    # Create summary report
    summary = {
        'export_date': datetime.now().isoformat(),
        'database_config': {k: v for k, v in DB_CONFIG.items() if k != 'password'},
        'tables_exported': TABLES_TO_EXPORT,
        'successful_exports': successful_exports,
        'failed_exports': failed_exports,
        'output_directory': output_dir
    }
    
    summary_file = os.path.join(output_dir, 'export_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(summary, jsonfile, indent=2)
    
    print(f"\n📋 Export Summary:")
    print(f"   ✅ Successful: {successful_exports}")
    print(f"   ❌ Failed: {failed_exports}")
    print(f"   📁 Output: {output_dir}")
    print(f"   📄 Summary: {summary_file}")
    
    if failed_exports == 0:
        print("\n🎉 All tables exported successfully!")
    else:
        print(f"\n⚠️  {failed_exports} table(s) failed to export. Check the output above for details.")

if __name__ == "__main__":
    main()
