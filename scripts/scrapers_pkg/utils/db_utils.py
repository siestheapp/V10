"""Database utilities for scrapers."""

from typing import Optional, Dict, Any, List
import json
from datetime import datetime

from config.database import db_config
from models.product import ScrapedProduct, ScrapingRun

class DatabaseManager:
    """Manages database operations for scrapers."""
    
    def __init__(self):
        self.db_config = db_config
    
    def get_brand_id(self, brand_name: str) -> Optional[int]:
        """Get brand ID from brand name."""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id FROM public.brands WHERE name ILIKE %s",
                (brand_name,)
            )
            result = cursor.fetchone()
            return result['id'] if result else None
        finally:
            cursor.close()
            conn.close()
    
    def get_category_id(self, category_name: str) -> Optional[int]:
        """Get category ID from category name."""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id FROM public.categories WHERE name ILIKE %s",
                (category_name,)
            )
            result = cursor.fetchone()
            return result['id'] if result else None
        finally:
            cursor.close()
            conn.close()
    
    def create_scraping_run(self, run: ScrapingRun) -> int:
        """Create a new scraping run record and return its ID."""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        try:
            brand_id = self.get_brand_id(run.brand_name)
            category_id = self.get_category_id(run.category)
            
            cursor.execute("""
                INSERT INTO product_catalog.scraping_runs (
                    brand_id, category_id, target_url, scraper_version,
                    products_found, products_added, products_updated, errors_count,
                    started_at, status, error_details
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """, (
                brand_id, category_id, run.target_url, run.scraper_version,
                run.products_found, run.products_added, run.products_updated, 
                run.errors_count, run.started_at, run.status, 
                json.dumps(run.error_details)
            ))
            
            run_id = cursor.fetchone()['id']
            conn.commit()
            return run_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def update_scraping_run(self, run_id: int, run: ScrapingRun):
        """Update an existing scraping run."""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE product_catalog.scraping_runs SET
                    products_found = %s,
                    products_added = %s,
                    products_updated = %s,
                    errors_count = %s,
                    completed_at = %s,
                    run_duration_seconds = %s,
                    status = %s,
                    error_details = %s
                WHERE id = %s
            """, (
                run.products_found, run.products_added, run.products_updated,
                run.errors_count, run.completed_at, run.run_duration_seconds,
                run.status, json.dumps(run.error_details), run_id
            ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def save_product(self, product: ScrapedProduct) -> int:
        """Save or update a scraped product."""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get brand and category IDs
            brand_id = self.get_brand_id(product.brand_name)
            category_id = self.get_category_id(product.category) if product.category else None
            
            if not brand_id:
                raise ValueError(f"Brand '{product.brand_name}' not found in database")
            
            # Check if product exists
            cursor.execute("""
                SELECT id FROM public.products 
                WHERE brand_id = %s AND external_id = %s
            """, (brand_id, product.external_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing product
                cursor.execute("""
                    UPDATE public.products SET
                        name = %s,
                        description = %s,
                        price = %s,
                        original_price = %s,
                        discount_percentage = %s,
                        image_url = %s,
                        product_url = %s,
                        material = %s,
                        fit_type = %s,
                        sizes_available = %s,
                        colors_available = %s,
                        scraping_metadata = %s,
                        last_scraped = %s
                    WHERE id = %s
                    RETURNING id
                """, (
                    product.name, product.description, product.price,
                    product.original_price, product.discount_percentage,
                    product.primary_image_url, product.product_url,
                    product.material, product.fit_type,
                    json.dumps(product.sizes_available),
                    json.dumps(product.colors_available),
                    json.dumps(product.scraping_metadata),
                    product.scraped_at, existing['id']
                ))
                
                product_id = existing['id']
                action = 'updated'
                
            else:
                # Insert new product
                cursor.execute("""
                    INSERT INTO public.products (
                        brand_id, category_id, name, description, price,
                        original_price, discount_percentage, image_url, product_url,
                        external_id, source_type, material, fit_type,
                        sizes_available, colors_available, scraping_metadata,
                        last_scraped, is_active
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """, (
                    brand_id, category_id, product.name, product.description,
                    product.price, product.original_price, product.discount_percentage,
                    product.primary_image_url, product.product_url,
                    product.external_id, 'scraped', product.material, product.fit_type,
                    json.dumps(product.sizes_available),
                    json.dumps(product.colors_available),
                    json.dumps(product.scraping_metadata),
                    product.scraped_at, True
                ))
                
                product_id = cursor.fetchone()['id']
                action = 'created'
            
            conn.commit()
            return product_id, action
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def log_product_scraping(self, run_id: int, product_id: Optional[int], 
                           external_id: str, product_url: str, 
                           action_type: str, error_message: Optional[str] = None,
                           scraped_data: Optional[Dict[str, Any]] = None):
        """Log individual product scraping attempts."""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO product_catalog.product_scraping_log (
                    scraping_run_id, product_id, external_id, product_url,
                    action_type, error_message, scraped_data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                run_id, product_id, external_id, product_url,
                action_type, error_message, 
                json.dumps(scraped_data) if scraped_data else None
            ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

# Global database manager instance
db_manager = DatabaseManager()
