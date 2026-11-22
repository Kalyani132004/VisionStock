@echo off
REM Start the VisionStock server on Windows (double click this file)
REM Run "pip install -r backend\requirements.txt" once before the first start.
cd /d %~dp0
echo Open http://127.0.0.1:8000 in your browser
python -m uvicorn backend.main:app --reload
pause
