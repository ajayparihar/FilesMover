# FilesMover

A user-friendly tool to automatically move files from a source directory to a destination directory. The application monitors a folder for new files or modifications and moves them in real-time to a destination folder.

## Features

- **Easy-to-use GUI** with intuitive controls and helpful tooltips
- **Real-time file monitoring** - automatically moves files as they appear
- **Manual processing option** - process all existing files with one click
- **Directory structure preservation** - maintains folder structure when moving files
- **Advanced file conflict handling** - options to replace, skip, or rename files
- **File timestamp preservation** - maintains original file timestamps when moving
- **File deletion confirmation** - provides protection for important destination files
- **Recursive monitoring** - option to monitor subdirectories
- **Processing delay control** - prevents processing incomplete files
- **Detailed activity logging** with status messages
- **Command-line interface** for automation and scripting
- **Simple unified launcher** to run either GUI or CLI versions
- **Settings persistence** to remember your preferences
- **Automatic log file creation** for tracking all operations
- **Comprehensive documentation** for both users and developers
- **File organization utility** to arrange files into categorized directories
- **File cleanup utility** to remove unnecessary files and free up space
- **File organization utility** with automatic cleanup of unnecessary files

## Installation

### Prerequisites
- Python 3.6 or higher
- Required Python libraries:
  - watchdog (for file system monitoring)
  - tkinter (for GUI, included with Python)

### Setup

1. Clone or download this repository
2. Run the install.bat file to set up the application:
   ```
   scripts\install.bat
   ```
   
For detailed installation instructions, see [INSTALL.md](INSTALL.md).

## Usage

### GUI Mode (Default)

1. Run the application by double-clicking `run.bat` or using:
   ```
   scripts\run_file_mover.bat
   ```
2. Set the source and destination directories using the interface
3. Click "Start Monitoring" to begin watching for files, or "Move All Files" to process existing files

### Command Line Mode

Run the application in CLI mode using:
```
scripts\run_file_mover.bat --cli
```

#### CLI Options:
```
-s, --source SOURCE             Source directory path
-d, --destination DEST          Destination directory path
-o, --one-time                  Process existing files once and exit
-c, --conflict-mode MODE        How to handle file conflicts (replace, skip, rename)
-p, --preserve-timestamps       Preserve file timestamps when moving (default)
--no-preserve-timestamps        Do not preserve file timestamps
--confirm-operations            Confirm before replacing or deleting files (default)
--no-confirm-operations         Do not confirm before replacing or deleting files
-r, --recursive                 Monitor subdirectories recursively
--processing-delay SECONDS      Delay before processing newly detected files
--verbose                       Enable verbose logging
-l, --log-file LOG_FILE         Custom log file path
```

### File Organization Utility

FilesMover includes a dedicated utility for organizing files into categorized directories and cleaning up unnecessary files:

```
arrange_files.bat [source_dir] [destination_dir] [options]
```

#### Organization Options:
```
--recursive, -r            Process subdirectories recursively
--keep-unnecessary, -k     Keep unnecessary files (don't remove them)
```

This utility:

1. Creates the following directory structure in the destination folder and moves files based on their extensions:
   - **documents/** - Text files, documents, spreadsheets, presentations (.txt, .doc, .pdf, .xlsx, etc.)
   - **images/** - Image files (.jpg, .png, .gif, etc.)
   - **audio/** - Audio files (.mp3, .wav, .flac, etc.)
   - **video/** - Video files (.mp4, .avi, .mkv, etc.)
   - **archives/** - Compressed archives (.zip, .rar, .7z, etc.)
   - **code/** - Source code and programming files (.py, .js, .html, etc.)
   - **executables/** - Executable and installable files (.exe, .msi, .bat, etc.)
   - **misc/** - Any other file types not covered above

2. Automatically removes unnecessary files during organization:
   - Temporary files (*.tmp, *.temp, ~*, etc.)
   - Thumbnail caches (Thumbs.db, .DS_Store, etc.)
   - Log files (*.log, *.log.*)
   - Compiled code (*.pyc, __pycache__, etc.)
   - IDE and editor files (.vscode, .idea, etc.)

### File Cleanup Utility

FilesMover includes a utility to identify and remove unnecessary files:

```
cleanup.bat [directory] [options]
```

#### Cleanup Options:
```
--recursive, -r            Process subdirectories recursively
--dry-run, -d              Only report files without deleting (default)
--trash DIR, -t DIR        Move files to this directory instead of deleting
--min-size SIZE, -s SIZE   Minimum file size in bytes to consider
--days-unused DAYS, -u DAYS  Remove files not accessed in this many days
--pattern PATTERN, -p PATTERN  Additional file pattern to match
```

This utility identifies and removes unnecessary files such as:
- Temporary files (*.tmp, *.temp, ~*, etc.)
- Thumbnail caches (Thumbs.db, .DS_Store, etc.)
- Browser caches (*.crdownload, *.part, etc.)
- Log files (*.log, *.log.*)
- Compiled code (*.pyc, __pycache__, etc.)
- Debug files (*.pdb, *.dmp, etc.)
- Package management files (node_modules, etc.)
- IDE and editor files (.vscode, .idea, etc.)

By default, it runs in "dry-run" mode to show what would be removed without actually deleting anything. Use the `--no-dry-run` option to actually remove files.

Note: This functionality is now integrated into the File Organization Utility. Use `arrange_files.bat` with the `--keep-unnecessary` option to skip cleanup during organization.

## File Handling Settings

FilesMover provides several options to control how files are handled:

1. **Conflict Handling**: Choose how to handle files with the same name in the destination:
   - Replace: Overwrite existing files (default)
   - Skip: Keep existing files, don't move new ones
   - Rename: Add a number to new files to avoid conflicts

2. **Preserve Timestamps**: When enabled, moved files maintain their original creation, modification, and access times.

3. **Confirm Deletions**: When enabled, you'll be asked to confirm before any file is deleted or replaced in the destination directory.

## Performance Settings

Performance-related settings allow you to optimize how FilesMover works:

1. **Recursive Monitoring**: When enabled, all subdirectories within the source directory will be monitored.

2. **Processing Delay**: Adds a delay before processing newly detected files. This is useful to ensure files are completely written before being moved, especially for large files or network drives.

## Code Structure

The application follows a modular design:

```
FilesMover/
├── scripts/               # Batch scripts for running the application
│   ├── install.bat        # Installation script
│   ├── run_file_mover.bat # Main launcher script
│   ├── organize_files.bat # File organization script
│   └── cleanup_files.bat  # File cleanup script
├── src/                   # Source code
│   ├── file_mover/        # Main package
│   │   ├── __init__.py    # Package initialization
│   │   ├── core.py        # Core file processing functionality
│   │   ├── cli.py         # Command line interface
│   │   ├── gui.py         # Graphical user interface
│   │   ├── organize_files.py # File organization utility
│   │   └── cleanup_files.py  # File cleanup utility
│   ├── file_mover_cli.py  # CLI entry point
│   └── file_mover_gui.py  # GUI entry point
├── run.bat                # Convenience launcher for main app
├── organize.bat           # Convenience launcher for file organization
├── cleanup.bat            # Convenience launcher for file cleanup
├── setup.py               # Setup script
├── requirements.txt       # Python dependencies
├── INSTALL.md             # Detailed installation instructions
└── DEVELOPER.md           # Documentation for developers
```

For detailed developer documentation, see [DEVELOPER.md](DEVELOPER.md).

## Troubleshooting

If you encounter issues while using FilesMover, consider the following solutions:

- **Ensure Python is installed correctly**: Verify that Python 3.6 or higher is installed and added to your system's PATH.
- **Check dependencies**: Make sure all required Python libraries are installed. You can reinstall them using:
  ```
  pip install -r requirements.txt
  ```
- **File permissions**: Ensure that the application has the necessary permissions to read from the source directory and write to the destination directory.
- **Log files**: Check the log files for any error messages or warnings that might indicate the problem.

For further assistance, please refer to the [DEVELOPER.md](DEVELOPER.md) or contact support.

## Version History

- **0.2.0** - Current version with activity-based file organization and improved documentation
- **0.1.0** - Initial release with basic file moving functionality

## Author

Developed by Bheb Developer

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and Tkinter
- Uses the watchdog library for file system monitoring