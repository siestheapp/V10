"""
Updates needed for app.py to use the unified product fetcher
Replace the relevant sections in app.py with these
"""

# REPLACE THIS SECTION IN app.py (around line 1485-1520):
# OLD: Using JCrewDynamicFetcher
# NEW: Using UnifiedProductFetcher

def updated_tryon_start_section():
    """
    Replace the product fetching logic in /tryon/start endpoint
    """
    code = '''
        # Initialize variables
        product_data = None
        fit_variations = {}
        
        # Use unified fetcher for ALL brands
        from unified_product_fetcher import UnifiedProductFetcher
        from category_normalizer import CategoryNormalizer
        
        fetcher = UnifiedProductFetcher()
        product_data = fetcher.fetch_product(product_url)
        
        if product_data:
            print(f"✅ Found product in database: {product_data['product_name']}")
            
            # Normalize the category for cross-brand consistency
            normalized_category = CategoryNormalizer.normalize_category(
                product_data['brand'],
                product_data.get('category', '')
            )
            
            # Format response with normalized data
            response_data = {
                "success": True,
                "product": {
                    "code": product_data['product_code'],
                    "name": product_data['product_name'],
                    "brand": product_data['brand'],
                    "category": product_data.get('category'),
                    "normalized_category": normalized_category,
                    "subcategory": product_data.get('subcategory'),
                    "url": product_url,
                    "materials": product_data.get('materials'),
                    "care_instructions": product_data.get('care_instructions'),
                    "fit_information": product_data.get('fit_information'),
                    "variants": product_data.get('variants', [])
                },
                "brand": brand_info["brand_name"],
                "brand_id": brand_info["brand_id"],
                "session_id": session_id
            }
        else:
            # Product not found in database
            print(f"❌ Product not found in database for URL: {product_url}")
            
            response_data = {
                "success": False,
                "error": "Product not found. This product hasn't been loaded into our system yet.",
                "brand": brand_info["brand_name"],
                "brand_id": brand_info["brand_id"]
            }
    '''
    return code

# REPLACE THIS SECTION IN app.py (around line 1610-1620):
# OLD: Using JCrewProductFetcher for images
# NEW: Using UnifiedProductFetcher

def updated_image_fetching_section():
    """
    Replace the image fetching logic
    """
    code = '''
        # Get product image from unified fetcher
        product_image = ""
        from unified_product_fetcher import UnifiedProductFetcher
        
        fetcher = UnifiedProductFetcher()
        product_data = fetcher.fetch_product(product_url)
        
        if product_data:
            # Check variants for images or use a default
            if product_data.get('variants'):
                # Use first variant's image if available
                product_image = product_data['variants'][0].get('image_url', '')
            
            # Store the product name from database
            product_name = product_data.get('product_name', product_name)
    '''
    return code

# NEW ENDPOINT: Cross-brand search
def new_cross_brand_search_endpoint():
    """
    Add this new endpoint for searching across brands
    """
    code = '''
@app.get("/products/search")
async def search_products(category: str = None, brand: str = None, normalized_category: str = None):
    """
    Search products across brands
    
    Query params:
    - category: Brand-specific category (e.g., "Bowery")
    - brand: Specific brand to filter
    - normalized_category: Cross-brand category (e.g., "FORMAL_SHIRTS")
    """
    try:
        from category_normalizer import CategoryNormalizer
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        
        if normalized_category:
            # Search across all brands in normalized category
            results = CategoryNormalizer.search_across_brands(
                normalized_category, 
                conn
            )
        else:
            # Regular search
            cur = conn.cursor()
            
            query = """
                SELECT 
                    pm.id,
                    pm.product_code,
                    pm.base_name as product_name,
                    b.name as brand,
                    pm.category,
                    pm.subcategory
                FROM product_master pm
                JOIN brands b ON pm.brand_id = b.id
                WHERE 1=1
            """
            params = []
            
            if brand:
                query += " AND b.name = %s"
                params.append(brand)
            
            if category:
                query += " AND pm.category = %s"
                params.append(category)
            
            query += " ORDER BY b.name, pm.base_name"
            
            cur.execute(query, params)
            results = cur.fetchall()
            cur.close()
        
        conn.close()
        
        return {
            "success": True,
            "count": len(results),
            "products": results
        }
        
    except Exception as e:
        print(f"Error searching products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    '''
    return code

print("""
INTEGRATION INSTRUCTIONS:
========================

1. In app.py, find the /tryon/start endpoint (around line 1460)
   - Replace the J.Crew-specific fetching logic with unified fetcher
   - Remove imports for JCrewDynamicFetcher, JCrewProductFetcher

2. Add the new /products/search endpoint for cross-brand search

3. Update imports at the top of app.py:
   from unified_product_fetcher import UnifiedProductFetcher
   from category_normalizer import CategoryNormalizer

4. Test with different brand URLs:
   - J.Crew: https://www.jcrew.com/p/MP694
   - Banana Republic: https://bananarepublic.com/products/000768592
   - Theory: https://theory.com/mens/shirts/J0901503.html

5. The app will now:
   - Check product_master for ANY brand
   - Return normalized categories for filtering
   - Say "Product not found" if not in database
   - No real-time scraping
""")
