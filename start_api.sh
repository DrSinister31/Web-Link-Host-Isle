#!/bin/sh
cd /app
python -m uvicorn bridge.synix_api:app --host 0.0.0.0 --port 8000
