# FilesMover

A user-friendly tool to automatically monitor and move files from a source directory to a destination directory in real-time. The application provides both a graphical user interface (GUI) and command-line interface (CLI) for flexibility.

## Table of Contents

- [User Guide](#user-guide)
  - [Features](#features)
  - [Installation](#installation)
  - [Getting Started](#getting-started)
  - [Using the GUI](#using-the-gui)
  - [Using the Command Line](#using-the-command-line)
  - [Configuration Options](#configuration-options)
  - [Troubleshooting](#troubleshooting)
- [Developer Guide](#developer-guide)
  - [Architecture Overview](#architecture-overview)
  - [Core Components](#core-components)
  - [Technology Stack](#technology-stack)
  - [Code Structure](#code-structure)
  - [Development Guidelines](#development-guidelines)
- [Additional Information](#additional-information)
  - [Version History](#version-history)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)

## User Guide

### Features

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
- **Activity-based file organization** - automatically manages files based on usage patterns
- **Settings persistence** to remember your preferences

### Installation

#### Prerequisites
- Python 3.6 or higher
- Required Python libraries:
  - watchdog (for file system monitoring)
  - tkinter (for GUI, included with Python)

#### Setup Instructions

1. **Clone or download this repository** to your local machine
   ```
   git clone https://github.com/yourusername/FilesMover.git
   cd FilesMover
   ```

2. **Install required dependencies** using pip:
   ```
   pip install -r requirements.txt
   ```

3. **Run the install script** (Windows):
   ```
   scripts\install.bat
   ```
   
   This script will:
   - Verify Python installation
   - Install required dependencies
   - Create necessary directories
   - Set up environment variables (if needed)

### Getting Started

The simplest way to get started with FilesMover is:

1. Launch the application by double-clicking `run.bat`
2. Set your source and destination folders using the "Browse" buttons
3. Click "Start Monitoring" to begin automatically moving files
4. Any new files added to your source folder will be moved to the destination folder

### Using the GUI

The graphical interface provides easy access to all features:

1. **Launch the application** by double-clicking `run.bat` or using:
   ```
   scripts\run_file_mover.bat
   ```

2. **Main Controls Tab**:
   - Set source and destination directories using the browse buttons
   - Start/Stop monitoring with the toggle button
   - Use "Move All Files" to process existing files immediately
   - View real-time activity in the log section

3. **Settings Tab**:
   - **File Handling**:
     - Conflict Mode: Choose how to handle duplicate files
     - Preserve Timestamps: Keep original file dates
     - Confirm Operations: Get prompted before replacements
   - **Performance**:
     - Recursive Monitoring: Include subdirectories
     - Processing Delay: Wait time before processing new files
   - **Activity Tracking**:
     - Enable/disable activity-based organization
     - Set inactive folder name and thresholds

4. **Help Tab**:
   - View basic usage instructions
   - Find troubleshooting tips
   - Access additional resources

### Using the Command Line

For automation and scripting, the command-line interface offers all the same functionality:

```
scripts\run_file_mover.bat --cli [options]
```

#### Basic CLI Examples:

1. **Simple monitoring** with default settings:
   ```
   scripts\run_file_mover.bat --cli -s C:\Source -d D:\Destination
   ```

2. **One-time processing** (move all files and exit):
   ```
   scripts\run_file_mover.bat --cli -s C:\Source -d D:\Destination --one-time
   ```

3. **Advanced configuration**:
   ```
   scripts\run_file_mover.bat --cli -s C:\Source -d D:\Destination -c rename -r --processing-delay 2.0
   ```

For a complete list of options, use:
```
scripts\run_file_mover.bat --cli --help
```

### Configuration Options

#### File Handling Settings

1. **Conflict Handling**:
   - **Replace**: Overwrite existing files in the destination (default)
   - **Skip**: Keep existing files in the destination, don't move new ones
   - **Rename**: Add a number suffix to new files to avoid conflicts (file.txt → file_1.txt)

2. **Preserve Timestamps**: 
   - When enabled, moved files maintain their original creation, modification, and access times
   - When disabled, files get new timestamps when moved

3. **Confirm Operations**:
   - When enabled, you'll be asked to confirm before any file is deleted or replaced
   - When disabled, operations proceed automatically without confirmation

#### Performance Settings

1. **Recursive Monitoring**:
   - When enabled, all subdirectories within the source directory will be monitored
   - When disabled, only the top-level source directory is monitored

2. **Processing Delay**:
   - Adds a delay (in seconds) before processing newly detected files
   - Useful for ensuring files are completely written before processing
   - Especially important for large files or network drives

#### Activity Tracking Settings

1. **Inactive Folder**:
   - Folder name for storing inactive files (default: "_inactive_files")
   - Created as a subdirectory of the destination directory

2. **Inactivity Threshold**:
   - Time (in seconds) before a file is considered inactive
   - Default is 7 days (604,800 seconds)

### Troubleshooting

#### Common Problems and Solutions

1. **Application won't start**:
   - Ensure Python 3.6+ is installed and in your PATH
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check permissions on the application directory

2. **Files aren't being moved**:
   - Verify source and destination paths are correct and accessible
   - Check that monitoring is actually started (status should say "Monitoring")
   - Ensure you have write permissions on both directories
   - Look for error messages in the log display or log files

3. **File access errors**:
   - Files may be locked by another process
   - Try increasing the processing delay to allow files to be fully written
   - Check for antivirus software that might be blocking operations

4. **Performance issues**:
   - Large directories with many files may cause slowdowns
   - Consider disabling recursive monitoring if not needed
   - Increase processing delay for network drives

#### Locating Log Files

Log files are automatically created in:
```
~/.file_mover/logs/file_mover_YYYYMMDD_HHMMSS.log
```

These logs contain detailed information about all operations and errors.

## Developer Guide

### Architecture Overview

FilesMover follows a modular design with clear separation of concerns:

1. **Core Module** (`core.py`):
   - Contains the core file processing logic
   - Implements `FileProcessor` for moving files between directories
   - Implements `FileEventHandler` for handling file system events
   - Provides monitoring functionality via watchdog library

2. **GUI Module** (`gui.py`):
   - Implements the graphical interface using tkinter
   - `FileMoverGUI` class manages the interface and user interactions
   - Provides tabbed interface for main controls, settings, and help
   - Implements thread-safe logging with `QueueHandler`

3. **CLI Module** (`cli.py`):
   - Provides command-line interface for the application
   - Parses command-line arguments and configures the processor
   - Supports one-time processing or continuous monitoring

4. **Activity Tracker Module** (`activity_tracker.py`):
   - Implements `FileActivityTracker` for tracking file access patterns
   - Manages inactive file storage and restoration
   - Provides thread-safe operation with the main file processor

### Core Components

1. **FileProcessor**:
   - Main class responsible for file operations
   - Handles file conflicts according to configuration
   - Preserves file timestamps when configured
   - Maintains directory structure during file moves

2. **FileEventHandler**:
   - Extends watchdog's `FileSystemEventHandler`
   - Detects file creation and modification events
   - Delegates to `FileProcessor` for handling files

3. **FileMoverGUI**:
   - Manages the tkinter interface
   - Implements settings persistence
   - Provides real-time logging display
   - Handles background processing threads

4. **FileActivityTracker**:
   - Tracks file access timestamps
   - Identifies inactive files based on access patterns
   - Moves inactive files to a designated folder
   - Restores files when they're accessed again

### Technology Stack

1. **Core Technologies**:
   - Python 3.6+: Main programming language
   - watchdog: File system monitoring
   - tkinter: GUI framework
   - threading: Concurrent operations
   - logging: Application logging

2. **File Operations**:
   - os, shutil: File system operations
   - json: Settings storage
   - queue: Thread-safe communication
   - argparse: Command-line argument parsing

### Code Structure

```
FilesMover/
├── scripts/               # Batch scripts for running the application
│   ├── install.bat        # Installation script
│   └── run_file_mover.bat # Main launcher script
├── src/                   # Source code
│   ├── file_mover/        # Main package
│   │   ├── __init__.py    # Package initialization
│   │   ├── core.py        # Core file processing functionality
│   │   ├── cli.py         # Command line interface
│   │   ├── gui.py         # Graphical user interface
│   │   └── activity_tracker.py  # Activity tracking functionality
│   ├── file_mover_cli.py  # CLI entry point
│   └── file_mover_gui.py  # GUI entry point
├── run.bat                # Convenience launcher for main app
├── requirements.txt       # Python dependencies
├── README.md              # This documentation file
└── LICENSE                # License information
```

### Development Guidelines

#### Adding New Features

1. **File Handling Extensions**:
   - Add new methods to `FileProcessor` class in `core.py`
   - Ensure proper error handling and logging
   - Update GUI and CLI interfaces to expose new functionality

2. **GUI Enhancements**:
   - Add new widgets to appropriate sections in `gui.py`
   - Update the settings storage mechanism if needed
   - Maintain consistent styling and tooltips

3. **CLI Options**:
   - Add new arguments to the parser in `cli.py`
   - Ensure backward compatibility with existing commands
   - Update help documentation

#### Coding Standards

1. **Style Guidelines**:
   - Follow PEP 8 for Python code style
   - Use docstrings for all classes and methods
   - Maintain consistent comment style

2. **Error Handling**:
   - Use appropriate try-except blocks
   - Log all errors with sufficient context
   - Display user-friendly error messages in GUI

3. **Testing**:
   - Test new features on multiple platforms
   - Verify backward compatibility
   - Test with various file types and directory structures

## Additional Information

### Version History

- **0.2.0** - Current version with activity-based file organization and improved documentation
- **0.1.0** - Initial release with basic file moving functionality

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgments

- Built with Python and Tkinter
- Uses the watchdog library for file system monitoring
- Thanks to all contributors and users for feedback and suggestions