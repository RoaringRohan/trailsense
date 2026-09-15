@echo off
echo Starting TrailSense System...

echo Starting Backend Service...
start "TrailSense Backend" cmd /k "cd backend && pip install -r requirements.txt && python main.py"

echo Starting Frontend Interface...
start "TrailSense Frontend" cmd /k "cd frontend && npm run dev"

echo System Initialized.
