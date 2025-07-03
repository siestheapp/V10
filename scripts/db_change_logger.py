#!/usr/bin/env python3
"""
Database Change Logger for V10
Lightweight tool to log individual database changes without full snapshots
"""

import psycopg2
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import pytz
from pathlib import Path

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

def log_change(change_type: str, table: str, details: Dict[str, Any], user_id: str = None):
    """
    Log a single database change
    
    Args:
        change_type: 'INSERT', 'UPDATE', 'DELETE', 'SCHEMA_CHANGE'
        table: Table name
        details: Dictionary with change details
        user_id: Optional user ID if change is user-related
    """
    timestamp = get_est_timestamp()
    
    change_log = {
        "timestamp": timestamp.isoformat(),
        "change_type": change_type,
        "table": table,
        "details": details,
        "user_id": user_id
    }
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("supabase/change_logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Append to daily log file
    date_str = timestamp.strftime("%Y-%m-%d")
    log_file = logs_dir / f"db_changes_{date_str}.jsonl"
    
    with open(log_file, "a") as f:
        f.write(json.dumps(change_log) + "\n")
    
    # Also append to summary log
    summary_file = logs_dir / "db_changes_summary.jsonl"
    with open(summary_file, "a") as f:
        f.write(json.dumps(change_log) + "\n")
    
    print(f"✅ Logged {change_type} on {table}: {details.get('description', 'No description')}")

def log_user_creation(email: str, gender: str, user_id: int):
    """Log user creation"""
    log_change(
        "INSERT", 
        "users", 
        {
            "description": f"Created user: {email}",
            "email": email,
            "gender": gender,
            "user_id": user_id
        },
        str(user_id)
    )

def log_garment_addition(user_id: int, brand_name: str, product_name: str, size_label: str, garment_id: int):
    """Log garment addition"""
    log_change(
        "INSERT",
        "user_garments",
        {
            "description": f"Added garment: {product_name} ({brand_name}, {size_label})",
            "brand_name": brand_name,
            "product_name": product_name,
            "size_label": size_label,
            "garment_id": garment_id
        },
        str(user_id)
    )

def log_feedback_submission(user_id: int, garment_id: int, dimension: str, feedback_text: str):
    """Log feedback submission"""
    log_change(
        "INSERT",
        "user_garment_feedback",
        {
            "description": f"Added feedback: {dimension} - {feedback_text}",
            "garment_id": garment_id,
            "dimension": dimension,
            "feedback_text": feedback_text
        },
        str(user_id)
    )

def log_brand_addition(brand_name: str, brand_id: int):
    """Log brand addition"""
    log_change(
        "INSERT",
        "brands",
        {
            "description": f"Added brand: {brand_name}",
            "brand_name": brand_name,
            "brand_id": brand_id
        }
    )

def log_category_addition(category_name: str, category_id: int):
    """Log category addition"""
    log_change(
        "INSERT",
        "categories",
        {
            "description": f"Added category: {category_name}",
            "category_name": category_name,
            "category_id": category_id
        }
    )

def log_subcategory_addition(subcategory_name: str, subcategory_id: int):
    """Log subcategory addition"""
    log_change(
        "INSERT",
        "subcategories",
        {
            "description": f"Added subcategory: {subcategory_name}",
            "subcategory_name": subcategory_name,
            "subcategory_id": subcategory_id
        }
    )

def log_size_guide_addition(brand_name: str, gender: str, category: str, size_guide_id: int):
    """Log size guide addition"""
    log_change(
        "INSERT",
        "size_guides",
        {
            "description": f"Added size guide: {brand_name} {gender} {category}",
            "brand_name": brand_name,
            "gender": gender,
            "category": category,
            "size_guide_id": size_guide_id
        }
    )

def get_recent_changes(limit: int = 20) -> List[Dict]:
    """Get recent changes from the summary log"""
    summary_file = Path("supabase/change_logs/db_changes_summary.jsonl")
    
    if not summary_file.exists():
        return []
    
    changes = []
    with open(summary_file, "r") as f:
        lines = f.readlines()
        # Get last N lines
        for line in lines[-limit:]:
            try:
                changes.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    return changes

def print_recent_changes(limit: int = 10):
    """Print recent changes in a readable format"""
    changes = get_recent_changes(limit)
    
    if not changes:
        print("No changes logged yet.")
        return
    
    print(f"\n📋 Recent Database Changes (last {len(changes)}):")
    print("=" * 80)
    
    for change in reversed(changes):  # Show newest first
        timestamp = change["timestamp"]
        change_type = change["change_type"]
        table = change["table"]
        description = change["details"].get("description", "No description")
        user_id = change.get("user_id", "N/A")
        
        print(f"🕒 {timestamp}")
        print(f"   📝 {change_type} on {table}")
        print(f"   👤 User: {user_id}")
        print(f"   📄 {description}")
        print("-" * 80)

def get_change_stats() -> Dict[str, Any]:
    """Get statistics about database changes"""
    summary_file = Path("supabase/change_logs/db_changes_summary.jsonl")
    
    if not summary_file.exists():
        return {"total_changes": 0, "changes_by_type": {}, "changes_by_table": {}}
    
    stats = {
        "total_changes": 0,
        "changes_by_type": {},
        "changes_by_table": {},
        "changes_by_user": {}
    }
    
    with open(summary_file, "r") as f:
        for line in f:
            try:
                change = json.loads(line.strip())
                stats["total_changes"] += 1
                
                # Count by type
                change_type = change["change_type"]
                stats["changes_by_type"][change_type] = stats["changes_by_type"].get(change_type, 0) + 1
                
                # Count by table
                table = change["table"]
                stats["changes_by_table"][table] = stats["changes_by_table"].get(table, 0) + 1
                
                # Count by user
                user_id = change.get("user_id", "system")
                stats["changes_by_user"][user_id] = stats["changes_by_user"].get(user_id, 0) + 1
                
            except json.JSONDecodeError:
                continue
    
    return stats

def print_change_stats():
    """Print change statistics"""
    stats = get_change_stats()
    
    print("\n📊 Database Change Statistics:")
    print("=" * 50)
    print(f"Total Changes: {stats['total_changes']}")
    
    print("\nBy Type:")
    for change_type, count in stats["changes_by_type"].items():
        print(f"  {change_type}: {count}")
    
    print("\nBy Table:")
    for table, count in stats["changes_by_table"].items():
        print(f"  {table}: {count}")
    
    print("\nBy User:")
    for user_id, count in stats["changes_by_user"].items():
        print(f"  {user_id}: {count}")

def main():
    """Main function for command line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python db_change_logger.py [recent|stats|log]")
        print("  recent [N] - Show recent changes (default 10)")
        print("  stats      - Show change statistics")
        print("  log        - Interactive logging mode")
        return
    
    command = sys.argv[1]
    
    if command == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print_recent_changes(limit)
    
    elif command == "stats":
        print_change_stats()
    
    elif command == "log":
        print("Interactive logging mode - use the log_* functions in your code")
        print("Example: log_user_creation('user@example.com', 'Male', 123)")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main() 