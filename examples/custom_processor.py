#!/usr/bin/env python3
"""
Example showing how to extend FilesMover with custom file processing.

This example demonstrates creating a custom file processor that sorts files
into subdirectories based on their file extensions.
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the core functionality from files_mover
from src.files_mover.core.core import FileProcessor

class CustomFileProcessor(FileProcessor):
    """Custom file processor that sorts files by extension."""
    
    def process_file(self, source_path):
        """
        Process a file by moving it to a subdirectory based on its extension.
        
        Args:
            source_path (str): Path to the source file
        
        Returns:
            bool: True if file was processed successfully, False otherwise
        """
        # Get the file extension (without the dot)
        file_extension = os.path.splitext(source_path)[1][1:].lower()
        
        # If no extension, use "unknown" folder
        if not file_extension:
            file_extension = "unknown"
        
        # Create the destination subdirectory if it doesn't exist
        dest_subdir = os.path.join(self.dest_dir, file_extension)
        os.makedirs(dest_subdir, exist_ok=True)
        
        # Get the destination path
        dest_path = os.path.join(dest_subdir, os.path.basename(source_path))
        
        # Let the parent class handle the actual file moving with conflict resolution
        return super().process_file(source_path, dest_path)

def main():
    """Run the custom file processor example."""
    # Define source and destination directories
    source_dir = input("Enter source directory: ")
    dest_dir = input("Enter destination directory: ")
    
    # Create and configure the custom processor
    processor = CustomFileProcessor(source_dir, dest_dir)
    processor.include_subdirs = True
    processor.conflict_handling = "rename"
    
    # Process existing files immediately
    print(f"Processing files from {source_dir} to {dest_dir}...")
    processor.process_existing_files()
    
    print("Processing complete. Files sorted by extension.")

if __name__ == "__main__":
    main() 