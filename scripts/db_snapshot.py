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

# Database configuration - match the one used in app.py
DB_CONFIG = {
    "database": "tailor2",
    "user": "seandavey",
    "password": "",
    "host": "localhost"
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
    
    # Fit feedback distribution
    cursor.execute("""
        SELECT overall_fit, COUNT(*) as count 
        FROM user_fit_feedback 
        GROUP BY overall_fit 
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
        'database_name': 'tailor2',
        'tables': {},
        'relationships': get_table_relationships(cursor),
        'insights': get_user_insights(cursor)
    }
    
    # Get table schemas
    tables = [
        'users',
        'user_garments', 
        'user_fit_feedback',
        'user_fit_zones',
        'user_body_measurements',
        'product_measurements',
        'brands',
        'size_guides_v2'
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
    
    # Sample user_garments
    cursor.execute("""
        SELECT ug.id, ug.user_id, b.name as brand_name, ug.category, ug.size_label, 
               ug.chest_range, ug.created_at, uff.overall_fit
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
        LIMIT 5
    """)
    sample_data['user_garments'] = cursor.fetchall()
    
    # Sample user_fit_feedback
    cursor.execute("""
        SELECT garment_id, overall_fit, chest_fit, sleeve_fit, neck_fit, waist_fit
        FROM user_fit_feedback
        LIMIT 5
    """)
    sample_data['user_fit_feedback'] = cursor.fetchall()
    
    # Sample brands
    cursor.execute("""
        SELECT id, name, measurement_type
        FROM brands
        LIMIT 10
    """)
    sample_data['brands'] = cursor.fetchall()
    
    # Sample size_guides_v2
    cursor.execute("""
        SELECT brand_id, category, size_label, chest_min, chest_max, sleeve_min, sleeve_max
        FROM size_guides_v2
        LIMIT 5
    """)
    sample_data['size_guides_v2'] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return snapshot

def save_snapshot(snapshot: Dict[str, Any], filename: str = None):
    """Save snapshot to JSON file"""
    if not filename:
        timestamp = get_est_timestamp().strftime("%Y%m%d_%H%M%S")
        filename = f"database_snapshots/database_snapshot_{timestamp}.json"
    
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

def save_snapshot_to_markdown(snapshot_data: dict, filename: str = None):
    """Save database snapshot to a markdown file for AI analysis"""
    if not filename:
        timestamp = get_est_timestamp().strftime("%Y%m%d_%H%M%S")
        filename = f"database_snapshots/database_evolution_{timestamp}.md"
    
    # Ensure directory exists
    os.makedirs("database_snapshots", exist_ok=True)
    
    # Extract data from the actual snapshot structure
    table_counts = {table: data.get('row_count', 0) for table, data in snapshot_data['tables'].items()}
    insights = snapshot_data['insights']
    sample_data = snapshot_data.get('sample_data', {})
    
    # Create markdown content
    markdown_content = f"""# Database Snapshot - {get_est_timestamp().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Database Overview
- **Total Users**: {table_counts.get('users', 0)}
- **Total Garments**: {table_counts.get('user_garments', 0)}
- **Total Fit Feedback**: {table_counts.get('user_fit_feedback', 0)}
- **Total Brands**: {table_counts.get('brands', 0)}
- **Total Size Guides**: {table_counts.get('size_guides_v2', 0)}

## 👥 User Insights
- **Active Users**: {insights.get('total_users', 0)}
- **Average Garments per User**: {insights.get('garments_per_user', {}).get('average', 0):.1f}
- **Max Garments per User**: {insights.get('garments_per_user', {}).get('max', 0)}

## 🏷️ Popular Brands
"""
    
    # Add popular brands
    for brand in insights.get('popular_brands', [])[:5]:
        markdown_content += f"- **{brand.get('brand', 'Unknown')}**: {brand.get('count', 0)} garments\n"
    
    markdown_content += f"""
## 📏 Fit Feedback Distribution
"""
    
    # Add fit feedback distribution
    for feedback in insights.get('fit_feedback_distribution', []):
        markdown_content += f"- **{feedback.get('type', 'Unknown')}**: {feedback.get('count', 0)} garments\n"
    
    markdown_content += f"""
## 🔍 Sample Data

### Recent Garments
"""
    
    # Add sample garments
    for garment in sample_data.get('user_garments', [])[:3]:
        markdown_content += f"- **{garment.get('brand_name', 'Unknown')}** {garment.get('category', 'Unknown')} (Size {garment.get('size_label', 'Unknown')}): {garment.get('chest_range', 'Unknown')} - {garment.get('overall_fit', 'No feedback')}\n"
    
    markdown_content += f"""
### Recent Fit Feedback
"""
    
    # Add sample feedback
    for feedback in sample_data.get('user_fit_feedback', [])[:3]:
        markdown_content += f"- Garment {feedback.get('garment_id', 'Unknown')}: {feedback.get('overall_fit', 'Unknown')} (Chest: {feedback.get('chest_fit', 'Unknown')}, Sleeve: {feedback.get('sleeve_fit', 'Unknown')})\n"
    
    markdown_content += f"""
## 🚀 Development Insights

### Data Quality
- **User Engagement**: {insights.get('total_users', 0)} active users
- **Feedback Quality**: {table_counts.get('user_fit_feedback', 0)} feedback entries
- **Brand Diversity**: {table_counts.get('brands', 0)} brands in system

### Growth Opportunities
- More garments needed for better fit zone calculations
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
    summary_file = "database_snapshots/DATABASE_EVOLUTION_SUMMARY.md"
    
    # Get all snapshot files
    snapshot_files = []
    if os.path.exists("database_snapshots"):
        for file in os.listdir("database_snapshots"):
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

| Date | Users | Garments | Fit Feedback | Brands | Avg Garments/User |
|------|-------|----------|--------------|--------|-------------------|
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
        json_filename = f"database_snapshots/database_snapshot_{timestamp}.json"
        
        os.makedirs("database_snapshots", exist_ok=True)
        with open(json_filename, 'w') as f:
            json.dump(snapshot_data, f, indent=2, default=str)
        
        print(f"✅ JSON snapshot saved: {json_filename}")
        
        # Save as markdown for AI analysis
        markdown_filename = save_snapshot_to_markdown(snapshot_data)
        
        # Update evolution summary
        update_evolution_summary()
        
        print("🎉 Database snapshot complete!")
        print(f"📊 JSON: {json_filename}")
        print(f"📝 Markdown: {markdown_filename}")
        print(f"📈 Summary: database_snapshots/DATABASE_EVOLUTION_SUMMARY.md")
        
    except Exception as e:
        print(f"❌ Error taking snapshot: {str(e)}")
        import traceback
        traceback.print_exc() 