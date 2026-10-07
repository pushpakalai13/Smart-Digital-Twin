@echo off
SETLOCAL EnableDelayedExpansion

echo ==========================================================================
echo          AI Digital Twin for Smart Campus - Setup Script                  
echo ==========================================================================

REM 1. Check Python Version
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3.10+ is required but not found in PATH! Please install Python.
    exit /b 1
)

REM 2. Check Node Version
node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js 18+ is required but not found in PATH! Please install Node.js.
    exit /b 1
)

REM 3. Create Python Virtual Environment
IF NOT EXIST "venv" (
    echo [SETUP] Creating Python Virtual Environment (venv)...
    python -m venv venv
) ELSE (
    echo [SETUP] Existing venv found.
)

call venv\Scripts\activate.bat
echo [SETUP] Upgrading pip and installing backend dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r backend\requirements.txt

REM 4. Install Frontend Dependencies
echo [SETUP] Installing frontend npm packages...
cd frontend
call npm install
cd ..

REM 5. Environment Files Initialization
IF NOT EXIST "backend\.env" (
    echo [SETUP] Creating backend\.env from template...
    copy backend\.env.example backend\.env >nul
)

IF NOT EXIST "frontend\.env" (
    echo [SETUP] Creating frontend\.env...
    echo VITE_API_URL=http://localhost:8000/api > frontend\.env
)

REM 6. MongoDB Atlas Connection Check
echo [SETUP] Validating MongoDB Atlas Connection...
python scripts\test_atlas.py
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [NOTICE] Atlas connection test did not succeed.
    echo If you want to run offline without Atlas right now, set USE_EMBEDDED_DB=true in backend\.env
    echo Otherwise, update MONGODB_URI in backend\.env and re-run setup.bat
)

REM 7. Seed Database & Train Initial ML Models
echo [SETUP] Running Idempotent Seeder and ML Pipeline...
python database\seed_data.py
python ml\pipeline.py

echo.
echo ==========================================================================
echo           SETUP COMPLETED SUCCESSFULLY! Ready to Start!                   
echo ==========================================================================
echo Run 'scripts\start.bat' to start both backend and frontend servers.
echo ==========================================================================
