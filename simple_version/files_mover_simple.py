#!/usr/bin/env python3
"""
FilesMover Simple - File organization and moving utility

A simplified version of FilesMover that uses only Python standard libraries.
This script monitors a source directory and moves files to a destination directory.

Usage:
    python files_mover_simple.py [-s SOURCE] [-d DESTINATION] [options]

Example:
    python files_mover_simple.py -s ~/Downloads -d ~/Documents/Organized
"""

import os
import shutil
import time
import argparse
import logging
import datetime
import threading
import signal
import sys
from typing import Dict, Any, Set

# Configure logging
def setup_logging(verbose=False):
    """Configure logging with appropriate level and output."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_dir = os.path.join(os.path.expanduser('~'), '.file_mover', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"file_mover_{current_time}.log")
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

class FileProcessor:
    """Processes and moves files between directories."""
    
    def __init__(self, source, destination, conflict_mode="rename", 
                 preserve_timestamps=True, recursive=True):
        """
        Initialize the file processor.
        
        Args:
            source: Source directory path
            destination: Destination directory path
            conflict_mode: How to handle file conflicts ('rename', 'overwrite', 'skip')
            preserve_timestamps: Whether to preserve file creation/modification times
            recursive: Whether to process subdirectories recursively
        """
        self.source = os.path.abspath(os.path.expanduser(source))
        self.destination = os.path.abspath(os.path.expanduser(destination))
        self.conflict_mode = conflict_mode
        self.preserve_timestamps = preserve_timestamps
        self.recursive = recursive
        
        # Create directories if they don't exist
        os.makedirs(self.source, exist_ok=True)
        os.makedirs(self.destination, exist_ok=True)
        
        logging.info(f"Source directory: {self.source}")
        logging.info(f"Destination directory: {self.destination}")
    
    def process_file(self, src_path):
        """
        Process a single file by moving it to the destination.
        
        Args:
            src_path: Path to the source file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.isfile(src_path):
            logging.warning(f"Not a file: {src_path}")
            return False
            
        rel_path = os.path.relpath(src_path, self.source)
        dest_path = os.path.join(self.destination, rel_path)
        dest_dir = os.path.dirname(dest_path)
        
        # Create destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)
        
        # Handle file conflicts
        if os.path.exists(dest_path):
            if self.conflict_mode == "skip":
                logging.info(f"Skipping existing file: {dest_path}")
                return True
            elif self.conflict_mode == "overwrite":
                logging.info(f"Overwriting existing file: {dest_path}")
            elif self.conflict_mode == "rename":
                base, ext = os.path.splitext(dest_path)
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = f"{base}_{counter}{ext}"
                    counter += 1
                logging.info(f"Renamed to avoid conflict: {dest_path}")
        
        try:
            # Copy file with metadata
            shutil.copy2(src_path, dest_path) if self.preserve_timestamps else shutil.copy(src_path, dest_path)
            logging.info(f"Moved: {src_path} -> {dest_path}")
            
            # Remove the original file
            os.remove(src_path)
            return True
        except Exception as e:
            logging.error(f"Error processing {src_path}: {str(e)}")
            return False
    
    def process_all(self):
        """Process all files in the source directory."""
        processed_count = 0
        error_count = 0
        
        for root, dirs, files in os.walk(self.source):
            # Skip processing if not recursive and we're in a subdirectory
            if not self.recursive and root != self.source:
                continue
                
            for filename in files:
                src_path = os.path.join(root, filename)
                success = self.process_file(src_path)
                if success:
                    processed_count += 1
                else:
                    error_count += 1
        
        logging.info(f"Processing complete. {processed_count} files processed, {error_count} errors.")
        return processed_count, error_count

class DirectoryMonitor:
    """Monitors a directory for changes and processes new or modified files."""
    
    def __init__(self, processor, poll_interval=1.0, min_age=0.5):
        """
        Initialize the directory monitor.
        
        Args:
            processor: FileProcessor instance to handle file operations
            poll_interval: Time in seconds between directory scans
            min_age: Minimum time in seconds a file must be unchanged before processing
        """
        self.processor = processor
        self.poll_interval = poll_interval
        self.min_age = min_age
        self.running = False
        self._snapshot = {}
        self._pending_files = {}
        self._monitor_thread = None
    
    def start(self):
        """Start monitoring the directory."""
        if self.running:
            logging.warning("Monitoring is already running")
            return False
        
        try:
            # Take initial snapshot
            self._snapshot = self._take_snapshot(self.processor.source)
            self.running = True
            self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
            self._monitor_thread.start()
            logging.info(f"Started monitoring {self.processor.source}")
            return True
        except Exception as e:
            logging.error(f"Error starting monitoring: {str(e)}")
            return False
    
    def stop(self):
        """Stop monitoring the directory."""
        if not self.running:
            return
            
        self.running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        logging.info("Stopped monitoring")
    
    def _take_snapshot(self, directory):
        """
        Take a snapshot of the directory contents.
        
        Args:
            directory: Directory path to scan
            
        Returns:
            dict: Dictionary mapping filenames to metadata
        """
        snapshot = {}
        for root, _, files in os.walk(directory):
            # Skip subdirectories if not recursive
            if not self.processor.recursive and root != directory:
                continue
                
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    stat = os.stat(filepath)
                    snapshot[filepath] = {
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'last_checked': time.time()
                    }
                except OSError:
                    # File might have been deleted or permission issues
                    pass
        return snapshot
    
    def _file_is_stable(self, filepath, metadata, now):
        """
        Check if a file is stable (not being modified).
        
        Args:
            filepath: Path to the file
            metadata: Current file metadata
            now: Current timestamp
            
        Returns:
            bool: True if the file is stable, False otherwise
        """
        if filepath not in self._pending_files:
            # File is new, add to pending
            self._pending_files[filepath] = metadata
            return False
        
        previous = self._pending_files[filepath]
        
        # If file size or modification time has changed, update and wait
        if metadata['size'] != previous['size'] or metadata['mtime'] != previous['mtime']:
            self._pending_files[filepath] = metadata
            return False
        
        # Check if file has been stable for min_age seconds
        if now - previous['last_checked'] >= self.min_age:
            return True
            
        return False
    
    def _monitor(self):
        """Monitor the directory for changes."""
        while self.running:
            try:
                # Take a new snapshot
                current = self._take_snapshot(self.processor.source)
                now = time.time()
                
                # Process files
                for filepath, metadata in current.items():
                    # Skip files that are in the initial snapshot (existing files)
                    if filepath in self._snapshot:
                        continue
                    
                    # Process files that are stable
                    if self._file_is_stable(filepath, metadata, now):
                        self.processor.process_file(filepath)
                        del self._pending_files[filepath]
                
                # Update snapshot with current state
                self._snapshot = current
                
                # Clean up pending files that no longer exist
                self._pending_files = {f: m for f, m in self._pending_files.items() if f in current}
                
                # Sleep before next poll
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logging.error(f"Error in monitoring thread: {str(e)}")
                time.sleep(self.poll_interval)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='FilesMover Simple - Organize and move files between directories',
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
        '-c', '--conflict',
        choices=['rename', 'overwrite', 'skip'],
        default='rename',
        help='How to handle file conflicts'
    )
    
    parser.add_argument(
        '-p', '--preserve-timestamps',
        action='store_true',
        default=True,
        help='Preserve file creation/modification times'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        default=True,
        help='Process subdirectories recursively'
    )
    
    parser.add_argument(
        '-i', '--interval',
        type=float,
        default=1.0,
        help='Poll interval in seconds'
    )
    
    parser.add_argument(
        '-a', '--min-age',
        type=float,
        default=0.5,
        help='Minimum file age in seconds before processing'
    )
    
    parser.add_argument(
        '-o', '--one-time',
        action='store_true',
        help='Process existing files once and exit'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

def main():
    """Main entry point function."""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Create processor and monitor
    processor = FileProcessor(
        source=args.source,
        destination=args.destination,
        conflict_mode=args.conflict,
        preserve_timestamps=args.preserve_timestamps,
        recursive=args.recursive
    )
    
    # For one-time processing
    if args.one_time:
        processor.process_all()
        return 0
    
    # For continuous monitoring
    monitor = DirectoryMonitor(
        processor=processor,
        poll_interval=args.interval,
        min_age=args.min_age
    )
    
    # Set up signal handler for clean shutdown
    def signal_handler(sig, frame):
        print("\nShutting down...")
        monitor.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        if monitor.start():
            print("Monitoring started. Press Ctrl+C to stop.")
            # Keep main thread alive
            while True:
                time.sleep(1)
        else:
            return 1
    except KeyboardInterrupt:
        monitor.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 