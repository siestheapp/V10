#!/usr/bin/env python3
"""
Example script showing how to use the database change logger
"""

from db_change_logger import (
    log_user_creation, 
    log_garment_addition, 
    log_feedback_submission, 
    log_brand_addition,
    log_size_guide_addition,
    print_recent_changes,
    print_change_stats
)

def example_usage():
    """Example of how to log various database changes"""
    
    print("🔍 Example Database Change Logging")
    print("=" * 50)
    
    # Example 1: Log user creation
    print("\n1. Logging user creation...")
    log_user_creation("john@example.com", "Male", 123)
    
    # Example 2: Log brand addition
    print("\n2. Logging brand addition...")
    log_brand_addition("Nike", 456)
    
    # Example 3: Log garment addition
    print("\n3. Logging garment addition...")
    log_garment_addition(123, "Nike", "Dri-FIT T-Shirt", "M", 789)
    
    # Example 4: Log feedback submission
    print("\n4. Logging feedback submission...")
    log_feedback_submission(123, 789, "chest", "Good Fit")
    log_feedback_submission(123, 789, "sleeve", "Too Tight")
    
    # Example 5: Log size guide addition
    print("\n5. Logging size guide addition...")
    log_size_guide_addition("Nike", "Male", "Tops", 101)
    
    print("\n✅ All changes logged!")
    
    # Show recent changes
    print_recent_changes(5)
    
    # Show statistics
    print_change_stats()

if __name__ == "__main__":
    example_usage() 