"""
Core file processing functionality for the FilesMover utility.

This module provides the core file processing capabilities for moving and organizing files.
"""

from .core import FileProcessor, DirectoryMonitor, start_monitoring

__all__ = [
    'FileProcessor',
    'DirectoryMonitor',
    'start_monitoring'
]
