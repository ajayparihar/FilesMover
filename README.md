# File Mover

This project contains two Python scripts for monitoring a source directory and automatically moving new or modified files to a destination directory.

## Scripts

1. **move_files.py** - Uses a simple polling approach to monitor the source directory
2. **watchdog_file_mover.py** - Uses the `watchdog` library for event-driven file monitoring (recommended)

## Requirements

### Basic Script (move_files.py)
- Python 3.x
- No additional dependencies required

### Watchdog Script (watchdog_file_mover.py)
- Python 3.x
- Watchdog library

To install the watchdog library:
```
pip install watchdog
```

## Configuration

Both scripts are configured to monitor:
- Source directory: `C:\Users\ajays\OneDrive\Desktop\Source`
- Destination directory: `C:\Users\ajays\OneDrive\Desktop\Dest`

You can modify these paths in the scripts if needed.

## Usage

### Running the Basic Script
```
python move_files.py
```

### Running the Watchdog Script (Recommended)
```
python watchdog_file_mover.py
```

## Features

- Monitors source directory for new or modified files and folders
- Automatically moves items from source to destination
- Overwrites existing files/folders in the destination if they have the same name
- Logs all actions with timestamps
- Handles errors gracefully
- Creates the destination directory if it doesn't exist

## Differences Between Scripts

### move_files.py
- Uses a simple polling approach (checks the directory every second)
- Lower system resource usage
- May have a slight delay in detecting changes

### watchdog_file_mover.py
- Uses the watchdog library for event-driven monitoring
- More efficient and responsive to file system changes
- Handles nested directories better
- Requires an additional library installation

## Error Handling

Both scripts handle common errors such as:
- Permission issues
- File in use by another process
- Source or destination directory not existing

Errors are logged with detailed messages but won't cause the script to crash.

## Stopping the Scripts

Press `Ctrl+C` in the terminal window to stop either script. 