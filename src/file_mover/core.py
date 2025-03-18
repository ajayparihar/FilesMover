"""
Core file processing functionality.

This module provides the core file processing capabilities for moving and organizing files.
"""

import os
import shutil
import time
import logging
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .activity_tracker import FileActivityTracker

# Setup log directory
LOG_DIR = os.path.join(os.path.expanduser('~'), '.file_mover', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Generate log filename with timestamp
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"file_mover_{current_time}.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class FileEventHandler(FileSystemEventHandler):
    """Handler for file system events (creation or modification)."""
    
    def __init__(self, processor):
        """
        Initialize the event handler with a file processor.
        
        Args:
            processor: FileProcessor instance to handle file operations
        """
        self.processor = processor
        
    def on_created(self, event):
        self._process_event(event)
        
    def on_modified(self, event):
        self._process_event(event)
        
    def _process_event(self, event):
        """Process file system events."""
        if event.is_directory:
            return
        
        src_path = event.src_path
        self.processor.process_file(src_path)


class FileProcessor:
    """Processes and moves files between directories."""
    
    def __init__(self, source, destination, activity_tracking=False, 
                 inactive_folder="_inactive_files", inactivity_threshold=7*24*60*60):
        """
        Initialize the file processor.
        
        Args:
            source: Source directory path
            destination: Destination directory path
            activity_tracking: Whether to enable activity tracking
            inactive_folder: Name of the folder for inactive files
            inactivity_threshold: Time threshold in seconds for inactivity
        """
        self.source = os.path.abspath(source)
        self.destination = os.path.abspath(destination)
        self.activity_tracking = activity_tracking
        self.activity_tracker = None
        
        # Initialize observer and handler
        self.observer = None
        self.event_handler = None
        
        # Initialize activity tracker if enabled
        if activity_tracking:
            self.activity_tracker = FileActivityTracker(
                root_dir=source,
                inactive_folder=inactive_folder,
                inactivity_threshold=inactivity_threshold
            )
    
    def process_file(self, src_path):
        """
        Process a single file by moving it to the destination.
        
        Args:
            src_path: Path to the source file
        """
        # Calculate the relative path from the source directory
        rel_path = os.path.relpath(src_path, self.source)
        dest_path = os.path.join(self.destination, rel_path)
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        try:
            # Move the file
            shutil.move(src_path, dest_path)
            logging.info(f"Moved: {rel_path} to {dest_path}")
        except (shutil.Error, PermissionError, OSError) as e:
            logging.error(f"Error moving {rel_path}: {e}")
    
    def process_all(self):
        """Process all files in the source directory."""
        file_count = 0
        
        for root, _, files in os.walk(self.source):
            for file in files:
                src_path = os.path.join(root, file)
                self.process_file(src_path)
                file_count += 1
                
        return file_count
    
    def start_monitoring(self):
        """Start monitoring the source directory for changes."""
        self.event_handler = FileEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.source, recursive=True)
        self.observer.start()
        
        # Start activity tracker if enabled
        if self.activity_tracking and self.activity_tracker:
            self.activity_tracker.start()
            
        logging.info(f"Started monitoring {self.source}")
    
    def stop_monitoring(self):
        """Stop monitoring the source directory."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
        if self.activity_tracking and self.activity_tracker:
            self.activity_tracker.stop()
            
        logging.info(f"Stopped monitoring {self.source}")


def start_monitoring(source, destination, activity_tracking=False, 
                    inactive_folder="_inactive_files", inactivity_threshold=7*24*60*60):
    """
    Start monitoring a directory for changes.
    
    Args:
        source: Source directory path
        destination: Destination directory path
        activity_tracking: Whether to enable activity tracking
        inactive_folder: Name of the folder for inactive files
        inactivity_threshold: Time threshold in seconds for inactivity
        
    Returns:
        FileProcessor: The processor instance
    """
    processor = FileProcessor(
        source=source,
        destination=destination,
        activity_tracking=activity_tracking,
        inactive_folder=inactive_folder,
        inactivity_threshold=inactivity_threshold
    )
    
    processor.start_monitoring()
    return processor 