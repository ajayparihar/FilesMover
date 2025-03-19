#!/usr/bin/env python3
"""
Graphical interface entry point for the FilesMover utility.

This script serves as the main entry point for the FilesMover utility
when used with the graphical interface.
"""

import sys
from file_mover import run_gui

if __name__ == "__main__":
    sys.exit(run_gui()) 