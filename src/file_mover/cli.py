"""
Command-line interface for the FilesMover utility.

This module provides a CLI interface to use the file mover functionality,
allowing users to monitor directories, process files, and configure options
through command-line arguments.

Functions:
    parse_arguments: Parse command line arguments
    setup_logging: Configure logging with appropriate level and output
    handle_keyboard_interrupt: Set up signal handler for clean shutdown
    main: Main CLI entry point function
"""

import os
import time
import argparse
import logging
import datetime
import signal
import sys
from .core import FileProcessor, DirectoryMonitor, start_monitoring

def parse_arguments():
    """
    Parse command line arguments.
    
    This function defines and parses the command-line arguments for the FilesMover
    utility, including source and destination directories, processing options,
    and logging configuration.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='FilesMover - Organize and move files between directories',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-s', '--source',
        help='Source directory path',
        default=os.path.join(os.path.expanduser('~'), 'Desktop', 'Source')
    )
    
    parser.add_argument(
        '-d', '--destination',
        help='Destination directory path',
        default=os.path.join(os.path.expanduser('~'), 'Desktop', 'Dest')
    )
    
    parser.add_argument(
        '-o', '--one-time',
        help='Process existing files once and exit',
        action='store_true'
    )
    
    # File handling options
    parser.add_argument(
        '-c', '--conflict-mode',
        help='How to handle file conflicts',
        choices=['replace', 'skip', 'rename'],
        default='replace'
    )
    
    parser.add_argument(
        '-p', '--preserve-timestamps',
        help='Preserve file timestamps when moving',
        action='store_true',
        default=True
    )
    
    parser.add_argument(
        '--no-preserve-timestamps',
        help='Do not preserve file timestamps when moving',
        dest='preserve_timestamps',
        action='store_false'
    )
    
    parser.add_argument(
        '--confirm-operations',
        help='Confirm before replacing or deleting files',
        action='store_true',
        default=True
    )
    
    parser.add_argument(
        '--no-confirm-operations',
        help='Do not confirm before replacing or deleting files',
        dest='confirm_operations',
        action='store_false'
    )
    
    # Performance options
    parser.add_argument(
        '-r', '--recursive',
        help='Monitor subdirectories recursively',
        action='store_true'
    )
    
    parser.add_argument(
        '--processing-delay',
        help='Delay in seconds before processing new files',
        type=float,
        default=0.5
    )
    
    parser.add_argument(
        '--poll-interval',
        help='Interval in seconds between directory scans',
        type=float,
        default=1.0
    )
    
    # Logging options
    parser.add_argument(
        '--verbose',
        help='Enable verbose logging',
        action='store_true'
    )
    
    parser.add_argument(
        '-l', '--log-file',
        help='Log file path',
        default=None
    )
    
    return parser.parse_args()

def setup_logging(verbose, log_file=None):
    """
    Configure logging with appropriate level and output.
    
    This function sets up the logging system with file and console handlers,
    creating the log directory if necessary and generating a timestamped
    log filename if one is not provided.
    
    Args:
        verbose (bool): Whether to enable verbose (DEBUG) logging
        log_file (str, optional): Custom log file path. If None, a timestamped
                                 filename will be generated.
    
    Returns:
        str: Path to the log file
    """
    # Setup log directory
    log_dir = os.path.join(os.path.expanduser('~'), '.file_mover', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log filename with timestamp
    if log_file is None:
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"file_mover_{current_time}.log")
    
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"Logging to {log_file}")
    return log_file

def handle_keyboard_interrupt(monitor, processor):
    """
    Set up signal handler for clean shutdown.
    
    This function registers a signal handler for the SIGINT signal (Ctrl+C)
    to ensure the directory monitor is properly shut down when the user
    interrupts the program.
    
    Args:
        monitor (DirectoryMonitor): The directory monitor instance to shut down
        processor (FileProcessor): The file processor instance
    """
    def signal_handler(sig, frame):
        """
        Signal handler function to handle keyboard interrupts.
        
        Args:
            sig: Signal number
            frame: Current stack frame
        """
        logging.info("Received keyboard interrupt, shutting down...")
        if monitor:
            monitor.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

def main():
    """
    Main CLI function.
    
    This function serves as the entry point for the CLI interface, parsing
    arguments, setting up logging, initializing the file processor, and
    starting file processing according to the specified options.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.verbose, args.log_file)
    
    # Validate directories
    source = os.path.abspath(args.source)
    destination = os.path.abspath(args.destination)
    
    if not os.path.exists(source):
        logging.error(f"Source directory does not exist: {source}")
        try:
            os.makedirs(source)
            logging.info(f"Created source directory: {source}")
        except Exception as e:
            logging.error(f"Error creating source directory: {e}")
            return 1
    
    if not os.path.exists(destination):
        try:
            os.makedirs(destination)
            logging.info(f"Created destination directory: {destination}")
        except Exception as e:
            logging.error(f"Error creating destination directory: {e}")
            return 1
    
    # Create processor
    processor = FileProcessor(
        source=source,
        destination=destination,
        conflict_mode=args.conflict_mode,
        preserve_timestamps=args.preserve_timestamps,
        confirm_operations=args.confirm_operations,
        recursive=args.recursive,
        processing_delay=args.processing_delay,
        process_existing=not args.one_time
    )
    
    if args.one_time:
        # Process all files once
        logging.info(f"Processing all files from {os.path.normpath(source)} to {os.path.normpath(destination)}...")
        file_count = processor.process_all()
        logging.info(f"Processed {file_count} files.")
        return 0
    else:
        # Start monitoring
        logging.info(f"Starting file monitoring from {os.path.normpath(source)} to {os.path.normpath(destination)}...")
        monitor = DirectoryMonitor(processor, poll_interval=args.poll_interval)
        
        # Set up keyboard interrupt handler
        handle_keyboard_interrupt(monitor, processor)
        
        # Start monitoring and enter main loop
        if monitor.start():
            try:
                # Keep the main thread alive
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                monitor.stop()
                logging.info("Monitoring stopped.")
            return 0
        else:
            logging.error("Failed to start monitoring.")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 