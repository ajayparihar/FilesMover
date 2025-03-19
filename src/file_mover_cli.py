#!/usr/bin/env python3
"""
Command-line entry point for the FilesMover utility.

This script serves as the main entry point for the FilesMover utility
when used from the command line.

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
"""

import sys
from file_mover import run_cli

if __name__ == "__main__":
    sys.exit(run_cli()) 