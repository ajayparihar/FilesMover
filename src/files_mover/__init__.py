"""
FilesMover - A utility for organizing and moving files automatically.

This package provides tools for file organization and monitoring. It can
automatically move files from a source directory to a destination directory,
either in response to file system events or as a one-time operation.

The package also includes functionality for tracking file activity and
organizing files based on usage patterns, moving inactive files to a
separate location and restoring them when accessed.

Modules:
    core: Core file processing functionality
    utils: Utility functions including activity tracking
    cli: Command-line interface
    gui: Graphical user interface

Classes:
    FileProcessor: Main class for processing and moving files
    DirectoryMonitor: Monitors directories for file changes
    FileActivityTracker: Tracks file activity and moves files based on usage
    
Functions:
    start_monitoring: Convenience function to start monitoring a directory
"""

from .core.core import FileProcessor, DirectoryMonitor, start_monitoring
from .utils.activity_tracker import FileActivityTracker
from .cli.cli import run_cli
from .gui.gui import run_gui

__all__ = [
    # Core functionality
    'FileProcessor', 
    'DirectoryMonitor', 
    'start_monitoring', 
    'FileActivityTracker',
    
    # Entry points
    'run_cli',
    'run_gui'
]

# Package version information
__version__ = "0.3.0"
__author__ = "Bheb Developer"
__license__ = "MIT"
