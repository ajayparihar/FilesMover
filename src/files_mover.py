#!/usr/bin/env python3
"""
Main entry point for the FilesMover utility.

This script serves as the main entry point for both the CLI and GUI versions
of the FilesMover utility. It imports and uses the functionality from the 
file_mover package.

Usage:
    python files_mover.py [--gui] [options]
    
To start the GUI:
    python files_mover.py --gui
    
To use the CLI:
    python files_mover.py [cli_options]
"""

import sys
from file_mover.main import main

if __name__ == "__main__":
    sys.exit(main()) 