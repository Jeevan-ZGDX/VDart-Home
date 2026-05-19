@echo off
echo ==============================================
echo    CMFH - AI Speech Coach Startup Script
echo ==============================================
echo.

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Python found
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=py
        echo ✓ Python found (using py launcher)
    ) else (
        echo ✗ Python not found! Please install Python 3.10+
        pause
        exit /b 1
    )
)

:: Check if Node.js is available
where node >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Node.js found
) else (
    echo ✗ Node.js not found! Please install Node.js 20+
    pause
    exit /b 1
)

echo.
echo ==============================================
echo    Installing Python Dependencies...
echo ==============================================
%PYTHON_CMD% -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✓ Python dependencies installed

echo.
echo ==============================================
echo    Installing Node.js Dependencies...
echo ==============================================
cd web
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Failed to install Node.js dependencies
    cd ..
    pause
    exit /b 1
)
echo ✓ Node.js dependencies installed
cd ..

echo.
echo ==============================================
echo    Starting Backend Server (FastAPI)...
echo ==============================================
start "CMFH Backend" cmd /k "%PYTHON_CMD% main.py"
timeout /t 3 /nobreak >nul

echo.
echo ==============================================
echo    Starting Frontend Server (Next.js)...
echo ==============================================
cd web
start "CMFH Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ==============================================
echo    ✨ All servers starting up!
echo ==============================================
echo.
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:3000
echo.
echo    Press any key to exit...
pause >nul
