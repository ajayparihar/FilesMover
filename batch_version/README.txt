======================================================
                FilesMover - Batch Version
======================================================

This is a Windows batch script version of the FilesMover utility, designed
to work on systems without Python or Watchdog installed.

FEATURES:
---------
- Continuously monitors a source directory for new files
- Automatically moves files to destination folders based on file extensions
- Configurable conflict resolution (rename, replace, or skip)
- Logs all activity to a log file
- No external dependencies, works on any Windows system

SETUP & CONFIGURATION:
----------------------
1. Edit the config.ini file to set your source and destination directories:
   - SourceDir: The directory to monitor for new files
   - DestinationDir: The base directory where files will be moved to
   - PollInterval: How often to check for new files (in seconds)
   - ConflictMode: How to handle file conflicts (rename, replace, or skip)
   - ProcessExisting: Whether to process existing files when starting (true/false)

2. File extension mappings are configured in the [Extensions] section of config.ini:
   - Each line defines a destination folder and the extensions to move there
   - Format: FolderName=.ext1,.ext2,.ext3
   - Example: Documents=.doc,.docx,.pdf,.txt

USAGE:
------
1. Simply double-click on run.bat to start the program
   - This will launch the file monitoring in the background
   - Check the logs at %USERPROFILE%\.file_mover\logs

2. To run in console mode (to see log output):
   - Double-click FilesMover.bat directly
   - Press Ctrl+C to stop the monitoring

TROUBLESHOOTING:
---------------
- Check the log files at %USERPROFILE%\.file_mover\logs for error messages
- Ensure that the source and destination directories exist and are accessible
- Verify that you have write permissions to both directories
- If files aren't being moved, check that their extensions are defined in config.ini 