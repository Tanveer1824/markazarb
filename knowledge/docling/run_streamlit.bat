@echo off
echo Starting Streamlit from the correct directory...
echo.

REM Change to the script directory
cd /d "%~dp0"

echo Working directory: %CD%
echo Database path: %CD%\data\lancedb

REM Check if database exists
if not exist "data\lancedb" (
    echo ERROR: Database path not found: data\lancedb
    pause
    exit /b 1
)

REM Set environment variable for database path
set DB_PATH=%CD%\data\lancedb
set DEBUG=true

echo.
echo Starting Streamlit...
echo Press Ctrl+C to stop
echo.

REM Run Streamlit
python -m streamlit run 5-chat.py --server.port 8501 --server.address localhost

pause
