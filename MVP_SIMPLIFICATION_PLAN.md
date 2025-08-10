

# MVP Simplified Fit System Plan

**Branch:** mvp-simplified-fit-system  
**Goal:** Get iOS build working with minimal complexity  
**Strategy:** Simple endpoints that work, prepare for AI overhaul  

## 🎯 CORE iOS ENDPOINTS NEEDED:

Based on iOS code analysis:
1. /user/{id}/closet - Show user's garments  
2. /user/{id}/measurements - User measurement profile
3. /garment/{id}/measurements - Individual garment measurements  
4. /garment/{id}/feedback - Submit fit feedback
5. /shop/recommendations - Size recommendations for shopping
6. /scan/recommend - Size recommendations from scanning

## 🔧 SIMPLIFICATION STRATEGY:

### Phase 1: Create Simple Unified Service
- Single file: simple_fit_service.py
- Handle both size_guides and garment_guides
- Basic logic: if measurements exist, return them
- Simple feedback: store and learn from it

### Phase 2: Replace Complex Analyzers  
- Remove 5 different analyzers
- Replace with simple lookup + basic logic
- Focus on 'it works' not 'it's perfect'

### Phase 3: Test iOS Build
- Verify all endpoints return data
- Test in Xcode simulator
- Ensure no crashes

Ready to start?
