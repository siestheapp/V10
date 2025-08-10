#!/usr/bin/env python3
"""
Admin Interface for Garment Management in tailor3
Separate from user interface for proper role separation
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from db_change_logger import log_brand_addition, log_category_addition, log_subcategory_addition

app = Flask(__name__)
app.secret_key = 'admin-secret-key-here'

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

def log_admin_activity(cursor, admin_id, action_type, table_name=None, record_id=None, description=None, details=None):
    """Log admin activity to the audit log"""
    cursor.execute("""
        INSERT INTO admin_activity_log (admin_id, action_type, table_name, record_id, description, details)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (admin_id, action_type, table_name, record_id, description, json.dumps(details) if details else None))

def require_admin_login(f):
    """Decorator to require admin login"""
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in as admin', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # In production, use proper password hashing
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT id, email, name, role FROM admins WHERE email = %s", (email,))
        admin = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if admin and password == "admin123":  # Simple password for demo
            session['admin_id'] = admin['id']
            session['admin_email'] = admin['email']
            session['admin_name'] = admin['name']
            session['admin_role'] = admin['role']
            flash(f'Welcome, {admin["name"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/')
@require_admin_login
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as user_count FROM users")
    user_count = cursor.fetchone()['user_count']
    
    cursor.execute("SELECT COUNT(*) as garment_count FROM user_garments")
    garment_count = cursor.fetchone()['garment_count']
    
    cursor.execute("SELECT COUNT(*) as brand_count FROM brands")
    brand_count = cursor.fetchone()['brand_count']
    
    cursor.execute("SELECT COUNT(*) as feedback_count FROM user_garment_feedback")
    feedback_count = cursor.fetchone()['feedback_count']
    
    # Get recent activity
    cursor.execute("""
        SELECT ug.id, ug.product_name, ug.created_at, b.name as brand_name, u.email as user_email
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        JOIN users u ON ug.user_id = u.id
        ORDER BY ug.created_at DESC
        LIMIT 10
    """)
    recent_garments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         user_count=user_count, 
                         garment_count=garment_count,
                         brand_count=brand_count,
                         feedback_count=feedback_count,
                         recent_garments=recent_garments)

@app.route('/admin/brands')
@require_admin_login
def admin_brands():
    """Manage brands"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT b.*, a.name as created_by_name, 
               COUNT(ug.id) as garment_count
        FROM brands b
        LEFT JOIN admins a ON b.created_by = a.id
        LEFT JOIN user_garments ug ON b.id = ug.brand_id
        GROUP BY b.id, a.name
        ORDER BY b.name
    """)
    brands = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/brands.html', brands=brands)

@app.route('/admin/brands/add', methods=['POST'])
@require_admin_login
def admin_add_brand():
    """Add new brand"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        brand_name = request.form['brand_name'].strip()
        default_unit = request.form.get('default_unit', 'in')
        
        if not brand_name:
            flash('Brand name is required', 'error')
            return redirect(url_for('admin_brands'))
        
        # Check if brand already exists
        cursor.execute("SELECT id FROM brands WHERE name = %s", (brand_name,))
        if cursor.fetchone():
            flash(f'Brand "{brand_name}" already exists', 'error')
            return redirect(url_for('admin_brands'))
        
        # Create brand
        cursor.execute("""
            INSERT INTO brands (name, default_unit, created_by)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (brand_name, default_unit, session['admin_id']))
        
        brand_id = cursor.fetchone()[0]
        
        # Log admin activity
        log_admin_activity(
            cursor, 
            session['admin_id'], 
            'CREATE_BRAND', 
            'brands', 
            brand_id, 
            f'Created brand: {brand_name}',
            {'brand_name': brand_name, 'default_unit': default_unit}
        )
        
        # Log the brand creation
        log_brand_addition(brand_name, brand_id)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Brand "{brand_name}" added successfully!', 'success')
        
    except Exception as e:
        flash(f'Error adding brand: {str(e)}', 'error')
    
    return redirect(url_for('admin_brands'))

@app.route('/admin/categories')
@require_admin_login
def admin_categories():
    """Manage categories"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT c.*, a.name as created_by_name,
               COUNT(ug.id) as garment_count
        FROM categories c
        LEFT JOIN admins a ON c.created_by = a.id
        LEFT JOIN user_garments ug ON c.id = ug.category_id
        GROUP BY c.id, a.name
        ORDER BY c.name
    """)
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['POST'])
@require_admin_login
def admin_add_category():
    """Add new category"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        category_name = request.form['category_name'].strip()
        
        if not category_name:
            flash('Category name is required', 'error')
            return redirect(url_for('admin_categories'))
        
        # Check if category already exists
        cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
        if cursor.fetchone():
            flash(f'Category "{category_name}" already exists', 'error')
            return redirect(url_for('admin_categories'))
        
        # Create category
        cursor.execute("""
            INSERT INTO categories (name, created_by)
            VALUES (%s, %s)
            RETURNING id
        """, (category_name, session['admin_id']))
        
        category_id = cursor.fetchone()[0]
        
        # Log admin activity
        log_admin_activity(
            cursor, 
            session['admin_id'], 
            'CREATE_CATEGORY', 
            'categories', 
            category_id, 
            f'Created category: {category_name}',
            {'category_name': category_name}
        )
        
        # Log the category creation
        log_category_addition(category_name, category_id)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Category "{category_name}" added successfully!', 'success')
        
    except Exception as e:
        flash(f'Error adding category: {str(e)}', 'error')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/users')
@require_admin_login
def admin_users():
    """View all users"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT u.*, COUNT(ug.id) as garment_count,
               COUNT(ugf.id) as feedback_count
        FROM users u
        LEFT JOIN user_garments ug ON u.id = ug.user_id
        LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/activity')
@require_admin_login
def admin_activity():
    """View admin activity log"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT aal.*, a.name as admin_name, a.email as admin_email
        FROM admin_activity_log aal
        JOIN admins a ON aal.admin_id = a.id
        ORDER BY aal.created_at DESC
        LIMIT 100
    """)
    activities = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/activity.html', activities=activities)

# Size Guide Management Routes
@app.route('/admin/size-guides')
@require_admin_login
def admin_size_guides():
    """List all size guides"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT sg.id, b.name as brand_name, sg.gender, c.name as category_name, 
                   sg.guide_level, sg.source_url, sg.created_at,
                   COUNT(sge.id) as entry_count
            FROM size_guides sg
            JOIN brands b ON sg.brand_id = b.id
            JOIN categories c ON sg.category_id = c.id
            LEFT JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
            GROUP BY sg.id, b.name, sg.gender, c.name, sg.guide_level, sg.source_url, sg.created_at
            ORDER BY sg.created_at DESC
        """)
        size_guides = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin/size_guides.html', size_guides=size_guides)
        
    except Exception as e:
        flash(f'Error loading size guides: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/size-guides/upload', methods=['GET', 'POST'])
@require_admin_login
def admin_upload_size_guide():
    """Multi-step size guide upload wizard"""
    if request.method == 'GET':
        # Load brands and categories for the form
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT id, name FROM brands ORDER BY name")
        brands = cursor.fetchall()
        
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin/upload_size_guide.html', brands=brands, categories=categories)
    
    # POST - Process the uploaded size guide
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get form data
        brand_id = request.form.get('brand_id')
        new_brand_name = request.form.get('new_brand_name', '').strip()
        gender = request.form.get('gender')
        category_id = request.form.get('category_id')
        source_url = request.form.get('source_url', '')
        screenshot_url = request.form.get('screenshot_url', '')
        
        # Handle new brand creation if needed
        if new_brand_name and not brand_id:
            cursor.execute("""
                INSERT INTO brands (name, default_unit, created_by)
                VALUES (%s, 'in', %s)
                RETURNING id
            """, (new_brand_name, session['admin_id']))
            brand_id = cursor.fetchone()['id']
            
            # Log brand creation
            log_admin_activity(
                cursor, 
                session['admin_id'], 
                'CREATE_BRAND', 
                'brands', 
                brand_id, 
                f'Created brand during size guide upload: {new_brand_name}',
                {'brand_name': new_brand_name}
            )
        
        # Create size guide
        cursor.execute("""
            INSERT INTO size_guides (brand_id, gender, category_id, fit_type, guide_level, unit, source_url, created_by)
            VALUES (%s, %s, %s, 'Regular', 'brand_level', 'in', %s, %s)
            RETURNING id
        """, (brand_id, gender, category_id, source_url, session['admin_id']))
        size_guide_id = cursor.fetchone()['id']
        
        # Process size entries from JSON data
        size_entries_json = request.form.get('size_entries', '[]')
        size_entries = json.loads(size_entries_json)
        
        for entry in size_entries:
            cursor.execute("""
                INSERT INTO size_guide_entries (
                    size_guide_id, size_label, chest_min, chest_max, chest_range,
                    sleeve_min, sleeve_max, sleeve_range, created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                size_guide_id, entry['size_label'], 
                entry.get('chest_min'), entry.get('chest_max'), entry.get('chest_range'),
                entry.get('sleeve_min'), entry.get('sleeve_max'), entry.get('sleeve_range'),
                session['admin_id']
            ))
        
        # Store raw source data in size_guides (migrated from raw_size_guides table)
        raw_text = f"Size guide for {new_brand_name or 'existing brand'} {gender} {category_id} - uploaded via admin interface"
        cursor.execute("""
            UPDATE size_guides 
            SET raw_source_text = %s, screenshot_path = %s, updated_by = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (raw_text, screenshot_url, session['admin_id'], size_guide_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Size guide uploaded successfully! {len(size_entries)} size entries added.', 'success')
        return redirect(url_for('admin_size_guides'))
        
    except Exception as e:
        flash(f'Error uploading size guide: {str(e)}', 'error')
        return redirect(url_for('admin_upload_size_guide'))

@app.route('/admin/api/check-brand/<brand_name>')
@require_admin_login
def api_check_brand(brand_name):
    """AJAX endpoint to check if brand exists"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT id, name FROM brands WHERE LOWER(name) = LOWER(%s)", (brand_name,))
        brand = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if brand:
            return jsonify({'exists': True, 'brand_id': brand['id'], 'brand_name': brand['name']})
        else:
            return jsonify({'exists': False})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 