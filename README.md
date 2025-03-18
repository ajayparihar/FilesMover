# File Mover

A user-friendly tool to automatically move files from a source directory to a destination directory. The application monitors a folder for new files or modifications and moves them in real-time to a destination folder.

![File Mover Screenshot](screenshots/file_mover_screenshot.png)

## Features

- **Easy-to-use GUI** with intuitive controls and helpful tooltips
- **Real-time file monitoring** - automatically moves files as they appear
- **Manual processing option** - process all existing files with one click
- **Directory structure preservation** - maintains folder structure when moving files
- **Detailed activity logging** with color-coded status messages
- **File counter** to track operations
- **Progress indicators** to show active monitoring
- **Error handling** with clear error messages
- **Help documentation** built into the application
- **Customizable settings** for tailored operation

## Installation

### Prerequisites
- Python 3.6 or higher
- Required Python libraries:
  - tkinter (usually comes with Python)
  - watchdog

### Setup

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install watchdog
   ```
3. Run the application using the provided batch file or directly with Python

## Usage

### GUI Application (Recommended)

1. Double-click `run_file_mover_gui.bat` to start the GUI application
2. Set your source and destination directories (or use the defaults)
3. Click "Start Monitoring" to begin automatic file moving
4. Files added to the source directory will be automatically moved to the destination

### Command-line Version

If you prefer a command-line version:

1. Run `watchdog_file_mover.py` for continuous monitoring:
   ```
   python watchdog_file_mover.py
   ```
   
2. Or run `move_files.py` for the simple polling version:
   ```
   python move_files.py
   ```

## GUI Overview

The GUI application is organized into tabs for better usability:

### Main Tab
- Configure source and destination directories
- Start and stop monitoring
- Trigger manual file moving
- View activity log

### Settings Tab
- Auto-start monitoring option
- Auto-create directories option
- Other customizable settings

### Help Tab
- Quick start guide
- Feature explanations
- Tips and tricks

## How It Works

The application uses the watchdog library to monitor the source directory for file system events:

1. When a file is created or modified in the source directory, it triggers an event
2. The application processes the event by moving the file to the destination
3. If a file with the same name already exists in the destination, it is overwritten
4. All activity is logged with timestamps for reference

## Common Use Cases

- **Automated file sorting**: Move files from a download folder to organized locations
- **Backup solution**: Automatically backup new files to another location
- **Workflow automation**: Move processed files to the next stage in a workflow
- **Network drive syncing**: Move files from local to network storage

## Troubleshooting

### Common Issues and Solutions

- **Files not moving**: Ensure both source and destination paths are valid and accessible
- **Application not starting**: Check if Python and required libraries are installed
- **Permission errors**: Run the application with appropriate permissions
- **Files in use**: Some files may not move if they are currently in use by other applications

## Contributing

Contributions are welcome! If you'd like to improve the application:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Built with [Python](https://www.python.org/)
- File monitoring powered by [Watchdog](https://github.com/gorakhargosh/watchdog) 