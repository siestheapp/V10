# Test Scripts

This directory contains various test and debugging scripts for the V10 project.

## Test Scripts

- **test_brand_dimensions.py** - Test what dimensions exist for each brand
- **test_garment_details.py** - Test garment details and size guide linking
- **test_measurement_linking.py** - Test measurement linking functionality
- **test_new_feedback_system.py** - Test the new feedback system
- **test_parameterized_query.py** - Test parameterized database queries

## Debug Scripts

- **debug_size_guides.py** - Debug size guides table and queries
- **manual_fix_garment.py** - Manual fix for specific garment issues

## Example Scripts

- **example_change_logging.py** - Example usage of the database change logger

## Usage

Run any test script from the project root:

```bash
python tests/test_brand_dimensions.py
```

## Notes

- These scripts are for testing and debugging purposes
- They may modify database state - use with caution
- Some scripts are one-time fixes and may not be needed for regular operation 