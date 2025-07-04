# V10 Project Structure

## Backend Files

### app.py
Main FastAPI application server that:
- Handles all HTTP endpoints for the application
- Manages database connections using asyncpg
- Processes garment submissions and feedback
- Provides measurement data and fit recommendations
Key endpoints:
- POST /garments/submit - Submit new garments
- GET /brands/{id}/measurements - Get available measurements
- GET /user/{id}/closet - Get user's saved garments

### fit_zone_calculator.py
Calculates personalized fit zones for users:
- Takes user's garment history and feedback
- Determines optimal measurement ranges
- Provides fit recommendations based on historical preferences
- Handles different measurement types (chest, sleeve, etc.)

## Frontend Files (Swift)

### Views/MatchScreen.swift
Primary screen for garment submission:
- Accepts product URL and size inputs
- Submits garment details to backend
- Collects fit feedback for measurements
- Shows feedback options using segmented controls
- Handles API communication with backend

### Views/ClosetView.swift
Displays user's saved garments and their fit information:
- Fetches garment data from backend
- Shows garment details and measurements
- Allows browsing past submissions

### Views/ClosetListView.swift
List component used within ClosetView:
- Displays garment items in a scrollable list
- Supports swipe-to-delete functionality
- Handles navigation to garment details

### Views/LiveMeasurementsView.swift
Shows real-time measurement updates and fit zones:
- Connects to hardware sensors for live measurements
- Displays current measurements and fit zones
- Updates in real-time as measurements change

## Testing
- `V10.xcodeproj/tailor_testing.sql` - SQL queries used for testing the application

## Key Features
1. Garment Submission
   - Users can submit garments via product URLs
   - System identifies brand and collects fit feedback
   - Stores measurements and user preferences

2. Fit Analysis
   - Calculates personalized fit zones
   - Provides fit recommendations
   - Tracks measurement history

3. User Closet
   - Maintains history of user's garments
   - Shows fit feedback and measurements
   - Allows browsing past submissions

## Database Structure
The `tailor3` database contains:
- User profiles and measurements
- Brand information and size guides
- Garment submissions and feedback
- Calculated fit zones

## Database Files
- Database snapshots in `supabase/snapshots/`
- Schema evolution in `supabase/`
- Current schema in `supabase/schema.sql`