@echo off
SETLOCAL EnableDelayedExpansion

:: Always navigate to project root directory
cd /d "%~dp0"
if exist "..\backend" cd /d "%~dp0.."

echo ==========================================================================
echo       Starting AI Digital Twin for Smart Campus (Backend & Frontend)     
echo ==========================================================================

if exist "venv\Scripts\activate.bat" (
    echo Activating Python Virtual Environment...
    call venv\Scripts\activate.bat
)

echo [START] Launching FastAPI Backend Server on http://localhost:8000 ...
start "SmartCampus Backend API" cmd /k "venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend"

echo [START] Launching React Frontend Server on http://localhost:5173 ...
start "SmartCampus Frontend UI" cmd /k "cd /d "%cd%\frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo Waiting 4 seconds for servers to initialize...
timeout /t 4 /nobreak >nul

echo Opening http://localhost:5173 in default browser...
start http://localhost:5173

echo ==========================================================================
echo  Servers running successfully!
echo  -> Frontend UI : http://localhost:5173
echo  -> Backend API: http://localhost:8000/api/health
echo  -> API Docs   : http://localhost:8000/docs
echo ==========================================================================
