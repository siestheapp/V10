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
            subcategory_name = request.form.get('subcategory_name', '').strip()
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
            
            # Find matching size guide and entry
            size_guide_id = None
            size_guide_entry_id = None
            
            # Look up size guide based on brand, category, gender, fit_type
            if subcategory_id:
                cursor.execute("""
                    SELECT id FROM size_guides 
                    WHERE brand_id = %s AND category_id = %s AND gender = %s 
                    AND (fit_type = %s OR fit_type = 'Unspecified')
                    AND subcategory_id = %s
                    ORDER BY CASE WHEN fit_type = %s THEN 1 ELSE 2 END
                    LIMIT 1
                """, (brand_id, category_id, gender, fit_type, subcategory_id, fit_type))
            else:
                cursor.execute("""
                    SELECT id FROM size_guides 
                    WHERE brand_id = %s AND category_id = %s AND gender = %s 
                    AND (fit_type = %s OR fit_type = 'Unspecified')
                    AND subcategory_id IS NULL
                    ORDER BY CASE WHEN fit_type = %s THEN 1 ELSE 2 END
                    LIMIT 1
                """, (brand_id, category_id, gender, fit_type, fit_type))
            
            size_guide_result = cursor.fetchone()
            if size_guide_result:
                size_guide_id = size_guide_result[0]
                
                # Look up specific size entry
                cursor.execute("""
                    SELECT id FROM size_guide_entries 
                    WHERE size_guide_id = %s AND size_label = %s
                    LIMIT 1
                """, (size_guide_id, size_label))
                
                entry_result = cursor.fetchone()
                if entry_result:
                    size_guide_entry_id = entry_result[0]

            # Insert garment with size guide links
            cursor.execute("""
                INSERT INTO user_garments (
                    user_id, brand_id, category_id, subcategory_id, gender, 
                    size_label, fit_type, unit, product_name, product_url, owns_garment,
                    size_guide_id, size_guide_entry_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'in', %s, %s, true, %s, %s)
                RETURNING id
            """, (user_id, brand_id, category_id, subcategory_id, gender, 
                  size_label, fit_type, product_name, product_url, size_guide_id, size_guide_entry_id))
            
            garment_id = cursor.fetchone()[0]
            
            # Log the garment addition
            log_garment_addition(user_id, brand_name, product_name, size_label, garment_id)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Create success message with measurement linking status
            base_message = f'Garment "{product_name}" added successfully!' if product_name else 'Garment added successfully!'
            
            if size_guide_entry_id:
                flash(f'{base_message} ✅ Linked to size guide measurements for accurate fit recommendations.', 'success')
            elif size_guide_id:
                flash(f'{base_message} ⚠️ Size guide found but your specific size ({size_label}) not available in our database.', 'warning')
            else:
                flash(f'{base_message} ⚠️ No size guide found for this brand/category combination. Fit recommendations may be limited.', 'warning')
            
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

    # Determine default brand, category, gender, fit_type for initial size list
    default_brand_id = brands[0]['id'] if brands else None
    default_category_id = categories[0]['id'] if categories else None
    default_gender = 'Male'  # or another default if you prefer
    default_fit_type = 'Regular'  # or another default if you prefer
    available_sizes = []
    if default_brand_id and default_category_id:
        cursor.execute("""
            SELECT sge.size_label FROM size_guides sg
            JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
            WHERE sg.brand_id = %s AND sg.category_id = %s AND sg.gender = %s AND (sg.fit_type = %s OR sg.fit_type = 'Unspecified')
            ORDER BY sge.size_label
        """, (default_brand_id, default_category_id, default_gender, default_fit_type))
        available_sizes = [row['size_label'] for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    
    return render_template('add_garment.html', users=users, brands=brands, categories=categories, subcategories=subcategories, available_sizes=available_sizes)

@app.route('/garment/<int:garment_id>')
def view_garment(garment_id):
    """View a specific garment and its feedback"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get garment details with measurements
    cursor.execute("""
        SELECT ug.*, b.name as brand_name, c.name as category_name, 
               sc.name as subcategory_name, u.email as user_email,
               sge.chest_min, sge.chest_max, sge.chest_range,
               sge.waist_min, sge.waist_max, sge.waist_range,
               sge.sleeve_min, sge.sleeve_max, sge.sleeve_range,
               sge.neck_min, sge.neck_max, sge.neck_range,
               sge.hip_min, sge.hip_max, sge.hip_range,
               sge.center_back_length
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        JOIN categories c ON ug.category_id = c.id
        LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
        JOIN users u ON ug.user_id = u.id
        LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
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

@app.route('/progressive_feedback/<int:garment_id>')
def progressive_feedback(garment_id):
    """Progressive feedback interface for a garment"""
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
    
    # Get overall fit codes (5-point satisfaction scale)
    cursor.execute("""
        SELECT id, feedback_text FROM feedback_codes 
        WHERE feedback_text IN ('Good Fit', 'Tight but I Like It', 'Loose but I Like It', 'Too Tight', 'Too Loose')
        ORDER BY 
            CASE feedback_text
                WHEN 'Good Fit' THEN 1
                WHEN 'Tight but I Like It' THEN 2
                WHEN 'Loose but I Like It' THEN 3
                WHEN 'Too Tight' THEN 4
                WHEN 'Too Loose' THEN 5
            END
    """)
    overall_fit_codes = cursor.fetchall()
    
    # Get dimension-specific fit codes (same 5-point satisfaction scale)
    cursor.execute("""
        SELECT id, feedback_text FROM feedback_codes 
        WHERE feedback_text IN ('Good Fit', 'Tight but I Like It', 'Loose but I Like It', 'Too Tight', 'Too Loose')
        ORDER BY 
            CASE feedback_text
                WHEN 'Good Fit' THEN 1
                WHEN 'Tight but I Like It' THEN 2
                WHEN 'Loose but I Like It' THEN 3
                WHEN 'Too Tight' THEN 4
                WHEN 'Too Loose' THEN 5
            END
    """)
    dimension_fit_codes = cursor.fetchall()
    
    # Get available dimensions based on size guide measurements
    available_dimensions = []
    if garment['size_guide_id']:
        # Check what dimensions exist across ALL sizes for this brand
        cursor.execute("""
            SELECT 
                CASE WHEN COUNT(CASE WHEN chest_min IS NOT NULL OR chest_max IS NOT NULL OR chest_range IS NOT NULL THEN 1 END) > 0 THEN 'chest' END as chest,
                CASE WHEN COUNT(CASE WHEN waist_min IS NOT NULL OR waist_max IS NOT NULL OR waist_range IS NOT NULL THEN 1 END) > 0 THEN 'waist' END as waist,
                CASE WHEN COUNT(CASE WHEN sleeve_min IS NOT NULL OR sleeve_max IS NOT NULL OR sleeve_range IS NOT NULL THEN 1 END) > 0 THEN 'sleeve' END as sleeve,
                CASE WHEN COUNT(CASE WHEN neck_min IS NOT NULL OR neck_max IS NOT NULL OR neck_range IS NOT NULL THEN 1 END) > 0 THEN 'neck' END as neck,
                CASE WHEN COUNT(CASE WHEN hip_min IS NOT NULL OR hip_max IS NOT NULL OR hip_range IS NOT NULL THEN 1 END) > 0 THEN 'hip' END as hip,
                CASE WHEN COUNT(CASE WHEN center_back_length IS NOT NULL THEN 1 END) > 0 THEN 'length' END as length
            FROM size_guide_entries 
            WHERE size_guide_id = %s
        """, (garment['size_guide_id'],))
        
        dimensions_result = cursor.fetchone()
        if dimensions_result:
            # Add all dimensions that exist for this brand (only non-None values)
            for dim in dimensions_result.values():
                if dim is not None:
                    available_dimensions.append(dim)
    
    # Default dimensions if no size guide or no measurements
    if not available_dimensions:
        available_dimensions = ['chest', 'waist']
    
    cursor.close()
    conn.close()
    
    return render_template('progressive_feedback.html', 
                         garment=garment,
                         overall_fit_codes=overall_fit_codes,
                         dimension_fit_codes=dimension_fit_codes,
                         available_dimensions=available_dimensions)

@app.route('/submit_progressive_feedback/<int:garment_id>', methods=['POST'])
def submit_progressive_feedback(garment_id):
    """Submit progressive feedback for a garment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user_id for logging
        cursor.execute("SELECT user_id FROM user_garments WHERE id = %s", (garment_id,))
        user_id = cursor.fetchone()[0]
        
        # Get overall fit feedback
        overall_fit_code_id = request.form.get('overall_fit')
        if not overall_fit_code_id:
            return jsonify({'success': False, 'message': 'Overall fit is required'})
        
        # Insert overall feedback
        cursor.execute("""
            INSERT INTO user_garment_feedback (user_garment_id, dimension, feedback_code_id)
            VALUES (%s, %s, %s)
        """, (garment_id, 'overall', overall_fit_code_id))
        
        # Get overall feedback text for logging
        cursor.execute("SELECT feedback_text FROM feedback_codes WHERE id = %s", (overall_fit_code_id,))
        overall_feedback_text = cursor.fetchone()[0]
        
        # Log overall feedback
        log_feedback_submission(user_id, garment_id, 'overall', overall_feedback_text)
        
        # Process dimension-specific feedback (optional - user can leave blank)
        dimensions = ['chest', 'waist', 'sleeve', 'neck', 'hip', 'length']
        for dimension in dimensions:
            dimension_feedback = request.form.get(f'dimension_{dimension}')
            if dimension_feedback:  # Only process if user selected something
                # Insert dimension feedback
                cursor.execute("""
                    INSERT INTO user_garment_feedback (user_garment_id, dimension, feedback_code_id)
                    VALUES (%s, %s, %s)
                """, (garment_id, dimension, dimension_feedback))
                
                # Get dimension feedback text for logging
                cursor.execute("SELECT feedback_text FROM feedback_codes WHERE id = %s", (dimension_feedback,))
                dimension_feedback_text = cursor.fetchone()[0]
                
                # Log dimension feedback
                log_feedback_submission(user_id, garment_id, dimension, dimension_feedback_text)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Progressive feedback submitted successfully!',
            'redirect_url': url_for('view_garment', garment_id=garment_id)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error submitting feedback: {str(e)}'})

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

@app.route('/get_sizes')
def get_sizes():
    brand_name = request.args.get('brand_name')
    category_name = request.args.get('category_name')
    gender = request.args.get('gender')
    # fit_type is ignored
    subcategory_name = request.args.get('subcategory_name')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get brand ID
    cursor.execute("SELECT id FROM brands WHERE name = %s", (brand_name,))
    brand_result = cursor.fetchone()
    if not brand_result:
        return jsonify({'sizes': []})
    brand_id = brand_result['id']

    # Get category ID
    cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
    category_result = cursor.fetchone()
    if not category_result:
        return jsonify({'sizes': []})
    category_id = category_result['id']

    # Get subcategory ID if provided
    subcategory_id = None
    if subcategory_name:
        cursor.execute("SELECT id FROM subcategories WHERE name = %s", (subcategory_name,))
        subcategory_result = cursor.fetchone()
        if subcategory_result:
            subcategory_id = subcategory_result['id']

    # Find matching size guide (ignore fit_type)
    if subcategory_id:
        cursor.execute("""
            SELECT id FROM size_guides 
            WHERE brand_id = %s AND category_id = %s AND gender = %s 
            AND subcategory_id = %s
            ORDER BY id LIMIT 1
        """, (brand_id, category_id, gender, subcategory_id))
    else:
        cursor.execute("""
            SELECT id FROM size_guides 
            WHERE brand_id = %s AND category_id = %s AND gender = %s 
            AND subcategory_id IS NULL
            ORDER BY id LIMIT 1
        """, (brand_id, category_id, gender))
    size_guide_result = cursor.fetchone()
    sizes = []
    if size_guide_result:
        size_guide_id = size_guide_result['id']
        cursor.execute("SELECT size_label FROM size_guide_entries WHERE size_guide_id = %s ORDER BY size_label", (size_guide_id,))
        sizes = [row['size_label'] for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return jsonify({'sizes': sizes})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 