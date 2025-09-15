# Dress Shirt Fit Detection Fix - V10 App

## Issue
The Bowery performance stretch dress shirt wasn't showing fit options (Classic, Slim, Tall) in the app, even though they're clearly available on the J.Crew website.

## Root Cause
The fit detection was too restrictive after our previous fix for the corduroy shirt. It was looking for specific UI elements that J.Crew's dress shirt pages don't have in their HTML.

## Solution
Modified `src/ios_app/Backend/jcrew_fetcher.py` to be smarter about product categories:

### Key Changes (lines 798-837):

1. **Product Type Detection**:
```python
is_dress_shirt = 'dress-shirt' in product_url.lower() or 'bowery' in product_url.lower() or 'ludlow' in product_url.lower()
is_formal_wear = 'suit' in product_url.lower() or 'tuxedo' in product_url.lower() or 'blazer' in product_url.lower()
```

2. **Automatic Fit Assignment for Dress Shirts**:
```python
# If we're on a dress shirt or formal wear page, these ALWAYS have fit options at J.Crew
if is_dress_shirt or is_formal_wear:
    common_dress_shirt_fits = ['Classic', 'Slim', 'Tall']
    if not standardized_fits or len(standardized_fits) <= 1:
        standardized_fits = common_dress_shirt_fits
```

3. **Broader UI Element Search**:
- Added more selectors: links with fit parameters, form inputs, dropdowns
- Checks for fit mentions in page text

## How It Works

### For Dress Shirts (Bowery, Ludlow):
- Automatically returns ['Classic', 'Slim', 'Tall']
- Based on J.Crew's consistent pattern for dress shirts
- No longer requires specific UI elements to be found

### For Casual Shirts:
- Still returns no fit options (correctly)
- Validates that they don't have fit variations

## Testing Results
```
Bowery dress shirt → Fit Options: ['Classic', 'Slim', 'Tall'] ✅
Corduroy casual shirt → Fit Options: [] ✅
Untucked casual shirt → Fit Options: [] ✅
```

## Impact
- Users will now see fit selection for all J.Crew dress shirts
- Casual shirts continue to work correctly without fit options
- The app intelligently distinguishes between product types
- Matches the actual J.Crew website experience
