# Capturing Performance Baseline with Instruments

## Step 1: Open the Project in Xcode
```bash
cd /Users/seandavey/projects/V10/src/ios_app
open V10.xcodeproj
```

## Step 2: Profile with Instruments
1. Select **iPhone 15 Pro** simulator (or any recent iPhone)
2. **Product → Profile** (or press **Cmd+I**)
3. The app will build in Release mode and Instruments will open

## Step 3: Choose Time Profiler
When Instruments opens:
1. Select **Time Profiler** template
2. Click **Choose**

## Step 4: Record the Baseline

### Test 1: Tab Switching
1. Click **Record** button (red circle)
2. Once app loads, quickly tap through all tabs:
   - Shop → Closet → Scan → Fit → Shop (repeat 3-5 times)
3. Stop recording after ~20 seconds

### Test 2: Scrolling Performance
1. Start new recording
2. Go to **Shop** tab
3. Scroll up and down rapidly for 10 seconds
4. Switch to **Closet** tab  
5. Scroll rapidly for 10 seconds
6. Stop recording

### Test 3: Button Response
1. Start new recording
2. Go to **Shop** tab
3. Tap on multiple product cards quickly
4. Go back and tap more products
5. Stop recording

## Step 5: Analyze Results

### In Time Profiler:
1. **Call Tree** view (bottom left)
2. Check **Invert Call Tree** 
3. Check **Hide System Libraries**
4. Sort by **Weight** column

### Look for:
- Functions taking >100ms
- Main thread blocks >16ms (causes frame drops)
- Repeated expensive operations

## Step 6: Measure Tab Switch Time
1. In the timeline, zoom into a tab switch
2. Select the time range from tap to view appearing
3. Note the duration (shown at bottom)

## Step 7: Check FPS
1. Switch to **Core Animation** instrument
2. Add it via **+** button if not present
3. Look at **FPS** graph during scrolling
4. Current should be ~20 FPS (we want 55+)

## Step 8: Save the Trace
1. **File → Save**
2. Name it: `V10_Baseline_2025-09-17.trace`
3. This is your "before" measurement

## What to Document:

### Tab Switching Times (measure 3 switches, take average):
- Shop → Closet: _____ ms
- Closet → Scan: _____ ms  
- Scan → Fit: _____ ms
- Fit → Shop: _____ ms

### Scrolling FPS:
- Shop grid: _____ FPS
- Closet list: _____ FPS

### Top Time Consumers:
1. Function: _____ Time: _____
2. Function: _____ Time: _____
3. Function: _____ Time: _____

### Memory at Points:
- App launch: _____ MB
- After 1 min: _____ MB
- After all tests: _____ MB

## Expected Current Performance (Bad):
- Tab switches: ~450ms
- Scrolling: ~20 FPS
- Lots of main thread blocking

## Target After Optimization:
- Tab switches: <200ms
- Scrolling: 55+ FPS
- Minimal main thread blocks

---

Save your .trace file - the contractor will need to beat these numbers!
