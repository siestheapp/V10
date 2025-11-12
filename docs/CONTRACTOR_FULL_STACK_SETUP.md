# Option 2: Full Stack Setup (If Backend Debugging Needed)

## ⚠️ SECURITY WARNING
This option requires more trust and security measures. Only use if iOS-only debugging is insufficient.

## Architecture Overview
```
iOS App (Simulator) 
    ↓ HTTP requests to localhost:8006
Python Backend (FastAPI)
    ↓ PostgreSQL connection
Mock Database (Local PostgreSQL)
```

## Setup Steps

### 1. Backend Setup (Simplified)

Create a mock backend configuration:

```python
# contractor_backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import random

app = FastAPI()

# Enable CORS for iOS simulator
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock endpoints matching your real API
@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    return {
        "user_id": user_id,
        "email": "test@example.com",
        "measurements": [
            {"dimension": "chest", "value": 40.0},
            {"dimension": "waist", "value": 32.0}
        ]
    }

@app.get("/api/garments")
async def get_garments():
    # Return large dataset for performance testing
    garments = []
    for i in range(500):
        garments.append({
            "id": i,
            "brand": random.choice(["J.Crew", "Uniqlo"]),
            "name": f"Garment {i}",
            "fit_score": random.uniform(0.5, 1.0)
        })
    return {"garments": garments}

@app.get("/api/shop/recommendations")
async def get_recommendations():
    items = []
    for i in range(200):
        items.append({
            "id": i,
            "name": f"Product {i}",
            "price": random.uniform(29.99, 199.99),
            "image_url": f"https://picsum.photos/300/400?random={i}"
        })
    return {"recommendations": items}

# Run with: uvicorn contractor_backend:app --reload --port 8006
```

### 2. Database Setup (Optional)

If database interaction is needed for debugging:

```bash
# Use SQLite for simplicity (no credentials needed)
# contractor_db_setup.py

import sqlite3

conn = sqlite3.connect('mock_v10.db')
c = conn.cursor()

# Create minimal schema
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        email TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS garments (
        garment_id INTEGER PRIMARY KEY,
        brand TEXT,
        product_name TEXT,
        category TEXT
    )
''')

# Insert mock data
c.execute("INSERT INTO users VALUES (1, 'test@example.com')")

for i in range(100):
    c.execute(
        "INSERT INTO garments VALUES (?, ?, ?, ?)",
        (i, 'TestBrand', f'Product{i}', 'shirt')
    )

conn.commit()
conn.close()
```

### 3. Running the Full Stack

**Terminal 1 - Backend:**
```bash
cd V10
python -m venv contractor_venv
source contractor_venv/bin/activate
pip install fastapi uvicorn
python contractor_backend.py
```

**Terminal 2 - iOS App:**
```bash
cd src/ios_app
open V10.xcodeproj
# Build and run in Xcode
```

## Environment Variables (Contractor Version)

Create `.env.contractor`:
```
# Mock environment - no real credentials
DATABASE_URL=sqlite:///mock_v10.db
API_KEY=mock-api-key-for-testing
OPENAI_API_KEY=not-needed-for-performance-testing
```

## What NOT to Share

Never share these files:
- `db_config.py` (real database credentials)
- `.env` (production environment variables)
- `src/ios_app/Backend/body_measurement_estimator.py` (proprietary algorithms)
- `src/ios_app/Backend/multi_dimensional_fit_analyzer.py` (core IP)
- Any `tailor3_dump_*.sql` files (real data)

## Simplified Testing Approach

Instead of full backend, consider a JSON server:

```bash
# Install json-server globally
npm install -g json-server

# Create mock data file
echo '{
  "users": [{"id": 1, "email": "test@example.com"}],
  "garments": [{"id": 1, "brand": "Test", "name": "Shirt"}],
  "recommendations": [{"id": 1, "name": "Product", "price": 99.99}]
}' > mock-db.json

# Run mock server on port 8006
json-server --watch mock-db.json --port 8006
```

This provides REST endpoints without any backend code exposure.

