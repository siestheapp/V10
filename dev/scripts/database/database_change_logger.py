#!/usr/bin/env python3
"""
Database Change Logger - Creates human-readable logs of all database modifications
This script can be imported and used by other scripts to log changes automatically
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
import os

class DatabaseChangeLogger:
    def __init__(self, db_config, log_file="logs/database_changes.log"):
        self.db_config = db_config
        self.log_file = log_file
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Start new session
        self.log_session_start()
    
    def log_session_start(self):
        """Log the start of a new database session"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"DATABASE CHANGE SESSION: {self.session_id}\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
    
    def log_change(self, operation, table, details, old_data=None, new_data=None):
        """Log a database change with details"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {operation.upper()}: {table}\n")
            f.write(f"Details: {details}\n")
            
            if old_data:
                f.write(f"Old Data: {old_data}\n")
            if new_data:
                f.write(f"New Data: {new_data}\n")
            
            f.write(f"{'-'*40}\n\n")
    
    def log_insert(self, table, record_data, description=""):
        """Log an INSERT operation"""
        self.log_change(
            operation="INSERT",
            table=table,
            details=f"{description} - Added new record",
            new_data=record_data
        )
    
    def log_update(self, table, old_data, new_data, description=""):
        """Log an UPDATE operation"""
        self.log_change(
            operation="UPDATE", 
            table=table,
            details=f"{description} - Modified record",
            old_data=old_data,
            new_data=new_data
        )
    
    def log_delete(self, table, deleted_data, description=""):
        """Log a DELETE operation"""
        self.log_change(
            operation="DELETE",
            table=table, 
            details=f"{description} - Removed record",
            old_data=deleted_data
        )
    
    def log_schema_change(self, operation, details):
        """Log schema changes (CREATE TABLE, ALTER TABLE, etc.)"""
        self.log_change(
            operation=f"SCHEMA {operation}",
            table="SYSTEM",
            details=details
        )
    
    def log_security_change(self, table, change_type, details):
        """Log security/RLS changes"""
        self.log_change(
            operation=f"SECURITY {change_type}",
            table=table,
            details=details
        )
    
    def log_session_end(self, summary=""):
        """Log the end of a database session"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"SESSION END: {self.session_id}\n")
            f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if summary:
                f.write(f"Summary: {summary}\n")
            f.write(f"{'='*80}\n\n")

# Database configuration
DB_CONFIG = {
    'host': 'aws-1-us-east-1.pooler.supabase.com',
    'port': '5432',
    'database': 'postgres',
    'user': 'fs_core_rw',
    'password': 'CHANGE_ME'
}

def generate_current_state_log():
    """Generate a comprehensive log of current database state"""
    
    logger = DatabaseChangeLogger(DB_CONFIG)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.log_change(
            operation="SNAPSHOT",
            table="DATABASE",
            details="Generating current database state snapshot"
        )
        
        # Log all brands
        cur.execute("SELECT * FROM brands ORDER BY id")
        brands = cur.fetchall()
        
        for brand in brands:
            logger.log_change(
                operation="CURRENT",
                table="brands",
                details=f"Brand: {brand['name']} (Region: {brand['region']})",
                new_data=f"ID: {brand['id']}, Notes: {brand['notes'][:100] if brand['notes'] else 'None'}..."
            )
        
        # Log all user garments
        cur.execute('''
            SELECT ug.*, b.name as brand_name, c.name as category_name, sc.name as subcategory_name
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN categories c ON ug.category_id = c.id  
            LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
            WHERE ug.user_id = 1 AND ug.owns_garment = true
            ORDER BY ug.id
        ''')
        garments = cur.fetchall()
        
        for garment in garments:
            logger.log_change(
                operation="CURRENT",
                table="user_garments", 
                details=f"Garment: {garment['brand_name']} {garment['size_label']} - {garment['product_name']}",
                new_data=f"ID: {garment['id']}, Category: {garment['category_name']} > {garment['subcategory_name']}"
            )
        
        # Log size guides
        cur.execute('''
            SELECT sg.*, b.name as brand_name, c.name as category_name
            FROM size_guides sg
            JOIN brands b ON sg.brand_id = b.id
            LEFT JOIN categories c ON sg.category_id = c.id
            ORDER BY sg.id
        ''')
        size_guides = cur.fetchall()
        
        for guide in size_guides:
            logger.log_change(
                operation="CURRENT",
                table="size_guides",
                details=f"Size Guide: {guide['brand_name']} - {guide['category_name']} ({guide['gender']})",
                new_data=f"ID: {guide['id']}, Fit Type: {guide['fit_type']}, Unit: {guide['unit']}"
            )
        
        # Log security status
        security_tables = ['users', 'user_garments', 'brands', 'categories', 'size_guides', 'admins']
        
        for table in security_tables:
            cur.execute('''
                SELECT 
                    c.relname as table_name,
                    c.relrowsecurity as rls_enabled
                FROM pg_class c
                JOIN pg_namespace n ON c.relnamespace = n.oid
                WHERE n.nspname = 'public' 
                AND c.relkind = 'r'
                AND c.relname = %s
            ''', (table,))
            
            result = cur.fetchone()
            if result:
                status = "RESTRICTED" if result['rls_enabled'] else "UNRESTRICTED"
                logger.log_security_change(
                    table=table,
                    change_type="STATUS",
                    details=f"Current security: {status}"
                )
        
        logger.log_session_end("Database state snapshot completed")
        
        cur.close()
        conn.close()
        
        print(f"✅ Database state logged to: {logger.log_file}")
        
    except Exception as e:
        logger.log_change(
            operation="ERROR",
            table="SYSTEM", 
            details=f"Failed to generate state log: {e}"
        )
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    generate_current_state_log()
