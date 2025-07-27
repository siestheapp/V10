# FIRST: Always activate virtual environment
source venv/bin/activate

Use this to start app
cd src/ios_app/Backend
./start_server.sh

Or

cd src/ios_app/Backend && source ../../../venv/bin/activate && python app.py


start Webpages
cd /Users/seandavey/projects/V10
./tools/start_web_services.sh

Connect to tailor3
PGPASSWORD='efvTower12' psql -h aws-0-us-east-2.pooler.supabase.com -p 6543 -U postgres.lbilxlkchzpducggkrxx -d postgres

Activate virtual environment
source venv/bin/activate

Take Database snapshot
python scripts/database/db_snapshot.py

Check if server is running
sleep 5 && curl -s http://127.0.0.1:8006/user/1/closet | jq length