@echo off
echo ======================================================
echo              File Mover - Starting...  
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

REM Check for command line arguments to determine which version to run
if "%1"=="--cli" goto run_cli
if "%1"=="--help" goto show_help

REM By default, run the GUI version
:run_gui
echo Starting File Mover GUI...
python ..\src\file_mover_gui.py
goto end

:run_cli
echo Starting File Mover CLI...
REM Pass any remaining arguments to the CLI script
python ..\src\file_mover_cli.py %2 %3 %4 %5 %6 %7 %8 %9
goto end

:show_help
echo File Mover - Command Line Options
echo.
echo Usage:
echo   run_file_mover.bat             - Run the graphical interface
echo   run_file_mover.bat --cli       - Run the command line interface
echo   run_file_mover.bat --cli [args] - Run CLI with additional arguments
echo   run_file_mover.bat --help      - Show this help
echo.
echo Common CLI arguments:
echo   -s, --source [path]     - Set source directory
echo   -d, --destination [path] - Set destination directory
echo   -o, --one-time          - Process existing files and exit
echo   -l, --log-file [path]   - Specify custom log file
echo   --verbose               - Enable verbose logging
echo.
echo For full CLI help, run: python ..\src\file_mover_cli.py --help
echo.

:end
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Failed to start File Mover
    echo Check if all required libraries are installed
    echo Try running: pip install watchdog
    echo.
    pause
) 