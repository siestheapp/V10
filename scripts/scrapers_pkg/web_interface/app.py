#!/usr/bin/env python3
"""
Web interface for the product scraper system.
Provides a user-friendly dashboard to manage and monitor scrapers.
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from datetime import datetime, timedelta
import json
import threading
import time

# Add scrapers to Python path
scrapers_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scrapers_dir))

from config.database import db_config
from scrapers.banana_republic import BananaRepublicScraper
from utils.db_utils import db_manager

app = Flask(__name__)
app.secret_key = 'scraper-dashboard-secret-key-change-in-production'

# Global variables for tracking scraping status
scraping_status = {
    'is_running': False,
    'current_brand': None,
    'progress': 0,
    'last_update': None,
    'results': None
}

@app.route('/')
def dashboard():
    """Main dashboard page."""
    try:
        # Get recent scraping runs
        recent_runs = get_recent_scraping_runs()
        
        # Get scraped products count
        products_count = get_scraped_products_count()
        
        # Get database status
        db_status = test_database_connection()
        
        return render_template('dashboard.html', 
                             recent_runs=recent_runs,
                             products_count=products_count,
                             db_status=db_status,
                             scraping_status=scraping_status)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', 
                             recent_runs=[],
                             products_count=0,
                             db_status=False,
                             scraping_status=scraping_status)

@app.route('/scrapers')
def scrapers_page():
    """Scrapers management page."""
    available_scrapers = [
        {
            'name': 'Banana Republic',
            'id': 'banana_republic',
            'category': 'Men\'s Casual Shirts',
            'status': 'Ready',
            'last_run': get_last_run_time('banana_republic')
        }
    ]
    
    return render_template('scrapers.html', 
                         scrapers=available_scrapers,
                         scraping_status=scraping_status)

@app.route('/products')
def products_page():
    """View scraped products."""
    try:
        products = get_scraped_products(limit=50)
        brands = get_available_brands()
        
        return render_template('products.html', 
                             products=products,
                             brands=brands)
    except Exception as e:
        flash(f'Error loading products: {str(e)}', 'error')
        return render_template('products.html', 
                             products=[],
                             brands=[])

@app.route('/api/start_scraper', methods=['POST'])
def start_scraper():
    """Start a scraper via API."""
    try:
        data = request.get_json()
        scraper_id = data.get('scraper_id')
        max_pages = data.get('max_pages', 3)
        
        if scraping_status['is_running']:
            return jsonify({'success': False, 'message': 'A scraper is already running'})
        
        if scraper_id == 'banana_republic':
            # Start scraping in background thread
            thread = threading.Thread(
                target=run_banana_republic_scraper,
                args=(max_pages,)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({'success': True, 'message': 'Scraper started successfully'})
        else:
            return jsonify({'success': False, 'message': 'Unknown scraper'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/scraping_status')
def get_scraping_status():
    """Get current scraping status."""
    return jsonify(scraping_status)

@app.route('/api/stop_scraper', methods=['POST'])
def stop_scraper():
    """Stop the current scraper."""
    global scraping_status
    scraping_status['is_running'] = False
    return jsonify({'success': True, 'message': 'Scraper stop requested'})

@app.route('/api/test_connection')
def test_connection():
    """Test database connection."""
    try:
        status = test_database_connection()
        return jsonify({'success': status, 'message': 'Connected' if status else 'Failed'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products')
def api_products():
    """Get products via API."""
    try:
        brand = request.args.get('brand', '')
        limit = int(request.args.get('limit', 20))
        
        products = get_scraped_products(brand=brand, limit=limit)
        return jsonify({'success': True, 'products': products})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def run_banana_republic_scraper(max_pages):
    """Run Banana Republic scraper in background."""
    global scraping_status
    
    try:
        scraping_status.update({
            'is_running': True,
            'current_brand': 'Banana Republic',
            'progress': 0,
            'last_update': datetime.now().isoformat(),
            'results': None
        })
        
        scraper = BananaRepublicScraper()
        
        # Update progress
        scraping_status['progress'] = 25
        scraping_status['last_update'] = datetime.now().isoformat()
        
        # Run scraping session
        result = scraper.run_scraping_session(
            category="Casual Shirts",
            target_url="https://bananarepublic.gap.com/browse/men/casual-shirts?cid=44873",
            max_pages=max_pages
        )
        
        # Update final status
        scraping_status.update({
            'is_running': False,
            'progress': 100,
            'last_update': datetime.now().isoformat(),
            'results': result
        })
        
    except Exception as e:
        scraping_status.update({
            'is_running': False,
            'progress': 0,
            'last_update': datetime.now().isoformat(),
            'results': {'status': 'failed', 'error': str(e)}
        })

def test_database_connection():
    """Test database connectivity."""
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False

def get_recent_scraping_runs(limit=10):
    """Get recent scraping runs."""
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sr.id,
                b.name as brand_name,
                c.name as category_name,
                sr.products_found,
                sr.products_added,
                sr.products_updated,
                sr.errors_count,
                sr.run_duration_seconds,
                sr.started_at,
                sr.status
            FROM product_catalog.scraping_runs sr
            LEFT JOIN public.brands b ON sr.brand_id = b.id
            LEFT JOIN public.categories c ON sr.category_id = c.id
            ORDER BY sr.started_at DESC
            LIMIT %s
        """, (limit,))
        
        runs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(run) for run in runs]
    except Exception as e:
        print(f"Error getting scraping runs: {e}")
        return []

def get_scraped_products_count():
    """Get count of scraped products."""
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM public.products 
            WHERE source_type = 'scraped'
        """)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result['count'] if result else 0
    except Exception:
        return 0

def get_scraped_products(brand='', limit=50):
    """Get scraped products."""
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                p.id,
                p.name,
                b.name as brand_name,
                p.price,
                p.original_price,
                p.discount_percentage,
                p.sizes_available,
                p.image_url,
                p.product_url,
                p.last_scraped
            FROM public.products p
            LEFT JOIN public.brands b ON p.brand_id = b.id
            WHERE p.source_type = 'scraped'
        """
        
        params = []
        if brand:
            query += " AND b.name ILIKE %s"
            params.append(f"%{brand}%")
        
        query += " ORDER BY p.last_scraped DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(product) for product in products]
    except Exception as e:
        print(f"Error getting products: {e}")
        return []

def get_available_brands():
    """Get available brands."""
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM public.brands ORDER BY name")
        brands = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [brand['name'] for brand in brands]
    except Exception:
        return []

def get_last_run_time(scraper_id):
    """Get last run time for a scraper."""
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(started_at) as last_run
            FROM product_catalog.scraping_runs sr
            LEFT JOIN public.brands b ON sr.brand_id = b.id
            WHERE b.name ILIKE %s
        """, (f"%{scraper_id.replace('_', ' ')}%",))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result['last_run']:
            return result['last_run'].strftime('%Y-%m-%d %H:%M')
        return 'Never'
    except Exception:
        return 'Unknown'

if __name__ == '__main__':
    print("🚀 Starting Scraper Web Interface...")
    print("📱 Open your browser to: http://localhost:5003")
    print("🛑 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5003, debug=True)
