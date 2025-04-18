@echo off
REM Batch file to run the file mover script

echo Starting File Mover...

REM Default source and destination directories
set SOURCE_DIR=C:\Users\ajays\OneDrive\Desktop\Mover\source
set DEST_DIR=C:\Users\ajays\OneDrive\Desktop\Mover\dest
set INTERVAL=1

REM Check if arguments were provided
if not "%~1"=="" set SOURCE_DIR=%~1
if not "%~2"=="" set DEST_DIR=%~2
if not "%~3"=="" set INTERVAL=%~3

echo Source directory: %SOURCE_DIR%
echo Destination directory: %DEST_DIR%
echo Polling interval: %INTERVAL% seconds

python file_mover.py %SOURCE_DIR% %DEST_DIR% --interval %INTERVAL%

echo File Mover stopped. 