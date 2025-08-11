#!/usr/bin/env python3
"""
Admin User Data Viewer
Simple Flask web interface to view all user measurements and feedback in one place
For debugging and analysis purposes only
"""

from flask import Flask, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": 6543,
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12"
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
@app.route('/user/<int:user_id>')
def user_data(user_id=1):
    """Display comprehensive user data"""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user info
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        
        # Get user garments - simplified query
        cur.execute("""
            SELECT 
                ug.id as garment_id,
                b.name as brand,
                ug.product_name,
                ug.size_label,
                ug.fit_feedback,
                ug.owns_garment,
                ug.created_at as garment_added,
                
                -- Size guide measurements
                sge.measurement_type,
                sge.min_value,
                sge.max_value,
                
                -- Get all feedback for this garment
                (SELECT STRING_AGG(
                    ugf.dimension || ': ' || fc.feedback_text, 
                    ', ' ORDER BY ugf.dimension
                ) FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id
                ) as all_feedback
                
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
            WHERE ug.user_id = %s
            ORDER BY b.name, ug.product_name
        """, (user_id,))
        
        # Get positive feedback summary - chest measurements with positive feedback
        cur.execute("""
            SELECT 
                'chest' as dimension,
                MIN(sge.min_value) as overall_min,
                MAX(sge.max_value) as overall_max,
                COUNT(DISTINCT ug.id) as garment_count,
                STRING_AGG(DISTINCT fc.feedback_text, ', ') as feedback_types
            FROM user_garments ug
            JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
            JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id AND ugf.dimension = 'chest'
            JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
            WHERE ug.user_id = %s 
            AND ug.owns_garment = true
            AND fc.feedback_text IN ('Good Fit', 'Tight but I Like It', 'Loose but I Like It', 'Slightly Loose')
            AND sge.measurement_type = 'chest'
        """, (user_id,))
        positive_feedback_summary = cur.fetchall()
        
        garments_raw = cur.fetchall()
        
        # Group measurements by garment
        garments = {}
        for row in garments_raw:
            gid = row['garment_id']
            if gid not in garments:
                garments[gid] = {
                    'id': gid,
                    'brand': row['brand'],
                    'product_name': row['product_name'],
                    'size_label': row['size_label'],
                    'fit_feedback': row['fit_feedback'],
                    'all_feedback': row['all_feedback'],
                    'owns_garment': row['owns_garment'],
                    'garment_added': row['garment_added'],
                    'measurements': {}
                }
            
            if row['measurement_type']:
                garments[gid]['measurements'][row['measurement_type']] = {
                    'min': row['min_value'],
                    'max': row['max_value']
                }
        
        garments = list(garments.values())
        
        # Get fit zones from both tables
        cur.execute("SELECT * FROM user_fit_zones WHERE user_id = %s ORDER BY dimension", (user_id,))
        user_fit_zones = cur.fetchall()
        
        cur.execute("SELECT * FROM fit_zones WHERE user_id = %s ORDER BY dimension, fit_type", (user_id,))
        fit_zones = cur.fetchall()
        
        # Get body measurements if any
        cur.execute("SELECT * FROM body_measurements WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        body_measurements = cur.fetchall()
        
        conn.close()
        
        # Create feedback details lookup - simplified for now
        feedback_lookup = {}
        
        return render_template_string(HTML_TEMPLATE, 
            user=user,
            garments=garments,
            user_fit_zones=user_fit_zones,
            fit_zones=fit_zones,
            body_measurements=body_measurements,
            positive_feedback_summary=positive_feedback_summary,
            feedback_lookup={},
            user_id=user_id,
            datetime=datetime
        )
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>User {{ user_id }} Data Viewer - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; }
        .section { background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .section h3 { color: #666; margin-top: 25px; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        tr:hover { background: #f8f9fa; }
        .garment { border-left: 4px solid #007bff; margin: 15px 0; padding: 15px; background: #f8f9fa; }
        .garment-header { font-weight: bold; color: #007bff; font-size: 16px; }
        .feedback { color: #28a745; font-weight: bold; }
        .feedback.negative { color: #dc3545; }
        .measurements { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 10px 0; }
        .measurement { background: white; padding: 10px; border-radius: 4px; border: 1px solid #ddd; }
        .fit-zone { background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 4px; }
        .fit-zone.tight { background: #ffebee; }
        .fit-zone.relaxed { background: #e8f5e8; }
        .no-data { color: #999; font-style: italic; }
        .owns-badge { background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .not-owns-badge { background: #6c757d; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }
        .summary-card { background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3; }
        .summary-card h4 { margin: 0 0 10px 0; color: #1976d2; }
        .summary-range { font-size: 18px; font-weight: bold; color: #0d47a1; }
        .summary-meta { font-size: 12px; color: #666; margin-top: 5px; }
        .missing-feedback { background: #fff3cd; border: 1px solid #ffeaa7; padding: 8px; border-radius: 4px; margin: 5px 0; }
        .missing-feedback strong { color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <h1>👤 User {{ user_id }} Data Viewer</h1>
        <p><strong>Admin Tool:</strong> Comprehensive view of user measurements and feedback for debugging</p>
        
        {% if user %}
        <div class="section">
            <h2>📋 User Profile</h2>
            <table>
                <tr><th>Email</th><td>{{ user.email }}</td></tr>
                <tr><th>Gender</th><td>{{ user.gender }}</td></tr>
                <tr><th>Height</th><td>{{ user.height_in }}"</td></tr>
                <tr><th>Preferred Units</th><td>{{ user.preferred_units }}</td></tr>
                <tr><th>Created</th><td>{{ user.created_at }}</td></tr>
            </table>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>📊 Positive Feedback Summary</h2>
            <p><em>Min-Max ranges across all garments with positive feedback (Good Fit, Tight/Loose but I Like It, etc.)</em></p>
            
            {% if positive_feedback_summary %}
            <div class="summary-grid">
                {% for summary in positive_feedback_summary %}
                <div class="summary-card">
                    <h4>{{ summary.dimension.title() }}</h4>
                    <div class="summary-range">{{ summary.overall_min }}" - {{ summary.overall_max }}"</div>
                    <div class="summary-meta">
                        {{ summary.garment_count }} garments<br>
                        Feedback: {{ summary.feedback_types or 'Overall positive' }}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p class="no-data">No positive feedback data available</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>👕 Garments & Measurements ({{ garments|length }} total)</h2>
            {% for garment in garments %}
            <div class="garment">
                <div class="garment-header">
                    {{ garment.brand }} - {{ garment.product_name }} (Size {{ garment.size_label }})
                    {% if garment.owns_garment %}
                        <span class="owns-badge">OWNS</span>
                    {% else %}
                        <span class="not-owns-badge">SCANNED</span>
                    {% endif %}
                </div>
                
                <p><strong>Overall Feedback:</strong> 
                    <span class="feedback {% if 'Tight' in (garment.fit_feedback or '') or 'Loose' in (garment.fit_feedback or '') %}negative{% endif %}">
                        {{ garment.fit_feedback or 'None' }}
                    </span>
                </p>
                
                {% if garment.all_feedback %}
                <p><strong>All Dimensional Feedback:</strong> <span class="feedback">{{ garment.all_feedback }}</span></p>
                {% endif %}
                
                <p><strong>Added:</strong> {{ garment.garment_added.strftime('%Y-%m-%d %H:%M') if garment.garment_added else 'Unknown' }}</p>
                
                {% if garment.measurements %}
                <div class="measurements">
                    {% for dim, meas in garment.measurements.items() %}
                    <div class="measurement">
                        <strong>{{ dim.title() }}:</strong><br>
                        {% if meas.min and meas.max %}
                            {{ meas.min }}" - {{ meas.max }}"
                        {% elif meas.range %}
                            {{ meas.range }}
                        {% else %}
                            <span class="no-data">No data</span>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <p class="no-data">No measurements available</p>
                {% endif %}
                
                {% set feedback_detail = feedback_lookup.get(garment.id) %}
                {% if feedback_detail and feedback_detail.missing_feedback_dimensions %}
                <div class="missing-feedback">
                    <strong>⚠️ Missing Feedback:</strong> User didn't provide feedback for: 
                    {{ feedback_detail.missing_feedback_dimensions | join(', ') }}
                    <br><small>Available dimensions: {{ feedback_detail.available_dimensions | join(', ') }}</small>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        
        <div class="section">
            <h2>📏 Current Fit Zones</h2>
            
            <h3>user_fit_zones table ({{ user_fit_zones|length }} records)</h3>
            {% if user_fit_zones %}
            {% for zone in user_fit_zones %}
            <div class="fit-zone">
                <strong>{{ zone.dimension.title() }}:</strong>
                {% if zone.tight_min %}
                    <span class="fit-zone tight">Tight: {{ zone.tight_min }}" - {{ zone.tight_max }}"</span>
                {% endif %}
                <span class="fit-zone">Good: {{ zone.good_min }}" - {{ zone.good_max }}"</span>
                {% if zone.relaxed_min %}
                    <span class="fit-zone relaxed">Relaxed: {{ zone.relaxed_min }}" - {{ zone.relaxed_max }}"</span>
                {% endif %}
                <br><small>Confidence: {{ zone.confidence_score }}, Data points: {{ zone.data_points_count }}, Updated: {{ zone.last_updated.strftime('%Y-%m-%d %H:%M') if zone.last_updated else 'Never' }}</small>
            </div>
            {% endfor %}
            {% else %}
            <p class="no-data">No fit zones in user_fit_zones table</p>
            {% endif %}
            
            <h3>fit_zones table ({{ fit_zones|length }} records)</h3>
            {% if fit_zones %}
            {% for zone in fit_zones %}
            <div class="fit-zone {% if zone.fit_type == 'tight' %}tight{% elif zone.fit_type == 'relaxed' %}relaxed{% endif %}">
                <strong>{{ zone.dimension.title() }} {{ zone.fit_type.title() }}:</strong> {{ zone.min_value }}" - {{ zone.max_value }}"
                <br><small>Created: {{ zone.created_at.strftime('%Y-%m-%d %H:%M') if zone.created_at else 'Unknown' }}, Unit: {{ zone.unit }}</small>
            </div>
            {% endfor %}
            {% else %}
            <p class="no-data">No fit zones in fit_zones table</p>
            {% endif %}
        </div>
        
        {% if body_measurements %}
        <div class="section">
            <h2>📐 Body Measurements ({{ body_measurements|length }} records)</h2>
            {% for bm in body_measurements %}
            <div class="fit-zone">
                <strong>Measurement Set {{ loop.index }}:</strong>
                Chest: {{ bm.chest or 'N/A' }}", Waist: {{ bm.waist or 'N/A' }}", Neck: {{ bm.neck or 'N/A' }}", Sleeve: {{ bm.sleeve or 'N/A' }}", Hip: {{ bm.hip or 'N/A' }}"
                <br><small>Source: {{ bm.source or 'Unknown' }}, Confidence: {{ bm.confidence_score or 'N/A' }}, Created: {{ bm.created_at.strftime('%Y-%m-%d %H:%M') if bm.created_at else 'Unknown' }}</small>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="section">
            <h2>🔧 Debug Actions</h2>
            <p><a href="/user/1">View User 1</a> | <a href="/">Refresh Current User</a></p>
            <p><small>Generated at {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</small></p>
        </div>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    print("🚀 Starting Admin User Data Viewer...")
    print("📊 View at: http://localhost:5003")
    print("👤 Default user: http://localhost:5003/user/1")
    app.run(debug=True, port=5003)
