#!/usr/bin/env python3
"""
FilesMover launcher script

This script provides a simple way to run the FilesMover application
without installation. It automatically adds the src directory to
the Python path and launches either the GUI or CLI version based
on command-line arguments.

Usage:
    python run.py [--gui] [cli_options]
"""

import os
import sys
import argparse

# Add the src directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, "src")
sys.path.insert(0, src_dir)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--gui', action='store_true', help='Start with graphical user interface')
    args, remaining = parser.parse_known_args()
    return args.gui, remaining

if __name__ == "__main__":
    # Check if the src directory exists
    if not os.path.isdir(src_dir):
        print(f"Error: Source directory not found at {src_dir}")
        sys.exit(1)
        
    use_gui, remaining_args = parse_args()
    
    if use_gui:
        # Launch the GUI version
        from file_mover.gui import run_gui
        sys.exit(run_gui())
    else:
        # Update sys.argv with remaining arguments
        sys.argv[1:] = remaining_args
        
        # Launch the CLI version
        from file_mover.cli import run_cli
        sys.exit(run_cli()) 