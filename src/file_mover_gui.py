#!/usr/bin/env python
"""
FilesMover GUI Entry Point

This script provides an entry point to the FilesMover GUI application.
It serves as a convenient way to launch the graphical user interface
for the file mover functionality.

Usage:
    python file_mover_gui.py

The script imports the main function from the file_mover.gui module 
and calls it when executed directly.
"""

import os
import sys

# Add the parent directory to the Python path so we can import the file_mover package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_mover.gui import main

if __name__ == "__main__":
    main() 