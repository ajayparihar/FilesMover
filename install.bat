@echo off
echo ======================================================
echo          File Mover - Installation Setup  
echo ======================================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Run the setup script
echo Running setup script...
python setup.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Setup failed
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
pause 