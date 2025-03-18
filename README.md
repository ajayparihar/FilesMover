# File Mover

A user-friendly tool to automatically move files from a source directory to a destination directory. The application monitors a folder for new files or modifications and moves them in real-time to a destination folder.

## Features

- **Easy-to-use GUI** with intuitive controls and helpful tooltips
- **Real-time file monitoring** - automatically moves files as they appear
- **Manual processing option** - process all existing files with one click
- **Directory structure preservation** - maintains folder structure when moving files
- **Detailed activity logging** with color-coded status messages
- **Command-line interface** for automation and scripting
- **Simple unified launcher** to run either GUI or CLI versions
- **Settings persistence** to remember your preferences
- **Automatic log file creation** for tracking all operations

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
   install.bat
   ```
3. This will install required dependencies and optionally create a desktop shortcut

## Usage

### GUI Application

1. Double-click `run_file_mover.bat` to start the application
2. Set your source and destination directories (or use the defaults)
3. Click "Start Monitoring" to begin automatic file moving
4. Files added to the source directory will be automatically moved to the destination

### Command-line Interface

For automation or scripting, use the command-line interface:

```
run_file_mover.bat --cli [options]
```

Available CLI options:
- `-s, --source`: Source directory path (default: ~/Desktop/Source)
- `-d, --destination`: Destination directory path (default: ~/Desktop/Dest)
- `-o, --one-time`: Process existing files once and exit
- `--verbose`: Enable verbose logging

For full command-line help:
```
run_file_mover.bat --help
```

## Code Structure

The application has been optimized for simplicity and maintainability:

- `core_file_mover.py` - Core functionality for file moving and monitoring
- `file_mover_gui.py` - Graphical user interface
- `file_mover_cli.py` - Command-line interface
- `run_file_mover.bat` - Unified launcher script

## Application Data

The application stores its data in the user's home directory:

- Settings: `~/.file_mover/settings.json`
- Log files: `~/.file_mover/logs/file_mover_[timestamp].log`

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
- **Additional log information**: Check the log files in `~/.file_mover/logs/` for detailed operation logs

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