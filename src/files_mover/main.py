#!/usr/bin/env python3
"""
Main entry point for the FilesMover application.

This module provides a unified entry point for the FilesMover application,
allowing users to launch either the GUI or CLI version.

Usage:
    python -m files_mover [--gui] [cli_options]
"""

import sys
import argparse
from .cli.cli import run_cli
from .gui.gui import run_gui

def parse_main_args():
    """
    Parse the command-line arguments for the main entry point.
    
    Returns:
        tuple: (use_gui, remaining_args) where use_gui is a boolean 
               and remaining_args is a list of unparsed arguments
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--gui', action='store_true', help='Start with graphical user interface')
    
    # Parse just the --gui argument, ignore the rest
    args, remaining = parser.parse_known_args()
    
    return args.gui, remaining

def main():
    """
    Main entry function that dispatches to either GUI or CLI.
    
    This function parses the command-line arguments to determine whether
    to launch the GUI or CLI version of the application, then calls
    the appropriate entry point.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    use_gui, remaining_args = parse_main_args()
    
    # If --gui is specified, start the GUI
    if use_gui:
        return run_gui()
    
    # Otherwise, pass remaining arguments to the CLI
    sys.argv[1:] = remaining_args
    return run_cli()

if __name__ == "__main__":
    sys.exit(main()) 