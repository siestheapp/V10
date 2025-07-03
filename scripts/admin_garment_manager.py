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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 