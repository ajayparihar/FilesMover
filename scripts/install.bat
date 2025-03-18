@echo off
:: ===================================================
:: FilesMover - Installation Setup Script
:: ===================================================
:: This batch file handles the installation of the
:: FilesMover application by:
::  1. Checking for Python installation
::  2. Installing required packages from requirements.txt
::  3. Optionally creating a desktop shortcut
::
:: After running this script, the application will be
:: ready to use via the run_file_mover.bat script.
:: ===================================================
echo ======================================================
echo          FilesMover - Installation Setup  
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

REM Run the pip install directly for requirements.txt
echo Installing required packages...
python -m pip install -r ..\requirements.txt

if %ERRORLEVEL% neq 0 (
    echo.
    echo WARNING: Some packages failed to install
    echo You can try installing them manually with:
    echo pip install -r ..\requirements.txt
    echo.
)

REM Ask about creating a desktop shortcut
echo.
set /p create_shortcut=Would you like to create a desktop shortcut? (y/n): 

if /i "%create_shortcut%"=="y" (
    echo Running setup for desktop shortcut...
    python ..\setup.py
) else (
    echo Skipping desktop shortcut creation.
)

echo.
echo Installation complete!
echo Run 'run_file_mover.bat' to start the application
echo.
pause 