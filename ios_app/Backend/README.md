# V10 Backend API

FastAPI backend server for the V10 iOS app.

## Setup

### 1. Activate Virtual Environment
```bash
cd /Users/seandavey/projects/V10
source venv/bin/activate
```

### 2. Install Dependencies
```bash
cd ios_app/Backend
pip install -r requirements.txt
```

### 3. Start the Server

**Option A: Using the startup script**
```bash
cd ios_app/Backend
./start_server.sh
```

**Option B: Manual start**
```bash
cd ios_app/Backend
source ../../venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8006 --reload
```

## API Endpoints

- `GET /user/{user_id}/closet` - Get user's closet garments
- `GET /user/{user_id}/measurements` - Get user's fit measurements
- `GET /shop/recommendations` - Get shopping recommendations

## Configuration

The server runs on `http://127.0.0.1:8006` by default.

Database connection is configured in `app.py` using environment variables.

## Troubleshooting

If you get "No module named uvicorn":
1. Make sure the virtual environment is activated
2. Run `pip install -r requirements.txt`
3. Try the startup script: `./start_server.sh` 