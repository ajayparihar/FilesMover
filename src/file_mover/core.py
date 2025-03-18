"""
Core file processing functionality for the FilesMover utility.

This module provides the core file processing capabilities for moving and organizing files.
It includes classes for handling file system events, processing files, and monitoring directories.

Classes:
    FileEventHandler: Handler for file system events (creation or modification)
    FileProcessor: Processes and moves files between directories

Functions:
    start_monitoring: Convenience function to start monitoring a directory
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
    """
    Handler for file system events (creation or modification).
    
    This class extends watchdog's FileSystemEventHandler to process file creation
    and modification events by delegating to a FileProcessor instance.
    
    Attributes:
        processor (FileProcessor): The processor used to handle file operations
    """
    
    def __init__(self, processor):
        """
        Initialize the event handler with a file processor.
        
        Args:
            processor (FileProcessor): Instance to handle file operations
        """
        self.processor = processor
        
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event (FileSystemEvent): The file system event object
        """
        self._process_event(event)
        
    def on_modified(self, event):
        """
        Handle file modification events.
        
        Args:
            event (FileSystemEvent): The file system event object
        """
        self._process_event(event)
        
    def _process_event(self, event):
        """
        Process file system events by delegating to the file processor.
        
        Args:
            event (FileSystemEvent): The file system event object
        """
        # Handle directory and file events differently
        if event.is_directory:
            self.processor.process_directory(event.src_path)
        else:
            self.processor.process_file(event.src_path)


class FileProcessor:
    """
    Processes and moves files between directories.
    
    This class is responsible for moving files from a source directory to a
    destination directory, either in response to file system events or as a
    one-time batch operation. It can also optionally track file activity.
    
    Attributes:
        source (str): Absolute path to the source directory
        destination (str): Absolute path to the destination directory
        activity_tracking (bool): Whether activity tracking is enabled
        activity_tracker (FileActivityTracker): Tracker for file activity
        conflict_mode (str): How to handle file conflicts ("replace", "skip", "rename")
        preserve_timestamps (bool): Whether to preserve file timestamps
        confirm_operations (bool): Whether to confirm destructive operations
        recursive (bool): Whether to monitor subdirectories
        processing_delay (float): Delay in seconds before processing new files
        observer (Observer): File system observer for monitoring changes
        event_handler (FileEventHandler): Handler for file system events
    """
    
    def __init__(self, source, destination, activity_tracking=False, 
                 inactive_folder="_inactive_files", inactivity_threshold=7*24*60*60,
                 conflict_mode="replace", preserve_timestamps=True, 
                 confirm_operations=True, recursive=False, processing_delay=0.5):
        """
        Initialize the file processor.
        
        Args:
            source (str): Source directory path
            destination (str): Destination directory path
            activity_tracking (bool): Whether to enable activity tracking
            inactive_folder (str): Name of the folder for inactive files
            inactivity_threshold (int): Time threshold in seconds for inactivity (default: 7 days)
            conflict_mode (str): How to handle file conflicts ("replace", "skip", "rename")
            preserve_timestamps (bool): Whether to preserve file timestamps
            confirm_operations (bool): Whether to confirm destructive operations
            recursive (bool): Whether to monitor subdirectories
            processing_delay (float): Delay in seconds before processing new files
        """
        self.source = os.path.abspath(source)
        self.destination = os.path.abspath(destination)
        self.activity_tracking = activity_tracking
        self.activity_tracker = None
        
        # New settings
        self.conflict_mode = conflict_mode
        self.preserve_timestamps = preserve_timestamps
        self.confirm_operations = confirm_operations
        self.recursive = recursive
        self.processing_delay = processing_delay
        
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
        
        This method moves a file from the source directory to the corresponding
        location in the destination directory, preserving the relative path.
        
        Args:
            src_path (str): Absolute path to the source file
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if file exists (it might have been processed already by another event)
        if not os.path.exists(src_path) or os.path.isdir(src_path):
            return False
            
        # Apply processing delay if set
        if self.processing_delay > 0:
            time.sleep(self.processing_delay)
            # Check again if file exists after delay
            if not os.path.exists(src_path):
                return False
                
        # Calculate the relative path from the source directory
        rel_path = os.path.relpath(src_path, self.source)
        dest_path = os.path.join(self.destination, rel_path)
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # Handle existing file conflicts
        if os.path.exists(dest_path):
            if self.conflict_mode == "skip":
                logging.info(f"Skipped (already exists): {rel_path}")
                return False
            elif self.conflict_mode == "rename":
                # Find a new name by appending a number
                base_name, ext = os.path.splitext(dest_path)
                counter = 1
                while os.path.exists(f"{base_name}_{counter}{ext}"):
                    counter += 1
                dest_path = f"{base_name}_{counter}{ext}"
            elif self.conflict_mode == "replace":
                # Ask for confirmation if enabled
                if self.confirm_operations:
                    # In CLI mode, log the information
                    logging.warning(f"About to replace existing file: {rel_path}")
                    # In GUI mode, this would be replaced with a dialog
        
        try:
            # Store the source directory and file stats for later
            source_dir = os.path.dirname(src_path)
            
            # Preserve timestamps if enabled
            if self.preserve_timestamps:
                file_stats = os.stat(src_path)
                
            # Move the file
            shutil.move(src_path, dest_path)
            
            # Restore timestamps if enabled
            if self.preserve_timestamps:
                os.utime(dest_path, (file_stats.st_atime, file_stats.st_mtime))
                
            # Log the move operation with a more concise message
            if rel_path == os.path.relpath(dest_path, self.destination):
                logging.info(f"Moved: {rel_path}")
            else:
                logging.info(f"Moved: {rel_path} → {os.path.relpath(dest_path, self.destination)}")
            
            # Check if the source directory is now empty and remove it if it is
            if os.path.exists(source_dir) and len(os.listdir(source_dir)) == 0:
                # Only remove directories under the source root
                if os.path.commonpath([source_dir, self.source]) == self.source and source_dir != self.source:
                    try:
                        os.rmdir(source_dir)
                        logging.info(f"Removed empty directory: {os.path.relpath(source_dir, self.source)}")
                    except OSError as e:
                        logging.warning(f"Could not remove empty directory {os.path.relpath(source_dir, self.source)}: {e}")
            
            return True
        except (shutil.Error, PermissionError, OSError) as e:
            logging.error(f"Error moving {rel_path}: {e}")
            return False
    
    def process_all(self):
        """
        Process all files in the source directory.
        
        This method walks through the source directory and moves all files
        to the destination directory, preserving the directory structure.
        It also removes empty directories in the source afterward.
        
        Returns:
            int: Number of files processed
        """
        file_count = 0
        
        # First, collect all files to process
        files_to_process = []
        for root, _, files in os.walk(self.source, topdown=False):
            for file in files:
                src_path = os.path.join(root, file)
                files_to_process.append(src_path)
        
        # Process each file
        for src_path in files_to_process:
            if self.process_file(src_path):
                file_count += 1
        
        # Now clean up any remaining empty directories
        for root, dirs, files in os.walk(self.source, topdown=False):
            # topdown=False ensures we process deepest directories first
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if len(os.listdir(dir_path)) == 0:
                    try:
                        os.rmdir(dir_path)
                        logging.info(f"Removed empty directory: {os.path.relpath(dir_path, self.source)}")
                    except OSError as e:
                        logging.warning(f"Could not remove empty directory {os.path.relpath(dir_path, self.source)}: {e}")
                
        return file_count
    
    def start_monitoring(self):
        """
        Start monitoring the source directory for changes.
        
        This method sets up and starts a file system observer to watch for
        file creation and modification events in the source directory.
        It also starts the activity tracker if enabled.
        """
        self.event_handler = FileEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.source, recursive=self.recursive)
        self.observer.start()
        
        # Start activity tracker if enabled
        if self.activity_tracking and self.activity_tracker:
            self.activity_tracker.start()
            
        logging.info(f"Started monitoring {os.path.normpath(self.source)} {'(including subdirectories)' if self.recursive else ''}")
    
    def stop_monitoring(self):
        """
        Stop monitoring the source directory.
        
        This method stops the file system observer and activity tracker
        if they are running.
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
        if self.activity_tracking and self.activity_tracker:
            self.activity_tracker.stop()
            
        logging.info(f"Stopped monitoring {os.path.normpath(self.source)}")

    def process_directory(self, src_dir):
        """
        Process a directory by creating the corresponding directory in the destination.
        
        This method creates a directory in the destination that matches the structure
        of the source directory. If the directory already exists in the destination,
        it will be kept as is.
        
        Args:
            src_dir (str): Absolute path to the source directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if directory exists
        if not os.path.exists(src_dir) or not os.path.isdir(src_dir):
            return False
            
        # Calculate the relative path from the source directory
        rel_path = os.path.relpath(src_dir, self.source)
        dest_dir = os.path.join(self.destination, rel_path)
        
        # Create destination directory if it doesn't exist
        try:
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
                logging.info(f"Created directory: {rel_path}")
            return True
        except OSError as e:
            logging.error(f"Error creating directory {rel_path}: {e}")
            return False


def start_monitoring(source, destination, activity_tracking=False, 
                    inactive_folder="_inactive_files", inactivity_threshold=7*24*60*60,
                    conflict_mode="replace", preserve_timestamps=True, 
                    confirm_operations=True, recursive=False, processing_delay=0.5):
    """
    Start monitoring a directory for changes.
    
    This convenience function creates a FileProcessor and starts monitoring
    the specified directory. It provides a simpler interface for common usage.
    
    Args:
        source (str): Source directory path
        destination (str): Destination directory path
        activity_tracking (bool): Whether to enable activity tracking
        inactive_folder (str): Name of the folder for inactive files
        inactivity_threshold (int): Time threshold in seconds for inactivity (default: 7 days)
        conflict_mode (str): How to handle file conflicts ("replace", "skip", "rename")
        preserve_timestamps (bool): Whether to preserve file timestamps
        confirm_operations (bool): Whether to confirm destructive operations
        recursive (bool): Whether to monitor subdirectories
        processing_delay (float): Delay in seconds before processing new files
        
    Returns:
        FileProcessor: The processor instance that was created and started
    """
    processor = FileProcessor(
        source=source,
        destination=destination,
        activity_tracking=activity_tracking,
        inactive_folder=inactive_folder,
        inactivity_threshold=inactivity_threshold,
        conflict_mode=conflict_mode,
        preserve_timestamps=preserve_timestamps,
        confirm_operations=confirm_operations,
        recursive=recursive,
        processing_delay=processing_delay
    )
    
    processor.start_monitoring()
    return processor 