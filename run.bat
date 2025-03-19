@echo off
:: ===================================================
:: FilesMover Application Launcher
:: ===================================================
:: This batch file provides a convenient way to launch
:: the FilesMover application from the root directory.
:: 
:: It runs the run_file_mover.bat script from the scripts
:: directory, passing along any command-line arguments.
:: ===================================================

:: Check if --cli argument is present
set "CLI_MODE=false"
for %%a in (%*) do (
    if /i "%%a"=="--cli" set "CLI_MODE=true"
)

:: If GUI mode, hide the command window
if "%CLI_MODE%"=="false" (
    start /b "" "%~dp0scripts\run_file_mover.bat" %*
    exit
) else (
    echo Launching FilesMover Application in CLI mode...
    cd scripts
    call run_file_mover.bat %*
    cd ..
) 