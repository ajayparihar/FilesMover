#!/usr/bin/env python3
"""
FilesMover Simple Launcher

This script provides a simple way to run the FilesMover Simple application
without installation. It automatically adds the simple_version directory to
the Python path and launches the application.

Usage:
    python run_simple.py [options]
"""

import os
import sys
import argparse

# Add the simple_version directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
simple_dir = os.path.join(script_dir, "simple_version")
sys.path.insert(0, simple_dir)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='FilesMover Simple - Launcher')
    
    # Forward all arguments to the main script
    args, remaining = parser.parse_known_args()
    return remaining

if __name__ == "__main__":
    # Check if the simple_version directory exists
    if not os.path.isdir(simple_dir):
        os.makedirs(simple_dir, exist_ok=True)
        print(f"Created directory: {simple_dir}")
    
    # Update sys.argv with remaining arguments
    remaining_args = parse_args()
    sys.argv[1:] = remaining_args
    
    try:
        # Import and run the main function from files_mover_simple
        sys.path.insert(0, simple_dir)
        from files_mover_simple import main
        sys.exit(main())
    except ImportError:
        print("Error: Could not import files_mover_simple module.")
        print(f"Make sure files_mover_simple.py exists in {simple_dir}")
        sys.exit(1) 