# FilesMover Developer Documentation

This document provides technical information about the FilesMover codebase for developers who want to understand, maintain, or extend the application.

## Project Information

- **Version**: 0.2.0
- **Developer**: Bheb Developer
- **License**: MIT

## Code Structure

The FilesMover application is organized as follows:

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
└── requirements.txt       # Python dependencies
```

## Core Modules

### Core Module (`core.py`)

The `core.py` module provides the core file processing functionality. Key components include:

- `FileProcessor`: Main class for processing and moving files between directories
- `FileEventHandler`: Watchdog event handler for file system events
- `start_monitoring()`: Convenience function to start file monitoring

The `FileProcessor` class handles both one-time processing (via `process_all()`) and continuous monitoring (via `start_monitoring()`).

### Activity Tracker Module (`activity_tracker.py`)

This module provides functionality for tracking file activity and organizing files based on usage patterns:

- `FileActivityTracker`: Main class for tracking file activity and organizing inactive files
- `FileActivityEventHandler`: Watchdog event handler for tracking file access events

Files that haven't been accessed for a specified period are moved to an inactive folder, and automatically restored when accessed.

### CLI Module (`cli.py`)

The `cli.py` module implements the command-line interface for the application:

- `parse_arguments()`: Parses command-line arguments
- `main()`: Main CLI entry point

### GUI Module (`gui.py`)

The `gui.py` module implements the graphical user interface:

- `FileMoverGUI`: Main GUI class with tabbed interface
- `QueueHandler`: Custom logging handler for thread-safe GUI updates
- `CreateToolTip`: Utility class for tooltip creation

## Extension Points

Here are the main ways to extend FilesMover:

### Adding New Features

1. **Add Command-Line Options**

   To add a new command-line option, modify `parse_arguments()` in `cli.py`:

   ```python
   parser.add_argument(
       '--new-option',
       help='Description of new option',
       action='store_true'
   )
   ```

2. **Add GUI Controls**

   To add new GUI controls, modify the appropriate tab creation method in `FileMoverGUI` class:

   ```python
   def create_settings_tab(self, parent):
       # Add new controls here
       new_control_frame = ttk.Frame(parent)
       new_control_frame.pack(fill=tk.X, pady=5)
       # ...
   ```

3. **Extend File Processing**

   To modify how files are processed, extend the `FileProcessor` class:

   ```python
   class ExtendedFileProcessor(FileProcessor):
       def process_file(self, src_path):
           # Add custom processing logic here
           super().process_file(src_path)
   ```

### Adding Custom File Handling

To add custom handling for specific file types:

1. Create a new subclass of `FileProcessor`
2. Override the `process_file` method
3. Implement your custom logic

Example:

```python
class MediaFileProcessor(FileProcessor):
    def process_file(self, src_path):
        if src_path.endswith(('.mp3', '.mp4', '.jpg', '.png')):
            # Special handling for media files
            # ...
        else:
            # Use default handling for other files
            super().process_file(src_path)
```

## Logging

The application uses Python's built-in logging module:

- Log files are stored in `~/.file_mover/logs/`
- Both the CLI and GUI interfaces log to files with timestamped names
- The GUI has a custom `QueueHandler` for thread-safe logging

Add logging to your extensions as follows:

```python
import logging
logging.info("Informational message")
logging.error("Error message")
```

## Settings Management

Settings are stored in JSON format:

- File location: `~/.file_mover/settings.json`
- GUI settings can be saved/loaded via the Settings tab
- CLI settings must be provided as command-line arguments

## Threading Considerations

The application uses threading to prevent UI freezing:

- File monitoring runs in a separate thread via watchdog's `Observer`
- One-time processing in the GUI runs in a background thread
- Activity tracking uses a dedicated thread for checking inactive files

When extending the code, be careful with thread safety, especially when accessing shared resources.

## Testing

To test modifications:

1. Create test directories with sample files
2. Run the application with your changes
3. Verify the expected behavior

For CLI testing:

```
scripts\run_file_mover.bat --cli -s test_source -d test_dest
```

For GUI testing, run the application and interact with your new features.

## Contributing

When contributing to FilesMover:

1. Follow the existing code style
2. Add comprehensive docstrings
3. Include comments for complex logic
4. Update README.md and this developer documentation as needed 