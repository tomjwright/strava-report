@echo off
echo Starting Strava Dashboard System...
echo.

echo [1/3] Starting Simple Backend...
start "Strava Backend" cmd /k "cd /d C:\workspace\strava-report && python simple_backend.py"

timeout /t 3 /nobreak

echo [2/3] Starting Clean Frontend...
start "Strava Frontend" cmd /k "cd /d C:\workspace\strava-report\frontend && python -m streamlit run ../clean_dashboard.py"

timeout /t 3 /nobreak

echo [3/3] Starting Auto-Loader...
start "Strava Auto-Loader" cmd /k "cd /d C:\workspace\strava-report && python auto_loader.py"

echo.
echo ====================================
echo All services started successfully!
echo Dashboard: http://localhost:8501
echo Backend API: http://localhost:8006
echo Auto-Loader: Running (loads data daily at 6:00 AM)
echo ====================================
echo.
pause