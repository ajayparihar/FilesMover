@echo off
echo ======================================================
echo              FilesMover - Batch Launcher  
echo ======================================================
echo.

start /b "" "%~dp0FilesMover.bat"
echo FilesMover is now running in the background.
echo Check the logs at %USERPROFILE%\.file_mover\logs
echo.

exit 