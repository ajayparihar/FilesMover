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
    activity_tracker: File activity tracking and organization
    cli: Command-line interface
    gui: Graphical user interface

Classes:
    FileProcessor: Main class for processing and moving files
    FileActivityTracker: Tracks file activity and moves files based on usage
    
Functions:
    start_monitoring: Convenience function to start monitoring a directory
"""

from .core import FileProcessor, start_monitoring
from .activity_tracker import FileActivityTracker

__all__ = ['FileProcessor', 'start_monitoring', 'FileActivityTracker']

# Package version information
__version__ = "0.2.0"
__author__ = "Bheb Developer"
__license__ = "MIT" 