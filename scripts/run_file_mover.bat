@echo off
:: ===================================================
:: FilesMover - Main Launcher Script
:: ===================================================
:: This batch file launches the FilesMover application.
:: 
:: It can run in either GUI mode (default) or CLI mode.
:: To run in CLI mode, use the --cli argument.
::
:: Arguments:
::   --cli     : Run in command-line interface mode
::   Any other arguments are passed to the CLI version
::
:: Examples:
::   run_file_mover.bat               - Run GUI version
::   run_file_mover.bat --cli         - Run CLI version
::   run_file_mover.bat --cli -o      - Run CLI with one-time processing
:: ===================================================
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
    REM Run GUI mode without showing console window
    start "" pythonw "%~dp0..\src\file_mover_gui.py"
    exit
) else (
    echo Starting FilesMover in CLI mode...
    echo.
    python "%~dp0..\src\file_mover_cli.py" %CLI_ARGS%

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
) 