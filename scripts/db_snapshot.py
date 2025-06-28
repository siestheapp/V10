#!/usr/bin/env python3
"""
Database Snapshot Script for V10
Exports current database state for AI analysis and recommendations
"""

import psycopg2
import json
import os
from datetime import datetime
from typing import Dict, List, Any

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'tailor2',
    'user': 'postgres',
    'password': 'password'  # Update with your actual password
}

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_table_schema(cursor, table_name: str) -> Dict[str, Any]:
    """Get schema information for a table"""
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = []
    for row in cursor.fetchall():
        columns.append({
            'name': row[0],
            'type': row[1],
            'nullable': row[2] == 'YES',
            'default': row[3]
        })
    
    return {'table_name': table_name, 'columns': columns}

def get_table_count(cursor, table_name: str) -> int:
    """Get row count for a table"""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]

def get_sample_data(cursor, table_name: str, limit: int = 5) -> List[Dict]:
    """Get sample data from a table"""
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    return [dict(zip(columns, row)) for row in rows]

def get_table_relationships(cursor) -> List[Dict]:
    """Get foreign key relationships"""
    cursor.execute("""
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
    """)
    
    return [{
        'table': row[0],
        'column': row[1],
        'references_table': row[2],
        'references_column': row[3]
    } for row in cursor.fetchall()]

def get_user_insights(cursor) -> Dict[str, Any]:
    """Get insights about user data and patterns"""
    insights = {}
    
    # User count
    cursor.execute("SELECT COUNT(*) FROM users")
    insights['total_users'] = cursor.fetchone()[0]
    
    # Garments per user
    cursor.execute("""
        SELECT user_id, COUNT(*) as garment_count 
        FROM garments 
        GROUP BY user_id 
        ORDER BY garment_count DESC
    """)
    garment_counts = cursor.fetchall()
    insights['garments_per_user'] = {
        'average': sum(count[1] for count in garment_counts) / len(garment_counts) if garment_counts else 0,
        'max': max(count[1] for count in garment_counts) if garment_counts else 0,
        'min': min(count[1] for count in garment_counts) if garment_counts else 0
    }
    
    # Popular brands
    cursor.execute("""
        SELECT brand, COUNT(*) as count 
        FROM garments 
        GROUP BY brand 
        ORDER BY count DESC 
        LIMIT 10
    """)
    insights['popular_brands'] = [{'brand': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Fit feedback distribution
    cursor.execute("""
        SELECT fit_type, COUNT(*) as count 
        FROM fit_feedback 
        GROUP BY fit_type 
        ORDER BY count DESC
    """)
    insights['fit_feedback_distribution'] = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    return insights

def create_database_snapshot() -> Dict[str, Any]:
    """Create a comprehensive database snapshot"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'database_name': 'tailor2',
        'tables': {},
        'relationships': get_table_relationships(cursor),
        'insights': get_user_insights(cursor)
    }
    
    # Core tables to analyze
    tables = [
        'users', 'garments', 'measurements', 'fit_feedback', 
        'fit_zones', 'products', 'product_measurements'
    ]
    
    for table in tables:
        try:
            count = get_table_count(cursor, table)
            schema = get_table_schema(cursor, table)
            sample_data = get_sample_data(cursor, table, 3)
            
            snapshot['tables'][table] = {
                'row_count': count,
                'schema': schema,
                'sample_data': sample_data
            }
        except Exception as e:
            print(f"Error processing table {table}: {e}")
            snapshot['tables'][table] = {'error': str(e)}
    
    cursor.close()
    conn.close()
    
    return snapshot

def save_snapshot(snapshot: Dict[str, Any], filename: str = None):
    """Save snapshot to JSON file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"database_snapshot_{timestamp}.json"
    
    os.makedirs('database_snapshots', exist_ok=True)
    filepath = os.path.join('database_snapshots', filename)
    
    with open(filepath, 'w') as f:
        json.dump(snapshot, f, indent=2, default=str)
    
    print(f"Database snapshot saved to: {filepath}")
    return filepath

def print_summary(snapshot: Dict[str, Any]):
    """Print a summary of the database snapshot"""
    print("\n=== DATABASE SNAPSHOT SUMMARY ===")
    print(f"Timestamp: {snapshot['timestamp']}")
    print(f"Database: {snapshot['database_name']}")
    
    print("\nTable Row Counts:")
    for table_name, table_data in snapshot['tables'].items():
        if 'row_count' in table_data:
            print(f"  {table_name}: {table_data['row_count']} rows")
    
    print("\nUser Insights:")
    insights = snapshot['insights']
    print(f"  Total Users: {insights['total_users']}")
    print(f"  Avg Garments per User: {insights['garments_per_user']['average']:.1f}")
    
    print("\nPopular Brands:")
    for brand in insights['popular_brands'][:5]:
        print(f"  {brand['brand']}: {brand['count']} garments")
    
    print("\nFit Feedback Distribution:")
    for feedback in insights['fit_feedback_distribution']:
        print(f"  {feedback['type']}: {feedback['count']}")

if __name__ == "__main__":
    try:
        print("Creating database snapshot...")
        snapshot = create_database_snapshot()
        filepath = save_snapshot(snapshot)
        print_summary(snapshot)
        
        print(f"\nFull snapshot available at: {filepath}")
        print("You can share this file with AI assistants for database analysis.")
        
    except Exception as e:
        print(f"Error creating snapshot: {e}")
        print("Make sure the database is running and credentials are correct.") 