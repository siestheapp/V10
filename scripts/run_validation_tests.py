#!/usr/bin/env python3
"""Run the J.Crew data validation tests"""

import psycopg2
import json
from datetime import datetime
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

def run_validation_tests():
    """Run all validation tests and display results"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("RUNNING J.CREW DATA VALIDATION TESTS")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run comprehensive test suite
    print("\n📋 TEST SUITE RESULTS:")
    print("-" * 80)
    
    cur.execute("SELECT * FROM run_jcrew_data_tests()")
    tests = cur.fetchall()
    
    passed_count = 0
    failed_count = 0
    
    for test_name, expected, actual, passed, details in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        passed_count += 1 if passed else 0
        failed_count += 0 if passed else 1
        
        print(f"\n{status}: {test_name}")
        print(f"   Expected: {expected}")
        print(f"   Actual: {actual}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    # Check data quality
    print("\n\n🔍 DATA QUALITY CHECKS:")
    print("-" * 80)
    
    cur.execute("SELECT * FROM check_jcrew_data_quality()")
    quality_issues = cur.fetchall()
    
    if not quality_issues:
        print("✅ No data quality issues found!")
    else:
        for alert_type, alert_level, message, count, details in quality_issues:
            icon = "❌" if alert_level == "ERROR" else "⚠️" if alert_level == "WARNING" else "ℹ️"
            print(f"\n{icon} {alert_level}: {message}")
            print(f"   Type: {alert_type}")
            print(f"   Count: {count}")
            if details and len(str(details)) < 500:
                print(f"   Details: {json.dumps(details, indent=6)[:500]}")
    
    # Validate critical products
    print("\n\n🔒 CRITICAL PRODUCTS VALIDATION:")
    print("-" * 80)
    
    cur.execute("SELECT * FROM validate_critical_products()")
    critical = cur.fetchall()
    
    all_critical_passed = True
    for product_code, test_name, expected, actual, passed in critical:
        status = "✅" if passed else "❌"
        all_critical_passed = all_critical_passed and passed
        print(f"{status} {product_code}: {'CORRECT' if passed else 'INCORRECT'}")
        if not passed:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
    
    # Summary statistics
    print("\n\n📊 DATABASE STATISTICS:")
    print("-" * 80)
    
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE fit_options IS NOT NULL AND array_length(fit_options, 1) > 0) as with_fits,
            COUNT(*) FILTER (WHERE fit_options IS NULL OR array_length(fit_options, 1) = 0 OR array_length(fit_options, 1) IS NULL) as without_fits,
            COUNT(DISTINCT product_code) as unique_codes
        FROM jcrew_product_cache
    """)
    
    total, with_fits, without_fits, unique_codes = cur.fetchone()
    
    print(f"Total products: {total}")
    print(f"Unique product codes: {unique_codes}")
    print(f"Products with fit options: {with_fits} ({round(with_fits*100/total, 1)}%)")
    print(f"Products without fit options: {without_fits} ({round(without_fits*100/total, 1)}%)")
    
    # Get some examples of products without fits
    cur.execute("""
        SELECT product_code, product_name
        FROM jcrew_product_cache
        WHERE fit_options IS NULL OR array_length(fit_options, 1) = 0 OR array_length(fit_options, 1) IS NULL
        LIMIT 5
    """)
    
    no_fits = cur.fetchall()
    if no_fits:
        print("\nExamples of products without fit options:")
        for code, name in no_fits:
            print(f"  - {code}: {name[:50] if name else 'No name'}...")
    
    # Overall test summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = passed_count + failed_count
    print(f"Tests Run: {total_tests}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"🔒 Critical Products: {'✅ ALL CORRECT' if all_critical_passed else '❌ SOME INCORRECT'}")
    
    if failed_count == 0 and all_critical_passed:
        print("\n🎉 ALL TESTS PASSED! Data is in good state.")
    else:
        print("\n⚠️ Some tests failed. Review issues above.")
    
    cur.close()
    conn.close()
    
    return passed_count, failed_count, all_critical_passed

if __name__ == "__main__":
    run_validation_tests()
