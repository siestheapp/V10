#!/bin/bash
source venv/bin/activate
cd V10/V10/Backend
uvicorn app:app --host 0.0.0.0 --port 8006 --reload
