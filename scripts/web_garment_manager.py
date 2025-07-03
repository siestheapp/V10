#!/usr/bin/env python3
"""
Web UI for Garment Management in tailor3
Simple Flask interface for adding garments and feedback
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
from db_change_logger import log_garment_addition, log_feedback_submission, log_brand_addition

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration - Supabase tailor3
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_or_create_id(cursor, table, column, value, extra_columns=None, extra_values=None, admin_id=None):
    """Get existing ID or create new record"""
    cursor.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # Insert if not found
    if extra_columns and extra_values:
        columns = f"{column}, {', '.join(extra_columns)}"
        placeholders = ', '.join(['%s'] * (1 + len(extra_values)))
        values = (value,) + tuple(extra_values)
        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id", values)
    else:
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES (%s) RETURNING id", (value,))
    new_id = cursor.fetchone()[0]
    
    # Update created_by for admin-tracked tables
    if admin_id and table in ["brands", "categories", "subcategories"]:
        cursor.execute(f"UPDATE {table} SET created_by = %s WHERE id = %s", (admin_id, new_id))
    
    # Log brand creation
    if table == "brands":
        log_brand_addition(value, new_id)
    
    return new_id

@app.route('/')
def index():
    """Main dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get users
    cursor.execute("SELECT id, email, gender, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    
    # Get recent garments
    cursor.execute("""
        SELECT ug.id, ug.product_name, ug.size_label, ug.created_at, 
               b.name as brand_name, u.email as user_email
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        JOIN users u ON ug.user_id = u.id
        ORDER BY ug.created_at DESC
        LIMIT 10
    """)
    recent_garments = cursor.fetchall()
    
    # Get brands
    cursor.execute("SELECT id, name, default_unit FROM brands ORDER BY name")
    brands = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', users=users, recent_garments=recent_garments, brands=brands)

@app.route('/add_garment', methods=['GET', 'POST'])
def add_garment():
    """Add a new garment"""
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get form data
            user_email = request.form['user_email']
            brand_name = request.form['brand_name']
            category_name = request.form['category_name']
            subcategory_name = request.form.get('subcategory_name', '')
            gender = request.form['gender']
            size_label = request.form['size_label']
            
            # Handle size - check if "Other" was selected
            if size_label == "Other":
                size_label = request.form.get('other_size_label', '').strip()
                if not size_label:
                    flash('Please enter a size when selecting "Other"', 'error')
                    return redirect(url_for('add_garment'))
            fit_type = request.form['fit_type']
            product_name = request.form['product_name'].strip()
            product_url = request.form.get('product_url', '')
            
            # Handle empty product name
            if not product_name:
                product_name = None
            
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE email = %s", (user_email,))
            user_result = cursor.fetchone()
            if not user_result:
                flash(f'User {user_email} not found. Please create the user first.', 'error')
                return redirect(url_for('add_garment'))
            user_id = user_result[0]
            
            # Get brand ID (must exist)
            cursor.execute("SELECT id FROM brands WHERE name = %s", (brand_name,))
            brand_result = cursor.fetchone()
            if not brand_result:
                flash(f'Brand "{brand_name}" not found. Please contact an admin to add this brand.', 'error')
                return redirect(url_for('add_garment'))
            brand_id = brand_result[0]
            
            # Get category ID (must exist)
            cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
            category_result = cursor.fetchone()
            if not category_result:
                flash(f'Category "{category_name}" not found. Please contact an admin to add this category.', 'error')
                return redirect(url_for('add_garment'))
            category_id = category_result[0]
            
            # Get subcategory ID if provided
            subcategory_id = None
            if subcategory_name:
                cursor.execute("SELECT id FROM subcategories WHERE name = %s", (subcategory_name,))
                subcategory_result = cursor.fetchone()
                if not subcategory_result:
                    flash(f'Subcategory "{subcategory_name}" not found. Please contact an admin to add this subcategory.', 'error')
                    return redirect(url_for('add_garment'))
                subcategory_id = subcategory_result[0]
            
            # Insert garment
            cursor.execute("""
                INSERT INTO user_garments (
                    user_id, brand_id, category_id, subcategory_id, gender, 
                    size_label, fit_type, unit, product_name, product_url, owns_garment
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'in', %s, %s, true)
                RETURNING id
            """, (user_id, brand_id, category_id, subcategory_id, gender, 
                  size_label, fit_type, product_name, product_url))
            
            garment_id = cursor.fetchone()[0]
            
            # Log the garment addition
            log_garment_addition(user_id, brand_name, product_name, size_label, garment_id)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Create success message
            if product_name:
                flash(f'Garment "{product_name}" added successfully!', 'success')
            else:
                flash(f'Garment added successfully!', 'success')
            return redirect(url_for('view_garment', garment_id=garment_id))
            
        except Exception as e:
            flash(f'Error adding garment: {str(e)}', 'error')
            return redirect(url_for('add_garment'))
    
    # GET request - show form
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get users for dropdown
    cursor.execute("SELECT id, email FROM users ORDER BY email")
    users = cursor.fetchall()
    
    # Get brands for dropdown
    cursor.execute("SELECT id, name FROM brands ORDER BY name")
    brands = cursor.fetchall()
    
    # Get categories for dropdown
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    
    # Get subcategories for dropdown
    cursor.execute("SELECT id, name FROM subcategories ORDER BY name")
    subcategories = cursor.fetchall()
    
    # Get existing sizes from user_garments
    cursor.execute("SELECT DISTINCT size_label FROM user_garments WHERE size_label IS NOT NULL ORDER BY size_label")
    existing_sizes = [row['size_label'] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('add_garment.html', users=users, brands=brands, categories=categories, subcategories=subcategories, existing_sizes=existing_sizes)

@app.route('/garment/<int:garment_id>')
def view_garment(garment_id):
    """View a specific garment and its feedback"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get garment details
    cursor.execute("""
        SELECT ug.*, b.name as brand_name, c.name as category_name, 
               sc.name as subcategory_name, u.email as user_email
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        JOIN categories c ON ug.category_id = c.id
        LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
        JOIN users u ON ug.user_id = u.id
        WHERE ug.id = %s
    """, (garment_id,))
    garment = cursor.fetchone()
    
    if not garment:
        flash('Garment not found', 'error')
        return redirect(url_for('index'))
    
    # Get feedback for this garment
    cursor.execute("""
        SELECT ugf.*, fc.feedback_text
        FROM user_garment_feedback ugf
        JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
        WHERE ugf.user_garment_id = %s
        ORDER BY ugf.created_at DESC
    """, (garment_id,))
    feedback = cursor.fetchall()
    
    # Get available feedback codes
    cursor.execute("SELECT id, feedback_text FROM feedback_codes ORDER BY feedback_text")
    feedback_codes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('view_garment.html', garment=garment, feedback=feedback, feedback_codes=feedback_codes)

@app.route('/add_feedback/<int:garment_id>', methods=['POST'])
def add_feedback(garment_id):
    """Add feedback for a garment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        dimension = request.form['dimension']
        feedback_code_id = request.form['feedback_code_id']
        
        # Insert feedback
        cursor.execute("""
            INSERT INTO user_garment_feedback (user_garment_id, dimension, feedback_code_id)
            VALUES (%s, %s, %s)
        """, (garment_id, dimension, feedback_code_id))
        
        # Get feedback text for logging
        cursor.execute("SELECT feedback_text FROM feedback_codes WHERE id = %s", (feedback_code_id,))
        feedback_text = cursor.fetchone()[0]
        
        # Get user_id for logging
        cursor.execute("SELECT user_id FROM user_garments WHERE id = %s", (garment_id,))
        user_id = cursor.fetchone()[0]
        
        # Log the feedback
        log_feedback_submission(user_id, garment_id, dimension, feedback_text)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Feedback added successfully!', 'success')
        
    except Exception as e:
        flash(f'Error adding feedback: {str(e)}', 'error')
    
    return redirect(url_for('view_garment', garment_id=garment_id))

@app.route('/api/feedback_codes')
def get_feedback_codes():
    """API endpoint to get feedback codes"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT id, feedback_text FROM feedback_codes ORDER BY feedback_text")
    feedback_codes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify([dict(code) for code in feedback_codes])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 