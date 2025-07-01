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
import pytz

# Database configuration - connect to Supabase (pooled connection)
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def get_est_timestamp():
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

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
    
    # Brand count
    cursor.execute("SELECT COUNT(*) FROM brands")
    insights['total_brands'] = cursor.fetchone()[0]
    
    # Size guides count
    cursor.execute("SELECT COUNT(*) FROM size_guides")
    insights['total_size_guides'] = cursor.fetchone()[0]
    
    # Garments per user
    cursor.execute("""
        SELECT user_id, COUNT(*) as garment_count 
        FROM user_garments 
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
        SELECT b.name as brand_name, COUNT(*) as count 
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        GROUP BY b.name 
        ORDER BY count DESC 
        LIMIT 10
    """)
    insights['popular_brands'] = [{'brand': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Fit feedback distribution (using feedback_codes table)
    cursor.execute("""
        SELECT fc.feedback_text, COUNT(*) as count 
        FROM user_garment_feedback ugf
        JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
        GROUP BY fc.feedback_text 
        ORDER BY count DESC
    """)
    insights['fit_feedback_distribution'] = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    return insights

def get_database_snapshot() -> Dict[str, Any]:
    """Create a comprehensive database snapshot"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    snapshot = {
        'timestamp': get_est_timestamp().isoformat(),
        'database_name': 'tailor3',
        'tables': {},
        'relationships': get_table_relationships(cursor),
        'insights': get_user_insights(cursor)
    }
    
    # Get table schemas
    tables = [
        'users',
        'admins',
        'body_measurements',
        'brands',
        'categories',
        'subcategories',
        'size_guides',
        'size_guide_entries',
        'raw_size_guides',
        'standardization_log',
        'user_garments',
        'user_garment_feedback',
        'feedback_codes',
        'fit_zones'
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
    
    # Sample data from key tables
    sample_data = {}
    
    # Sample users
    cursor.execute("""
        SELECT id, email, gender, created_at FROM users LIMIT 5
    """)
    sample_data['users'] = cursor.fetchall()

    # Sample brands
    cursor.execute("""
        SELECT id, name, default_unit FROM brands LIMIT 5
    """)
    sample_data['brands'] = cursor.fetchall()

    # Sample size_guides
    cursor.execute("""
        SELECT id, brand_id, gender, category_id, fit_type, guide_level, version, unit FROM size_guides LIMIT 5
    """)
    sample_data['size_guides'] = cursor.fetchall()

    # Sample size_guide_entries
    cursor.execute("""
        SELECT id, size_guide_id, size_label, chest_min, chest_max, waist_min, waist_max, sleeve_min, sleeve_max, neck_min, neck_max, hip_min, hip_max FROM size_guide_entries LIMIT 5
    """)
    sample_data['size_guide_entries'] = cursor.fetchall()

    # Sample user_garments
    cursor.execute("""
        SELECT id, user_id, brand_id, category_id, subcategory_id, gender, size_label, fit_type, unit, product_name, created_at FROM user_garments LIMIT 5
    """)
    sample_data['user_garments'] = cursor.fetchall()

    # Sample user_garment_feedback
    cursor.execute("""
        SELECT id, user_garment_id, dimension, feedback_code_id, created_at FROM user_garment_feedback LIMIT 5
    """)
    sample_data['user_garment_feedback'] = cursor.fetchall()

    # Sample fit_zones
    cursor.execute("""
        SELECT id, user_id, category_id, subcategory_id, dimension, fit_type, min_value, max_value, unit, created_at FROM fit_zones LIMIT 5
    """)
    sample_data['fit_zones'] = cursor.fetchall()

    # Print sample data
    print("\nSample users:")
    for row in sample_data.get('users', [])[:3]:
        print(row)
    print("\nSample brands:")
    for row in sample_data.get('brands', [])[:3]:
        print(row)
    print("\nSample size_guides:")
    for row in sample_data.get('size_guides', [])[:3]:
        print(row)
    print("\nSample size_guide_entries:")
    for row in sample_data.get('size_guide_entries', [])[:3]:
        print(row)
    print("\nSample user_garments:")
    for row in sample_data.get('user_garments', [])[:3]:
        print(row)
    print("\nSample user_garment_feedback:")
    for row in sample_data.get('user_garment_feedback', [])[:3]:
        print(row)
    print("\nSample fit_zones:")
    for row in sample_data.get('fit_zones', [])[:3]:
        print(row)
    
    cursor.close()
    conn.close()
    
    return snapshot

def save_snapshot(snapshot: Dict[str, Any], filename: str = None):
    """Save snapshot to JSON file"""
    if not filename:
        timestamp = get_est_timestamp().strftime("%Y%m%d_%H%M%S")
        filename = f"supabase/snapshots/2025-06-29/database_snapshot_{timestamp}.json"
    
    os.makedirs('supabase/snapshots/2025-06-29', exist_ok=True)
    filepath = os.path.join('supabase/snapshots/2025-06-29', filename) if not filename.startswith('supabase/snapshots/2025-06-29') else filename
    
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
    print(f"  Total Brands: {insights['total_brands']}")
    print(f"  Total Size Guides: {insights['total_size_guides']}")
    
    print("\nGarments per User:")
    garment_counts = insights['garments_per_user']
    print(f"  Average: {garment_counts['average']}")
    print(f"  Max: {garment_counts['max']}")
    print(f"  Min: {garment_counts['min']}")
    
    print("\nPopular Brands:")
    for brand in insights['popular_brands'][:5]:
        print(f"  {brand['brand']}: {brand['count']} garments")
    
    print("\nFit Feedback Distribution:")
    for feedback in insights['fit_feedback_distribution'][:5]:
        print(f"  {feedback['type']}: {feedback['count']} garments")

def save_snapshot_to_markdown(snapshot_data: dict, filename: str = None):
    """Save database snapshot to a markdown file for AI analysis"""
    if not filename:
        timestamp = get_est_timestamp().strftime("%Y%m%d_%H%M%S")
        filename = f"supabase/snapshots/2025-06-29/database_evolution_{timestamp}.md"
    
    # Ensure directory exists
    os.makedirs("supabase/snapshots/2025-06-29", exist_ok=True)
    
    # Extract data from the actual snapshot structure
    table_counts = {table: data.get('row_count', 0) for table, data in snapshot_data['tables'].items()}
    insights = snapshot_data['insights']
    sample_data = snapshot_data.get('sample_data', {})
    
    # Create markdown content
    markdown_content = f"""# Database Snapshot - {get_est_timestamp().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Database Overview
- **Total Users**: {table_counts.get('users', 0)}
- **Total Brands**: {table_counts.get('brands', 0)}
- **Total Size Guides**: {table_counts.get('size_guides', 0)}

## 👥 User Insights
- **Garments per User**: {insights['garments_per_user']}
- **Popular Brands**: {insights['popular_brands']}
- **Fit Feedback Distribution**: {insights['fit_feedback_distribution']}

## 🏷️ Popular Brands
"""
    
    # Add popular brands
    for brand in insights.get('popular_brands', [])[:5]:
        markdown_content += f"- **{brand.get('brand', 'Unknown')}**: {brand.get('count', 0)} garments\n"
    
    markdown_content += f"""
## 📏 Size Guide Distribution
"""
    
    # Add size guide distribution
    for guide in insights.get('size_guides', []):
        markdown_content += f"- **{guide.get('brand_id', 'Unknown')}**: {guide.get('guide_level', 'Unknown')} (Size {guide.get('size_label', 'Unknown')})\n"
    
    markdown_content += f"""
## 🔍 Sample Data

### Recent Garments
"""
    
    # Add sample garments
    for garment in sample_data.get('user_garments', [])[:3]:
        markdown_content += f"- **{garment.get('brand_name', 'Unknown')}** {garment.get('category_id', 'Unknown')} (Size {garment.get('size_label', 'Unknown')}): {garment.get('chest_range', 'Unknown')} - {garment.get('overall_fit', 'No feedback')}\n"
    
    markdown_content += f"""
### Recent Fit Feedback
"""
    
    # Add sample feedback
    for feedback in sample_data.get('user_garment_feedback', [])[:3]:
        markdown_content += f"- Garment {feedback.get('user_garment_id', 'Unknown')}: {feedback.get('dimension', 'Unknown')} (Feedback Code: {feedback.get('feedback_code_id', 'Unknown')})\n"
    
    markdown_content += f"""
## 🚀 Development Insights

### Data Quality
- **Brand Diversity**: {table_counts.get('brands', 0)} brands in system
- **Size Guide Coverage**: {table_counts.get('size_guides', 0)} size guides
- **Fit Zone Calculations**: {table_counts.get('fit_zones', 0)} fit zones

### Growth Opportunities
- More size guides needed for better fit zone calculations
- Additional fit feedback will improve recommendation accuracy
- Expanding brand catalog will enhance size guide coverage

---
*Snapshot generated automatically for AI analysis*
"""
    
    # Save to file
    with open(filename, 'w') as f:
        f.write(markdown_content)
    
    print(f"✅ Snapshot saved to {filename}")
    return filename

def update_evolution_summary():
    """Update the main evolution summary file"""
    summary_file = "supabase/snapshots/2025-06-29/DATABASE_EVOLUTION_SUMMARY.md"
    
    # Get all snapshot files
    snapshot_files = []
    if os.path.exists("supabase/snapshots/2025-06-29"):
        for file in os.listdir("supabase/snapshots/2025-06-29"):
            if file.startswith("database_evolution_") and file.endswith(".md"):
                snapshot_files.append(file)
    
    # Sort by timestamp
    snapshot_files.sort()
    
    # Create summary
    summary_content = """# Database Evolution Summary

This file tracks how the V10 database evolves over time, providing context for AI analysis and development decisions.

## 📈 Evolution Timeline

"""
    
    for file in snapshot_files:
        timestamp = file.replace("database_evolution_", "").replace(".md", "")
        date_str = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M")
        summary_content += f"- [{date_str}](./{file}) - Database snapshot\n"
    
    summary_content += f"""
## 📊 Key Metrics Over Time

| Date | Brands | Size Guides | Fit Zones | Avg Garments/User |
|------|--------|------------|-----------|-------------------|
"""
    
    # Add metrics from each snapshot (simplified for now)
    for file in snapshot_files[-5:]:  # Last 5 snapshots
        timestamp = file.replace("database_evolution_", "").replace(".md", "")
        date_str = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d")
        summary_content += f"| {date_str} | [View](./{file}) | | | | |\n"
    
    summary_content += f"""
## 🎯 Development Insights

### Data Quality Trends
- Track user engagement over time
- Monitor fit feedback quality
- Identify popular brands and categories

### Performance Indicators
- User retention (garments per user)
- Feedback completion rates
- Brand diversity

### AI Training Opportunities
- More data = better fit zone calculations
- Diverse feedback = more accurate recommendations
- Brand variety = better size guide coverage

---
*Updated automatically with each snapshot*
"""
    
    # Save summary
    with open(summary_file, 'w') as f:
        f.write(summary_content)
    
    print(f"✅ Evolution summary updated: {summary_file}")

if __name__ == "__main__":
    try:
        print("🔍 Taking database snapshot...")
        
        # Get database snapshot
        snapshot_data = get_database_snapshot()
        
        # Save as JSON (existing functionality)
        timestamp = get_est_timestamp().strftime("%Y%m%d_%H%M%S")
        json_filename = f"supabase/snapshots/2025-06-29/database_snapshot_{timestamp}.json"
        
        os.makedirs("supabase/snapshots/2025-06-29", exist_ok=True)
        with open(json_filename, 'w') as f:
            json.dump(snapshot_data, f, indent=2, default=str)
        
        print(f"✅ JSON snapshot saved: {json_filename}")
        
        # Save as markdown for AI analysis
        markdown_filename = save_snapshot_to_markdown(snapshot_data)
        
        # Update evolution summary
        update_evolution_summary()
        
        print("🎉 Database snapshot complete!")
        print(f"\ud83d\udcca JSON: {json_filename}")
        print(f"\ud83d\udcdd Markdown: {markdown_filename}")
        print(f"\ud83d\udcc8 Summary: supabase/snapshots/2025-06-29/DATABASE_EVOLUTION_SUMMARY.md")
        
    except Exception as e:
        print(f"❌ Error taking snapshot: {str(e)}")
        import traceback
        traceback.print_exc() 