#!/usr/bin/env python3
import os
import time
import shutil
import argparse
import logging
from pathlib import Path
import sys


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Monitor a directory and move new files to another directory.')
    parser.add_argument('source_dir', help='Directory to monitor for new files/folders')
    parser.add_argument('destination_dir', help='Directory to move files/folders to')
    parser.add_argument('--interval', type=int, default=1, help='Polling interval in seconds (default: 1)')
    return parser.parse_args()


def ensure_directories_exist(source_dir, destination_dir):
    """Ensure that source and destination directories exist."""
    # Check if source directory exists
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory '{source_dir}' does not exist")
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        try:
            os.makedirs(destination_dir)
            logger.info(f"Created destination directory: {destination_dir}")
        except PermissionError:
            raise PermissionError(f"Permission denied when creating destination directory: {destination_dir}")


def move_file_or_folder(item, source_dir, destination_dir):
    """Move a file or folder from source to destination directory."""
    source_path = os.path.join(source_dir, item)
    destination_path = os.path.join(destination_dir, item)
    
    try:
        # Check if item is a file or directory
        if os.path.exists(destination_path):
            if os.path.isdir(destination_path):
                shutil.rmtree(destination_path)
            else:
                os.remove(destination_path)
            logger.info(f"Removed existing item at destination: {destination_path}")
        
        # Move the item
        shutil.move(source_path, destination_path)
        logger.info(f"Moved: {source_path} -> {destination_path}")
        return True
    except (PermissionError, shutil.Error) as e:
        logger.error(f"Error moving {source_path}: {str(e)}")
        return False


def monitor_directory(source_dir, destination_dir, interval):
    """Monitor source directory for new files/folders and move them to destination."""
    logger.info(f"Starting to monitor: {source_dir}")
    logger.info(f"Files will be moved to: {destination_dir}")
    logger.info(f"Polling interval: {interval} seconds")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            # Get list of items in source directory
            items = os.listdir(source_dir)
            
            # Process each item in the source directory
            for item in items:
                if item != '.DS_Store':  # Skip macOS specific files
                    move_file_or_folder(item, source_dir, destination_dir)
            
            # Wait for the specified interval before checking again
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False


def main():
    try:
        args = parse_arguments()
        
        # Convert to absolute paths
        source_dir = os.path.abspath(args.source_dir)
        destination_dir = os.path.abspath(args.destination_dir)
        
        # Ensure directories exist
        ensure_directories_exist(source_dir, destination_dir)
        
        # Start monitoring
        monitor_directory(source_dir, destination_dir, args.interval)
        
    except FileNotFoundError as e:
        logger.error(str(e))
        return 1
    except PermissionError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    logger = setup_logging()
    sys.exit(main()) 