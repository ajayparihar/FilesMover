# FilesMover

A user-friendly tool to automatically move files from a source directory to a destination directory. The application monitors a folder for new files or modifications and moves them in real-time to a destination folder.

## Features

- **Easy-to-use GUI** with intuitive controls and helpful tooltips
- **Real-time file monitoring** - automatically moves files as they appear
- **Manual processing option** - process all existing files with one click
- **Directory structure preservation** - maintains folder structure when moving files
- **Activity-based file organization** - automatically organizes files based on usage patterns
- **Detailed activity logging** with status messages
- **Command-line interface** for automation and scripting
- **Simple unified launcher** to run either GUI or CLI versions
- **Settings persistence** to remember your preferences
- **Automatic log file creation** for tracking all operations
- **Comprehensive documentation** for both users and developers

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
-s, --source SOURCE       Source directory path
-d, --destination DEST    Destination directory path
-o, --one-time            Process existing files once and exit
-a, --activity-tracking   Enable activity-based file organization
-t, --inactive-threshold  Inactivity threshold in days (default: 7)
--verbose                 Enable verbose logging
-l, --log-file LOG_FILE   Custom log file path
```

## Activity-Based File Organization

When activity tracking is enabled, FilesMover will:

1. Monitor file access patterns in your source directory
2. Move files that haven't been accessed for a specified period (default: 7 days) to a special "_inactive_files" folder
3. Automatically restore files to their original location when they are accessed again

This feature helps keep your workspace clean while ensuring all files remain accessible.

## Code Structure

The application follows a modular design:

```
FilesMover/
├── scripts/               # Batch scripts for running the application
│   ├── install.bat        # Installation script
│   └── run_file_mover.bat # Main launcher script
├── src/                   # Source code
│   ├── file_mover/        # Main package
│   │   ├── __init__.py    # Package initialization
│   │   ├── core.py        # Core file processing functionality
│   │   ├── activity_tracker.py # Activity-based file organization
│   │   ├── cli.py         # Command line interface
│   │   └── gui.py         # Graphical user interface
│   ├── file_mover_cli.py  # CLI entry point
│   └── file_mover_gui.py  # GUI entry point
├── run.bat                # Convenience launcher
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