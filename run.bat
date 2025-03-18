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

echo Launching FilesMover Application...
cd scripts
call run_file_mover.bat %*
cd .. 