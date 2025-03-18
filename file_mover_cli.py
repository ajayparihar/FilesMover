import os
import time
import argparse
import logging
import datetime
from core_file_mover import start_monitoring, process_all_items

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='File Mover - Move files from source to destination directory',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-s', '--source',
        help='Source directory path',
        required=False,
        default=os.path.join(os.path.expanduser('~'), 'Desktop', 'Source')
    )
    
    parser.add_argument(
        '-d', '--destination',
        help='Destination directory path',
        required=False,
        default=os.path.join(os.path.expanduser('~'), 'Desktop', 'Dest')
    )
    
    parser.add_argument(
        '-o', '--one-time',
        help='Process existing files once and exit',
        action='store_true'
    )
    
    parser.add_argument(
        '--verbose',
        help='Enable verbose logging',
        action='store_true'
    )
    
    parser.add_argument(
        '-l', '--log-file',
        help='Custom log file path (default uses timestamp)',
        default=None
    )
    
    return parser.parse_args()

def main():
    """Main CLI function"""
    args = parse_arguments()
    
    # Configure logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    source = os.path.abspath(args.source)
    destination = os.path.abspath(args.destination)
    
    print(f"Source directory: {source}")
    print(f"Destination directory: {destination}")
    
    # Ensure application logs directory exists
    logs_dir = os.path.join(os.path.expanduser('~'), '.file_mover', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Set custom log file if specified
    if args.log_file:
        # Configure a file handler for custom log file
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S'))
        logging.getLogger().addHandler(file_handler)
        print(f"Logging to custom file: {args.log_file}")
    
    # Ensure source and destination directories exist
    if not os.path.exists(source):
        print(f"Error: Source directory does not exist: {source}")
        return 1
    
    if not os.path.exists(destination):
        try:
            os.makedirs(destination)
            print(f"Created destination directory: {destination}")
        except Exception as e:
            print(f"Error creating destination directory: {e}")
            return 1
    
    if args.one_time:
        # One-time processing of all files
        print("Processing all files in the source directory...")
        count = process_all_items(source, destination)
        print(f"Processed {count} items")
        return 0
    
    # Start continuous monitoring
    print("Starting continuous monitoring. Press Ctrl+C to stop.")
    observer, handler = start_monitoring(source, destination)
    
    if not observer:
        print("Failed to start monitoring")
        return 1
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the observer gracefully on keyboard interrupt
        observer.stop()
        print("\nFile monitoring stopped.")
    
    # Wait for the observer to complete
    observer.join()
    return 0

if __name__ == "__main__":
    exit(main()) 