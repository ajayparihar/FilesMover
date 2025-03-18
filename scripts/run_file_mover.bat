@echo off
echo ======================================================
echo              FilesMover - Starting...  
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

REM Set the parent directory in PYTHONPATH for proper imports
set PYTHONPATH=%PYTHONPATH%;%~dp0..

REM Check for command line arguments to determine which version to run
set "GUI_MODE=true"
set "CLI_ARGS="

:parse_args
if "%~1"=="" goto :run_program
if /i "%~1"=="--cli" (
    set "GUI_MODE=false"
    shift
    goto :parse_args
)
if defined CLI_ARGS (
    set "CLI_ARGS=%CLI_ARGS% %~1"
) else (
    set "CLI_ARGS=%~1"
)
shift
goto :parse_args

:run_program
echo.
if "%GUI_MODE%"=="true" (
    echo Starting FilesMover in GUI mode...
    echo.
    python "%~dp0..\src\file_mover_gui.py"
) else (
    echo Starting FilesMover in CLI mode...
    echo.
    python "%~dp0..\src\file_mover_cli.py" %CLI_ARGS%
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo ======================================================
    echo ERROR: FilesMover encountered a problem (code: %ERRORLEVEL%)
    echo ======================================================
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ======================================================
echo FilesMover completed successfully
echo ======================================================
echo. 