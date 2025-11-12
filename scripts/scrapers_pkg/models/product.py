"""Product data models for scraped products."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

@dataclass
class ScrapedProduct:
    """Model for scraped product data."""
    
    # Required fields
    name: str
    product_url: str
    external_id: str
    brand_name: str
    
    # Optional product details
    description: Optional[str] = None
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    discount_percentage: Optional[int] = None
    currency: str = "USD"
    
    # Product attributes
    material: Optional[str] = None
    fit_type: Optional[str] = None
    care_instructions: Optional[str] = None
    
    # Availability
    sizes_available: List[str] = field(default_factory=list)
    colors_available: List[str] = field(default_factory=list)
    in_stock: bool = True
    
    # Media
    primary_image_url: Optional[str] = None
    additional_images: List[str] = field(default_factory=list)
    
    # Categories
    category: Optional[str] = None
    subcategory: Optional[str] = None
    
    # Metadata
    scraping_metadata: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Calculate discount percentage if not provided
        if (self.price and self.original_price and 
            self.discount_percentage is None and 
            self.original_price > self.price):
            self.discount_percentage = int(
                ((self.original_price - self.price) / self.original_price) * 100
            )
        
        # Clean and validate data
        if self.name:
            self.name = self.name.strip()
        
        if self.description:
            self.description = self.description.strip()
        
        # Ensure external_id is string
        self.external_id = str(self.external_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            'name': self.name,
            'product_url': self.product_url,
            'external_id': self.external_id,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'original_price': float(self.original_price) if self.original_price else None,
            'discount_percentage': self.discount_percentage,
            'material': self.material,
            'fit_type': self.fit_type,
            'care_instructions': self.care_instructions,
            'sizes_available': self.sizes_available,
            'colors_available': self.colors_available,
            'in_stock': self.in_stock,
            'primary_image_url': self.primary_image_url,
            'additional_images': self.additional_images,
            'category': self.category,
            'subcategory': self.subcategory,
            'scraping_metadata': self.scraping_metadata,
            'scraped_at': self.scraped_at
        }

@dataclass
class ScrapingRun:
    """Model for tracking scraping runs."""
    
    brand_name: str
    category: str
    target_url: str
    scraper_version: str = "1.0.0"
    
    # Results
    products_found: int = 0
    products_added: int = 0
    products_updated: int = 0
    errors_count: int = 0
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    run_duration_seconds: Optional[int] = None
    
    # Status
    status: str = "running"  # running, completed, failed
    error_details: Dict[str, Any] = field(default_factory=dict)
    
    def mark_completed(self):
        """Mark the run as completed and calculate duration."""
        self.completed_at = datetime.now()
        self.status = "completed"
        if self.started_at:
            self.run_duration_seconds = int(
                (self.completed_at - self.started_at).total_seconds()
            )
    
    def mark_failed(self, error_details: Dict[str, Any]):
        """Mark the run as failed with error details."""
        self.completed_at = datetime.now()
        self.status = "failed"
        self.error_details = error_details
        if self.started_at:
            self.run_duration_seconds = int(
                (self.completed_at - self.started_at).total_seconds()
            )
