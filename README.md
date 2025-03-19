# FilesMover

A simple tool to automatically monitor and move files from a source directory to a destination directory in real-time. The application provides both a graphical user interface (GUI) and command-line interface (CLI).

## Features

- **Real-time file monitoring** - automatically moves files as they appear
- **Easy-to-use GUI** with intuitive controls
- **Manual processing option** - process all existing files with one click
- **Directory structure preservation** - maintains folder structure when moving files
- **File conflict handling** - options to replace, skip, or rename files
- **File timestamp preservation** - maintains original file timestamps when moving
- **Recursive monitoring** - option to monitor subdirectories
- **Processing delay control** - prevents processing incomplete files
- **Detailed activity logging**

## Project Structure

The project is organized as follows:

```
FilesMover/
├── docs/                 # Documentation
├── examples/             # Example configurations and usage
├── scripts/              # Utility scripts
├── src/                  # Source code
│   └── files_mover/      # Main package
│       ├── cli/          # Command-line interface
│       ├── core/         # Core functionality
│       ├── gui/          # Graphical user interface
│       └── utils/        # Utility functions
├── tests/                # Test suite
└── ...
```

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (included with Python standard library)

### Setup Instructions

1. Clone the repository or download the source code
2. Run the installation script:
   ```
   scripts\install.bat
   ```
   
   Or install manually:
   ```
   pip install .
   ```

## Using the Application

### Quick Start

1. Double-click `run.bat` to launch the GUI
2. Select source and destination directories
3. Click "Start Monitoring" to begin automatic file movement
4. Use "Process All Files" to immediately move existing files

### GUI Interface

The graphical interface provides easy access to all features:

1. **Main Controls Tab**:
   - Set source and destination directories using the browse buttons
   - Start/Stop monitoring with the toggle button
   - Use "Move All Files" to process existing files immediately
   - View real-time activity in the log section

2. **Settings Tab**:
   - **File Handling**:
     - Conflict Mode: Choose how to handle duplicate files
     - Preserve Timestamps: Keep original file dates
     - Confirm Operations: Get prompted before replacements
   - **Performance**:
     - Recursive Monitoring: Include subdirectories
     - Processing Delay: Wait time before processing new files
     - Poll Interval: Frequency of directory scans

### Command Line Usage

For automation and scripting, use the command-line interface:

```
run.bat --cli [options]
```

#### CLI Examples:

1. **Simple monitoring** with default settings:
   ```
   run.bat --cli -s C:\Source -d D:\Destination
   ```

2. **One-time processing** (move all files and exit):
   ```
   run.bat --cli -s C:\Source -d D:\Destination --one-time
   ```

3. **Advanced configuration**:
   ```
   run.bat --cli -s C:\Source -d D:\Destination -c rename -r --processing-delay 2.0 --poll-interval 0.5
   ```

For a complete list of options, use:
```
run.bat --cli --help
```

## Configuration Options

### File Handling Settings

1. **Conflict Handling**:
   - **Replace**: Overwrite existing files in the destination (default)
   - **Skip**: Keep existing files in the destination, don't move new ones
   - **Rename**: Add a number suffix to new files to avoid conflicts (file.txt → file_1.txt)

2. **Preserve Timestamps**: 
   - When enabled, moved files maintain their original creation and modification times

3. **Confirm Operations**:
   - When enabled, you'll be asked to confirm before replacing files

### Performance Settings

1. **Recursive Monitoring**:
   - When enabled, all subdirectories within the source directory will be monitored

2. **Processing Delay**:
   - Adds a delay (in seconds) before processing newly detected files
   - Useful for ensuring files are completely written before processing

3. **Poll Interval**:
   - Time in seconds between directory scans
   - Lower values provide faster response but increase CPU usage

## Troubleshooting

### Common Issues

1. **Files aren't being moved**:
   - Verify source and destination paths are correct and accessible
   - Check that monitoring is actually started (status should say "Monitoring")
   - Ensure you have write permissions on both directories

2. **File access errors**:
   - Files may be locked by another process
   - Try increasing the processing delay
   - Check for antivirus software that might be blocking operations

## License

This project is licensed under the MIT License - see the LICENSE file for details.