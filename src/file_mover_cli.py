#!/usr/bin/env python
"""
FilesMover CLI Entry Point

This script provides an entry point to the FilesMover CLI application.
It serves as a convenient way to launch the command-line interface
for the file mover functionality.

Usage:
    python file_mover_cli.py [options]

Available options:
    -s, --source SOURCE       Source directory path
    -d, --destination DEST    Destination directory path
    -o, --one-time            Process existing files once and exit
    -a, --activity-tracking   Enable activity-based file organization
    -t, --inactive-threshold  Inactivity threshold in days (default: 7)
    --verbose                 Enable verbose logging
    -l, --log-file LOG_FILE   Custom log file path

The script imports the main function from the file_mover.cli module 
and calls it when executed directly, passing the return code to sys.exit().
"""

import os
import sys

# Add the parent directory to the Python path so we can import the file_mover package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_mover.cli import main

if __name__ == "__main__":
    sys.exit(main()) 