"""
Core file processing functionality for the FilesMover utility.

This module provides the core file processing capabilities for moving and organizing files.
It includes classes for handling file system monitoring, processing files, and monitoring directories.

Classes:
    DirectoryMonitor: Monitors directories for file changes
    FileProcessor: Processes and moves files between directories

Functions:
    start_monitoring: Convenience function to start monitoring a directory
"""

import os
import shutil
import time
import logging
import datetime
import threading

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

class DirectoryMonitor:
    """
    Monitors a directory for changes and processes new or modified files.
    
    This class provides functionality to watch a directory for file system changes
    without using external libraries. It uses a polling approach with 
    file metadata comparison to detect changes.
    
    Attributes:
        processor (FileProcessor): The processor used to handle file operations
        poll_interval (float): Time in seconds between directory scans
        running (bool): Flag indicating if monitoring is active
        _snapshot (dict): Dictionary storing file metadata for change detection
    """
    
    def __init__(self, processor, poll_interval=1.0):
        """
        Initialize the directory monitor with a file processor.
        
        Args:
            processor (FileProcessor): Instance to handle file operations
            poll_interval (float): Time in seconds between directory scans
        """
        self.processor = processor
        self.poll_interval = poll_interval
        self.running = False
        self._snapshot = {}
        self._monitor_thread = None
    
    def start(self):
        """
        Start monitoring the directory.
        
        Returns:
            bool: True if monitoring started successfully, False otherwise
        """
        if self.running:
            logging.warning("Monitoring is already running")
            return False
        
        try:
            # Take initial snapshot
            self._snapshot = self._take_snapshot(self.processor.source)
            
            # Process any existing files first if configured
            if self.processor.process_existing:
                self.processor.process_all()
            
            # Start monitoring thread
            self.running = True
            self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
            self._monitor_thread.start()
            logging.info(f"Started monitoring directory: {self.processor.source}")
            return True
        except Exception as e:
            logging.error(f"Failed to start monitoring: {e}")
            self.running = False
            return False
    
    def stop(self):
        """
        Stop monitoring the directory.
        
        Returns:
            bool: True if monitoring stopped successfully, False otherwise
        """
        if not self.running:
            logging.warning("Monitoring is not running")
            return False
        
        self.running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=3.0)
        logging.info("Stopped monitoring directory")
        return True
    
    def _take_snapshot(self, directory):
        """
        Take a snapshot of the directory contents.
        
        Args:
            directory (str): Path to the directory to scan
            
        Returns:
            dict: Dictionary mapping file paths to their metadata
        """
        snapshot = {}
        try:
            for root, dirs, files in os.walk(directory) if self.processor.recursive else [(directory, [], [f.name for f in os.scandir(directory) if f.is_file()])]:
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        stat = os.stat(filepath)
                        # Store mtime and size for change detection
                        snapshot[filepath] = {
                            'mtime': stat.st_mtime,
                            'size': stat.st_size
                        }
                    except (FileNotFoundError, PermissionError):
                        # Skip files that can't be accessed
                        pass
        except Exception as e:
            logging.error(f"Error taking directory snapshot: {e}")
        
        return snapshot
    
    def _monitor(self):
        """
        Monitor the directory for changes.
        
        This method runs in a separate thread and periodically compares
        directory snapshots to detect changes.
        """
        while self.running:
            try:
                new_snapshot = self._take_snapshot(self.processor.source)
                
                # Find new or modified files
                for filepath, metadata in new_snapshot.items():
                    # File is new
                    if filepath not in self._snapshot:
                        logging.debug(f"New file detected: {filepath}")
                        if not os.path.isdir(filepath):
                            self.processor.process_file(filepath)
                        else:
                            self.processor.process_directory(filepath)
                    # File is modified (mtime or size changed)
                    elif (metadata['mtime'] > self._snapshot[filepath]['mtime'] or 
                          metadata['size'] != self._snapshot[filepath]['size']):
                        logging.debug(f"Modified file detected: {filepath}")
                        if not os.path.isdir(filepath):
                            self.processor.process_file(filepath)
                
                # Update snapshot
                self._snapshot = new_snapshot
                
                # Sleep until next poll
                time.sleep(self.poll_interval)
            except Exception as e:
                logging.error(f"Error during directory monitoring: {e}")
                time.sleep(self.poll_interval)  # Sleep and try again

class FileProcessor:
    """
    Processes and moves files between directories.
    
    This class provides functionality to process files according to
    predefined rules and move them to appropriate destinations.
    
    Attributes:
        source (str): Source directory path
        destination (str): Destination directory path
        activity_tracking (bool): Whether to track file activity
        conflict_mode (str): How to handle file conflicts
        preserve_timestamps (bool): Whether to preserve file timestamps
        confirm_operations (bool): Whether to confirm destructive operations
        recursive (bool): Whether to process subdirectories
        processing_delay (float): Delay in seconds before processing files
        process_existing (bool): Whether to process existing files on startup
    """
    
    def __init__(self, source, destination, activity_tracking=False, 
                 conflict_mode="rename", preserve_timestamps=True, 
                 confirm_operations=False, recursive=True, 
                 processing_delay=0.0, process_existing=True):
        """
        Initialize the file processor with the given parameters.
        
        Args:
            source (str): Source directory path
            destination (str): Destination directory path
            activity_tracking (bool, optional): Whether to track file activity
            conflict_mode (str, optional): How to handle file conflicts
            preserve_timestamps (bool, optional): Whether to preserve file timestamps
            confirm_operations (bool, optional): Whether to confirm destructive operations
            recursive (bool, optional): Whether to process subdirectories
            processing_delay (float, optional): Delay in seconds before processing files
            process_existing (bool, optional): Whether to process existing files on startup
        """
        self.source = os.path.abspath(source)
        self.destination = os.path.abspath(destination)
        self.activity_tracking = activity_tracking
        self.conflict_mode = conflict_mode
        self.preserve_timestamps = preserve_timestamps
        self.confirm_operations = confirm_operations
        self.recursive = recursive
        self.processing_delay = processing_delay
        self.process_existing = process_existing
        
        # Create destination if it doesn't exist
        os.makedirs(self.destination, exist_ok=True)
        
        # Validate paths
        if not os.path.isdir(self.source):
            raise ValueError(f"Source directory does not exist: {self.source}")
        if not os.path.isdir(self.destination):
            raise ValueError(f"Destination directory could not be created: {self.destination}")
    
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
        
        # Handle file conflicts
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
                logging.info(f"Renamed due to conflict: {os.path.basename(src_path)} → {os.path.basename(dest_path)}")
            # For "replace" mode, we'll just overwrite
        
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
                   conflict_mode="rename", preserve_timestamps=True, 
                   confirm_operations=False, recursive=True,
                   processing_delay=0.0, poll_interval=1.0,
                   process_existing=True):
    """
    Start monitoring a directory for changes.
    
    This is a convenience function to create a FileProcessor and DirectoryMonitor
    instance and start monitoring in one step.
    
    Args:
        source (str): Source directory path
        destination (str): Destination directory path
        activity_tracking (bool, optional): Whether to track file activity
        conflict_mode (str, optional): How to handle file conflicts
        preserve_timestamps (bool, optional): Whether to preserve file timestamps
        confirm_operations (bool, optional): Whether to confirm destructive operations
        recursive (bool, optional): Whether to process subdirectories
        processing_delay (float, optional): Delay in seconds before processing files
        poll_interval (float, optional): Time in seconds between directory scans
        process_existing (bool, optional): Whether to process existing files on startup
        
    Returns:
        tuple: (DirectoryMonitor instance, FileProcessor instance) if successful,
               None if there was an error
    """
    try:
        processor = FileProcessor(
            source=source,
            destination=destination,
            activity_tracking=activity_tracking,
            conflict_mode=conflict_mode,
            preserve_timestamps=preserve_timestamps,
            confirm_operations=confirm_operations,
            recursive=recursive,
            processing_delay=processing_delay,
            process_existing=process_existing
        )
        
        monitor = DirectoryMonitor(
            processor=processor,
            poll_interval=poll_interval
        )
        
        if monitor.start():
            return monitor, processor
        else:
            return None
    except Exception as e:
        logging.error(f"Error starting monitoring: {e}")
        return None 