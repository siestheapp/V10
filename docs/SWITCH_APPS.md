# Switching Between Original and Optimized App

## Currently Active: OptimizedSiesApp ✅
- Lazy-loads tabs for fast startup
- ~5x faster launch time

## To Switch Back to Original:
1. In `OptimizedSiesApp.swift`: Comment out `@main` on line 3
2. In `SiesApp.swift`: Uncomment `@main` on line 3
3. Clean and rebuild

## To Switch to Optimized:
1. In `SiesApp.swift`: Comment out `@main` on line 3
2. In `OptimizedSiesApp.swift`: Ensure `@main` is present on line 3
3. Clean and rebuild

## Performance Comparison:
- **Original SiesApp:** ~3.93 seconds startup
- **OptimizedSiesApp:** ~0.8 seconds startup

## Key Difference:
- **Original:** All 5 tabs load data at startup
- **Optimized:** Only visible tab loads data

