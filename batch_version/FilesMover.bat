@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo              FilesMover - Batch Version  
echo ======================================================
echo.

:: Initialize variables
set "SCRIPT_DIR=%~dp0"
set "CONFIG_FILE=%SCRIPT_DIR%config.ini"
set "LOG_DIR=%USERPROFILE%\.file_mover\logs"
set "RUNNING=true"
set "MONITOR_COUNT=0"

:: Create log directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Set log file with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "LOG_FILE=%LOG_DIR%\file_mover_%dt:~0,8%_%dt:~8,6%.log"

:: Load configuration
call :log "Loading configuration from %CONFIG_FILE%"
if not exist "%CONFIG_FILE%" (
    call :log "ERROR: Configuration file not found!"
    exit /b 1
)

:: Read config.ini (settings section only)
for /f "usebackq tokens=1,2 delims==" %%a in ("%CONFIG_FILE%") do (
    if "%%a"=="SourceDir" set "SourceDir=%%b"
    if "%%a"=="DestinationDir" set "DestinationDir=%%b"
    if "%%a"=="PollInterval" set "PollInterval=%%b"
    if "%%a"=="ConflictMode" set "ConflictMode=%%b"
    if "%%a"=="ProcessExisting" set "ProcessExisting=%%b"
)

:: Load extension mappings into memory
call :log "Loading extension mappings"
set "ExtList="
set "EXTENSIONS_LOADED=false"
for /f "usebackq tokens=1,2 delims==" %%a in ("%CONFIG_FILE%") do (
    if "!EXTENSIONS_LOADED!"=="true" (
        if not "%%a"=="" if not "%%a:~0,1"=="[" (
            set "Folder_%%a=%%b"
            set "ExtList=!ExtList! %%a"
            call :log "Added extension group: %%a = %%b"
        )
    )
    if "%%a"=="[Extensions]" set "EXTENSIONS_LOADED=true"
)

:: Expand variables in paths
call set "SourceDir=!SourceDir!"
call set "DestinationDir=!DestinationDir!"

call :log "Source directory: !SourceDir!"
call :log "Destination directory: !DestinationDir!"

:: Validate configuration
if not exist "!SourceDir!" (
    call :log "ERROR: Source directory does not exist: !SourceDir!"
    mkdir "!SourceDir!" 2>nul
    call :log "Created source directory: !SourceDir!"
)

if not exist "!DestinationDir!" (
    call :log "ERROR: Destination directory does not exist: !DestinationDir!"
    mkdir "!DestinationDir!" 2>nul
    call :log "Created destination directory: !DestinationDir!"
)

:: Process existing files if enabled
if /i "!ProcessExisting!"=="true" (
    call :log "Processing existing files in !SourceDir!"
    call :process_directory "!SourceDir!"
)

:: Start monitoring loop
call :log "Starting directory monitoring... (Press Ctrl+C to stop)"
echo.
echo Press Ctrl+C to stop monitoring
echo.

:monitor_loop
    set /a MONITOR_COUNT+=1
    call :log "Monitoring cycle #!MONITOR_COUNT!"
    
    call :process_directory "!SourceDir!"
    
    :: Sleep for PollInterval seconds
    timeout /t !PollInterval! /nobreak >nul
    
    :: Check if we should still be running
    if "!RUNNING!"=="true" goto :monitor_loop

exit /b 0

:: ==========================================
:: Function to process a directory
:: ==========================================
:process_directory
    setlocal enabledelayedexpansion
    set "dir_path=%~1"
    
    call :log "Processing directory: !dir_path!"
    
    :: Process all files in the directory
    for %%F in ("!dir_path!\*.*") do (
        if not "%%~aF:~0,1"=="d" (
            call :process_file "%%F"
        )
    )
    
    :: Process subdirectories recursively
    for /d %%D in ("!dir_path!\*") do (
        call :process_directory "%%D"
    )
    
    endlocal
    exit /b 0

:: ==========================================
:: Function to process a file
:: ==========================================
:process_file
    setlocal enabledelayedexpansion
    set "file_path=%~1"
    set "file_name=%~nx1"
    set "file_ext=%~x1"
    
    call :log "Found file: !file_name!"
    
    :: Convert extension to lowercase for comparison
    set "ext=!file_ext!"
    for %%i in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do set "ext=!ext:%%i=%%i!"
    
    :: Find matching extension group
    set "target_folder="
    
    :: Improved extension matching
    for %%a in (!ExtList!) do (
        call :log "Checking extension group: %%a"
        set "ext_list=!Folder_%%a!"
        
        :: Check if the extension is in the list
        for %%e in (!ext_list!) do (
            if "!ext!"=="%%e" (
                set "target_folder=%%a"
                call :log "Match found: !ext! in extension group %%a"
                goto :found_folder
            )
        )
    )
    
    :found_folder
    if "!target_folder!"=="" (
        call :log "No matching folder for !file_name! (extension: !ext!)"
        exit /b 0
    )
    
    :: Create destination folder if it doesn't exist
    set "dest_dir=!DestinationDir!\!target_folder!"
    if not exist "!dest_dir!" (
        mkdir "!dest_dir!"
        call :log "Created destination folder: !dest_dir!"
    )
    
    :: Handle file conflict according to configuration
    set "dest_path=!dest_dir!\!file_name!"
    
    if exist "!dest_path!" (
        if /i "!ConflictMode!"=="skip" (
            call :log "Skipped (already exists): !file_name!"
            exit /b 0
        ) else if /i "!ConflictMode!"=="rename" (
            set counter=1
            :rename_loop
            if exist "!dest_dir!\!file_name:~0,-4!_!counter!!file_ext!" (
                set /a counter+=1
                goto :rename_loop
            )
            set "dest_path=!dest_dir!\!file_name:~0,-4!_!counter!!file_ext!"
            call :log "Renamed due to conflict: !file_name! -> !file_name:~0,-4!_!counter!!file_ext!"
        )
        :: For "replace" mode, we just continue with the move operation
    )
    
    :: Move the file
    call :log "Moving file: !file_path! to !dest_path!"
    move "!file_path!" "!dest_path!"
    
    if !errorlevel! equ 0 (
        call :log "Successfully moved file: !file_name! to !target_folder!"
    ) else (
        call :log "ERROR: Failed to move file: !file_name!"
    )
    
    endlocal
    exit /b 0

:: ==========================================
:: Function to log messages
:: ==========================================
:log
    set "msg=%~1"
    echo %date% %time% - %msg%
    echo %date% %time% - %msg% >> "%LOG_FILE%"
    exit /b 0 