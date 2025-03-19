@echo off
:: FilesMover Simple Launcher for Windows
:: This batch file provides a simple way to run the FilesMover Simple application

setlocal

echo FilesMover Simple - File Mover Utility
echo --------------------------------------

:: Find Python in the system
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo Error: Python not found in PATH.
        echo Please install Python 3.7 or higher and try again.
        pause
        exit /b 1
    )
)

:: Get the directory of this batch file
set SCRIPT_DIR=%~dp0
set PARENT_DIR=%SCRIPT_DIR:~0,-1%\..\

:: Run the application with arguments
echo Starting FilesMover Simple...
%PYTHON_CMD% "%PARENT_DIR%\run_simple.py" %*

if %ERRORLEVEL% neq 0 (
    echo Error running FilesMover Simple. Exit code: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0 