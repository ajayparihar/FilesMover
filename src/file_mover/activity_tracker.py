"""
Activity tracking and file organization based on access patterns.

This module provides functionality to track file activity and organize files
based on how frequently they are accessed. Files that haven't been accessed
for a specified period can be automatically moved to an "inactive" folder,
and will be restored when accessed again.

Classes:
    FileActivityEventHandler: Event handler for tracking file activity events
    FileActivityTracker: Main class for tracking file activity and organizing files
"""

import os
import time
import logging
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Default configuration values
DEFAULT_INACTIVE_FOLDER = "_inactive_files"
DEFAULT_INACTIVITY_THRESHOLD = 7 * 24 * 60 * 60  # 7 days in seconds
DEFAULT_CHECK_INTERVAL = 3600  # 1 hour in seconds
DEFAULT_IGNORED_DIRS = ["_inactive_files", ".git", "__pycache__", ".venv"]
DEFAULT_IGNORED_FILES = [".gitignore", ".DS_Store", "desktop.ini", "Thumbs.db"]

class FileActivityEventHandler(FileSystemEventHandler):
    """
    Event handler for file system events to track file activity.
    
    This class extends watchdog's FileSystemEventHandler to detect and record
    file access events, and to restore inactive files when they are accessed.
    
    Attributes:
        tracker (FileActivityTracker): The activity tracker instance
    """
    
    def __init__(self, tracker):
        """
        Initialize the file activity event handler.
        
        Args:
            tracker (FileActivityTracker): The activity tracker that will process events
        """
        self.tracker = tracker
        
    def on_any_event(self, event):
        """
        Handle any file system event by updating file activity.
        
        This method is called for any file system event (create, modify, delete, move).
        It updates the activity timestamp for the file and restores files from
        the inactive folder if they are accessed.
        
        Args:
            event (FileSystemEvent): The file system event object
        """
        # Skip directory events and events in ignored directories
        if event.is_directory:
            return
            
        # Get the path and check if it should be ignored
        filepath = event.src_path
        rel_path = os.path.relpath(filepath, self.tracker.root_dir)
        
        # Skip files in ignored directories or with ignored names
        if any(ignored in rel_path.split(os.sep) for ignored in self.tracker.ignored_dirs):
            return
            
        filename = os.path.basename(filepath)
        if filename in self.tracker.ignored_files:
            return
            
        # Update activity data for the file
        self.tracker._update_file_activity(filepath)
        
        # If the file is in the inactive folder, move it back to root
        if os.path.commonpath([filepath, self.tracker.inactive_path]) == self.tracker.inactive_path:
            rel_path_in_inactive = os.path.relpath(filepath, self.tracker.inactive_path)
            self.tracker._move_to_root(filepath, rel_path_in_inactive)

class FileActivityTracker:
    """
    Tracks file activity and moves files based on interaction patterns.
    
    This class monitors file access patterns and organizes files based on activity:
    - Files that haven't been accessed for a specified period are moved to an inactive folder
    - When an inactive file is accessed, it's moved back to its original location
    
    Attributes:
        root_dir (str): Root directory to monitor
        inactive_folder (str): Name of the folder for inactive files
        inactive_path (str): Full path to the inactive folder
        inactivity_threshold (int): Time threshold in seconds for inactivity
        check_interval (int): Interval in seconds to check for inactive files
        ignored_dirs (list): List of directory names to ignore
        ignored_files (list): List of file names to ignore
        activity_data (dict): Dictionary mapping filepaths to last activity timestamps
        observer (Observer): File system observer for monitoring changes
        event_handler (FileActivityEventHandler): Handler for file system events
        check_thread (Thread): Thread for periodically checking inactive files
        running (bool): Flag indicating whether the tracker is running
    """
    def __init__(self, 
                 root_dir, 
                 inactive_folder=DEFAULT_INACTIVE_FOLDER,
                 inactivity_threshold=DEFAULT_INACTIVITY_THRESHOLD,
                 check_interval=DEFAULT_CHECK_INTERVAL,
                 ignored_dirs=None,
                 ignored_files=None):
        """
        Initialize the file activity tracker.
        
        Args:
            root_dir (str): Root directory to monitor
            inactive_folder (str): Name of the folder for inactive files (default: "_inactive_files")
            inactivity_threshold (int): Time threshold in seconds for inactivity (default: 7 days)
            check_interval (int): Interval in seconds to check for inactive files (default: 1 hour)
            ignored_dirs (list): List of directory names to ignore (default: [])
            ignored_files (list): List of file names to ignore (default: [])
        """
        self.root_dir = os.path.abspath(root_dir)
        self.inactive_folder = inactive_folder
        self.inactive_path = os.path.join(self.root_dir, inactive_folder)
        self.inactivity_threshold = inactivity_threshold
        self.check_interval = check_interval
        
        # Set ignored directories and files
        self.ignored_dirs = ignored_dirs or DEFAULT_IGNORED_DIRS
        self.ignored_files = ignored_files or DEFAULT_IGNORED_FILES
        
        # Ensure the inactive folder is in the ignored directories
        if self.inactive_folder not in self.ignored_dirs:
            self.ignored_dirs.append(self.inactive_folder)
        
        # Create the inactive folder if it doesn't exist
        if not os.path.exists(self.inactive_path):
            os.makedirs(self.inactive_path, exist_ok=True)
        
        # Dictionary to store file activity: {filepath: last_activity_time}
        self.activity_data = {}
        
        # Setup observer and event handler
        self.observer = None
        self.event_handler = None
        
        # Thread for checking inactive files
        self.check_thread = None
        self.running = False
        
        # Initialize activity data from existing files
        self._initialize_activity_data()
        
    def start(self):
        """
        Start monitoring file activity and checking for inactive files.
        
        This method initializes and starts the file system observer to monitor file access,
        and starts a background thread to periodically check for inactive files.
        """
        # Start the observer for file system events
        self.event_handler = FileActivityEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.root_dir, recursive=True)
        self.observer.start()
        
        # Start the thread for checking inactive files
        self.running = True
        self.check_thread = threading.Thread(target=self._schedule_inactivity_check)
        self.check_thread.daemon = True
        self.check_thread.start()
        
        logging.info(f"Started file activity tracking in {self.root_dir}")
    
    def stop(self):
        """
        Stop monitoring file activity.
        
        This method stops the file system observer and the background thread
        for checking inactive files.
        """
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
        if self.check_thread and self.check_thread.is_alive():
            self.check_thread.join(timeout=1.0)
            
        logging.info("Stopped file activity tracking")
    
    def _initialize_activity_data(self):
        """
        Initialize activity data from existing files.
        
        This method scans the root directory and initializes the activity timestamp
        for each file to the current time.
        """
        current_time = time.time()
        
        # Walk through the root directory
        for root, dirs, files in os.walk(self.root_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            # Add files to activity data
            for file in files:
                if file not in self.ignored_files:
                    filepath = os.path.join(root, file)
                    self.activity_data[filepath] = current_time
    
    def _update_file_activity(self, filepath):
        """
        Update the last activity time for a file.
        
        Args:
            filepath (str): Path to the file being accessed
        """
        self.activity_data[filepath] = time.time()
        logging.debug(f"Updated activity for {filepath}")
    
    def _schedule_inactivity_check(self):
        """
        Schedule periodic checks for inactive files.
        
        This method runs in a separate thread and periodically checks
        for inactive files that should be moved.
        """
        while self.running:
            self._check_inactive_files()
            time.sleep(self.check_interval)
    
    def _check_inactive_files(self):
        """
        Check for inactive files and move them accordingly.
        
        This method checks both the root directory for files that have become inactive,
        and the inactive directory for files that have been accessed recently.
        """
        current_time = time.time()
        
        # Check files in the root directory
        self._check_root_files(current_time)
        
        # Check files in the inactive directory
        self._check_inactive_files_for_activity(current_time)
    
    def _check_root_files(self, current_time):
        """
        Check files in the root directory and move inactive ones.
        
        This method identifies files in the root directory that haven't been
        accessed for the specified inactivity threshold and moves them to
        the inactive folder.
        
        Args:
            current_time (float): Current timestamp for comparison
        """
        inactive_files = []
        
        # Find inactive files
        for filepath, last_activity in list(self.activity_data.items()):
            # Skip files not in root directory or already in inactive folder
            if not os.path.exists(filepath):
                continue
                
            if os.path.commonpath([filepath, self.inactive_path]) == self.inactive_path:
                continue
            
            # Check if file is inactive
            if current_time - last_activity > self.inactivity_threshold:
                inactive_files.append(filepath)
        
        # Move inactive files
        for filepath in inactive_files:
            self._move_to_inactive(filepath)
    
    def _check_inactive_files_for_activity(self, current_time):
        """
        Check if any inactive files have been recently accessed.
        
        This method identifies files in the inactive folder that have been
        accessed recently and restores them to their original locations.
        
        Args:
            current_time (float): Current timestamp for comparison
        """
        to_restore = []
        
        # Find files to restore
        for filepath, last_activity in list(self.activity_data.items()):
            if not os.path.exists(filepath):
                continue
                
            # Skip files not in inactive folder
            if os.path.commonpath([filepath, self.inactive_path]) != self.inactive_path:
                continue
            
            # If recently active, move back to root
            if current_time - last_activity < self.inactivity_threshold:
                rel_path = os.path.relpath(filepath, self.inactive_path)
                to_restore.append((filepath, rel_path))
        
        # Restore active files
        for filepath, rel_path in to_restore:
            self._move_to_root(filepath, rel_path)
    
    def _move_to_inactive(self, filepath):
        """
        Move a file to the inactive folder.
        
        This method moves a file from its current location to the same relative
        path within the inactive folder.
        
        Args:
            filepath (str): Path to the file to be moved
        """
        try:
            # Calculate the relative path from the root directory
            rel_path = os.path.relpath(filepath, self.root_dir)
            dest_path = os.path.join(self.inactive_path, rel_path)
            
            # Create the destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Move the file
            os.rename(filepath, dest_path)
            
            # Update activity data
            del self.activity_data[filepath]
            self.activity_data[dest_path] = time.time()
            
            logging.info(f"Moved inactive file to inactive folder: {rel_path}")
        except (OSError, PermissionError) as e:
            logging.error(f"Error moving file to inactive folder: {e}")
    
    def _move_to_root(self, filepath, rel_path_in_inactive):
        """
        Move a file back to the root directory.
        
        This method restores a file from the inactive folder to its original
        location in the root directory structure.
        
        Args:
            filepath (str): Path to the file in the inactive folder
            rel_path_in_inactive (str): Relative path within the inactive folder
        """
        try:
            # Calculate the destination path
            dest_path = os.path.join(self.root_dir, rel_path_in_inactive)
            
            # Create the destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Move the file
            os.rename(filepath, dest_path)
            
            # Update activity data
            del self.activity_data[filepath]
            self.activity_data[dest_path] = time.time()
            
            logging.info(f"Restored active file to root: {rel_path_in_inactive}")
        except (OSError, PermissionError) as e:
            logging.error(f"Error moving file to root: {e}") 