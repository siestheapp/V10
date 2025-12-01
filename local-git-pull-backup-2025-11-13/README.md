# V10 Monorepo

This repo contains the V10 app code and data tooling:
- Expo mobile app in `expo/`
- Python scripts and data tools in `scripts/`
- Supabase schema and docs in `supabase/`
- Project notes in `daily-notes/`

## Quick start

Prereqs:
- Python 3.11+
- Node 20+

Install Python deps:
```bash
python -m venv venv && source venv/bin/activate
pip install -U pip -r requirements.txt
```

Install Expo deps:
```bash
cd expo
npm ci
```

Run Expo:
```bash
npm run start
```

## Development hygiene

- Lint checks run in CI for Python (ruff/black) and Expo (eslint).
- Pre-commit is configured. Install locally:
```bash
pip install pre-commit && pre-commit install
```

## Documentation

- Contractor setup: `CONTRACTOR_SETUP_GUIDE.md`, `CONTRACTOR_FULL_STACK_SETUP.md`
- Database: `supabase/README.md`, `daily-notes/*/TAILOR3_*`, `DATABASE_SCHEMA_GUIDE.md`
- Scrapers and ingestion: see `scripts/` and accompanying docs in root.


