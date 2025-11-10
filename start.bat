@echo off
echo Starting Payment Refund Investigations POC
echo ================================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Please run setup first:
    echo    python setup.py
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Check if node_modules exists in FrontendReact
if not exist "FrontendReact\node_modules" (
    echo Frontend dependencies not found. Installing...
    cd FrontendReact
    call npm install
    cd ..
)

echo.
echo Starting Backend Server...
echo ================================================
start "Backend Server" cmd /k "call .venv\Scripts\activate && echo Backend Server running at http://localhost:5000 && echo Press Ctrl+C to stop backend && python -m app.web"

REM Wait a moment for backend to start
timeout /t 2 /nobreak >nul

echo.
echo Starting Frontend Server...
echo ================================================
cd FrontendReact
start "Frontend Server" cmd /k "echo Frontend Server running at http://localhost:3000 && echo Press Ctrl+C to stop frontend && npm run dev"
cd ..

echo.
echo ================================================
echo Both servers are starting in separate windows:
echo   - Backend:  http://localhost:5000
echo   - Frontend: http://localhost:3000
echo.
echo Close the server windows to stop the servers.
echo Press any key to exit this window (servers will continue running)...
echo ================================================
pause >nul
