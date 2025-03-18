"""
FilesMover - A utility for organizing and moving files automatically.

This package provides tools for file organization and monitoring.
"""

from .core import FileProcessor, start_monitoring
from .activity_tracker import FileActivityTracker

__all__ = ['FileProcessor', 'start_monitoring', 'FileActivityTracker']

__version__ = "0.2.0" 