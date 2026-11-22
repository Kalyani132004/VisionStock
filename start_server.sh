#!/bin/bash
# Start the VisionStock server on Linux / Mac
# Run "pip install -r backend/requirements.txt" once before the first start.
cd "$(dirname "$0")"
echo "Open http://127.0.0.1:8000 in your browser"
python3 -m uvicorn backend.main:app --reload
