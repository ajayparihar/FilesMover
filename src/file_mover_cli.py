#!/usr/bin/env python
"""
File Mover CLI Entry Point

This script provides an entry point to the File Mover CLI application.
"""

import os
import sys

# Add the parent directory to the Python path so we can import the file_mover package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_mover.cli import main

if __name__ == "__main__":
    sys.exit(main()) 