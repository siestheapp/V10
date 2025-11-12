# iOS App Updates Needed for Dynamic Fit Selection

## Current State
The backend is now successfully providing all necessary data for dynamic fit selection. When a J.Crew product URL is processed, the API returns:

```json
{
  "product_name": "Slim Untucked Broken-in organic cotton oxford shirt",
  "current_fit": "Slim Untucked",
  "base_product_name": "Broken-in organic cotton oxford shirt",
  "fit_options": ["Classic", "Slim", "Slim Untucked", "Tall", "Relaxed"],
  "fit_variations": {
    "Classic": {
      "product_name": "Broken-in organic cotton oxford shirt",
      "colors_available": [...],
      "product_url": "https://www.jcrew.com/p/BE996?fit=Classic"
    },
    "Slim": {
      "product_name": "Slim Broken-in organic cotton oxford shirt",
      "colors_available": [...],
      "product_url": "https://www.jcrew.com/p/BE996?fit=Slim"
    },
    // ... other fits
  }
}
```

## Issues to Fix in iOS App

### 1. ❌ Product Name Not Updating
**Problem:** When user taps a different fit option, the product name stays the same.

**Solution:** 
```swift
// In TryOnConfirmationView or wherever fit selection is handled
func selectFit(_ fit: String) {
    if let fitData = session.fit_variations?[fit] {
        // Update the displayed product name
        self.productName = fitData["product_name"] as? String ?? session.product_name
        self.currentFit = fit
    }
}
```

### 2. ❌ Colors Not Updating
**Problem:** Available colors should change based on selected fit (some fits have different color options).

**Solution:**
```swift
func updateColorsForFit(_ fit: String) {
    if let fitData = session.fit_variations?[fit],
       let colors = fitData["colors_available"] as? [String] {
        self.availableColors = colors
        // Refresh color swatches UI
    }
}
```

### 3. ❌ Color Swatches Missing
**Problem:** Color circles are all gray placeholders instead of showing actual colors.

**Possible Causes:**
1. Color data format mismatch (backend sends color names, iOS expects hex codes?)
2. Missing color mapping logic
3. Color swatch view not properly rendering

**Solution Ideas:**
- Map J.Crew color names to actual colors/images
- Use color codes from the API if available
- Fetch color swatch images from J.Crew CDN

## Implementation Steps

1. **Add State Management**
   ```swift
   @State private var selectedFit: String = ""
   @State private var displayedProductName: String = ""
   @State private var currentColors: [ColorOption] = []
   ```

2. **Handle Fit Selection**
   ```swift
   Button(action: {
       selectFit("Slim")
   }) {
       Text("Slim")
   }
   ```

3. **Update UI Dynamically**
   - When fit changes → update product name from `fit_variations[selectedFit]["product_name"]`
   - When fit changes → update colors from `fit_variations[selectedFit]["colors_available"]`
   - Store selected fit to send with feedback submission

## Testing
Test with BE996 URL variations:
- `https://www.jcrew.com/p/BE996?fit=Classic` → "Broken-in organic cotton oxford shirt"
- `https://www.jcrew.com/p/BE996?fit=Slim` → "Slim Broken-in organic cotton oxford shirt"
- `https://www.jcrew.com/p/BE996?fit=Slim%20Untucked` → "Slim Untucked Broken-in organic cotton oxford shirt"

## Backend API Response Structure
The backend sends `fit_variations` in the `/tryon/start` response. Check for this field and use it to enable dynamic updates in the UI.
