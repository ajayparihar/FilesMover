import os
import time
import logging
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Default configuration
DEFAULT_INACTIVE_FOLDER = "_inactive_files"
DEFAULT_INACTIVITY_THRESHOLD = 7 * 24 * 60 * 60  # 7 days in seconds
DEFAULT_CHECK_INTERVAL = 3600  # 1 hour in seconds
DEFAULT_IGNORED_DIRS = ["_inactive_files", ".git", "__pycache__", ".venv"]
DEFAULT_IGNORED_FILES = [".gitignore", ".DS_Store", "desktop.ini", "Thumbs.db"]

class FileActivityEventHandler(FileSystemEventHandler):
    """
    Event handler for file system events to track file activity.
    """
    def __init__(self, tracker):
        self.tracker = tracker
        
    def on_any_event(self, event):
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
    Files that haven't been accessed for a specified period are moved to the inactive folder.
    Files in the inactive folder that are accessed are moved back to the root.
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
            inactive_folder (str): Folder name for inactive files
            inactivity_threshold (int): Seconds of inactivity before moving files
            check_interval (int): How often to check for inactive files (seconds)
            ignored_dirs (list): Directories to ignore
            ignored_files (list): Files to ignore
        """
        self.root_dir = os.path.abspath(root_dir)
        self.inactive_folder = inactive_folder
        self.inactive_path = os.path.join(self.root_dir, inactive_folder)
        self.inactivity_threshold = inactivity_threshold
        self.check_interval = check_interval
        self.ignored_dirs = ignored_dirs or DEFAULT_IGNORED_DIRS
        self.ignored_files = ignored_files or DEFAULT_IGNORED_FILES
        self.is_running = False
        self.activity_data = {}  # Store file activity data
        self.observer = None
        self.event_handler = None
        self.timer = None
        
        # Create inactive folder if it doesn't exist
        if not os.path.exists(self.inactive_path):
            os.makedirs(self.inactive_path)
            logging.info(f"Created inactive files directory: {self.inactive_path}")
    
    def start(self):
        """Start monitoring file activity"""
        if self.is_running:
            logging.warning("File activity tracker is already running")
            return False
        
        # Set up the event handler for file system events
        self.event_handler = FileActivityEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.root_dir, recursive=True)
        
        # Start the watchdog observer
        self.observer.start()
        self.is_running = True
        logging.info(f"Started monitoring file activity in {self.root_dir}")
        
        # Initialize activity data for existing files
        self._initialize_activity_data()
        
        # Start periodic check for inactive files
        self._schedule_inactivity_check()
        
        return True
    
    def stop(self):
        """Stop monitoring file activity"""
        if not self.is_running:
            logging.warning("File activity tracker is not running")
            return False
        
        # Stop the watchdog observer
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        # Cancel scheduled checks
        if self.timer:
            self.timer.cancel()
            self.timer = None
        
        self.is_running = False
        logging.info("Stopped monitoring file activity")
        return True
    
    def _initialize_activity_data(self):
        """Initialize activity data for existing files"""
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            # Skip ignored directories
            dirnames[:] = [d for d in dirnames if d not in self.ignored_dirs and 
                          os.path.join(self.root_dir, d) != self.inactive_path]
            
            for filename in filenames:
                if filename in self.ignored_files:
                    continue
                
                filepath = os.path.join(dirpath, filename)
                # Record current access and modification times
                self._update_file_activity(filepath)
    
    def _update_file_activity(self, filepath):
        """Update activity data for a file"""
        try:
            if os.path.exists(filepath):
                rel_path = os.path.relpath(filepath, self.root_dir)
                self.activity_data[rel_path] = {
                    'last_access': os.path.getatime(filepath),
                    'last_modified': os.path.getmtime(filepath),
                    'last_checked': time.time()
                }
        except Exception as e:
            logging.error(f"Error updating activity data for {filepath}: {e}")
    
    def _schedule_inactivity_check(self):
        """Schedule the next check for inactive files"""
        if self.is_running:
            self._check_inactive_files()
            self.timer = threading.Timer(self.check_interval, self._schedule_inactivity_check)
            self.timer.daemon = True
            self.timer.start()
    
    def _check_inactive_files(self):
        """Check for inactive files and move them if needed"""
        current_time = time.time()
        
        # Check files in the root directory
        self._check_root_files(current_time)
        
        # Check files in the inactive directory
        self._check_inactive_files_for_activity(current_time)
        
        logging.info("Completed inactivity check")
    
    def _check_root_files(self, current_time):
        """Check files in the root directory for inactivity"""
        # Get list of files in the root directory (excluding the inactive folder)
        for dirpath, _, filenames in os.walk(self.root_dir):
            # Skip the inactive folder and other ignored directories
            rel_dirpath = os.path.relpath(dirpath, self.root_dir)
            if (rel_dirpath in self.ignored_dirs or 
                rel_dirpath.startswith(self.inactive_folder) or
                any(ignored in rel_dirpath.split(os.sep) for ignored in self.ignored_dirs)):
                continue
            
            for filename in filenames:
                if filename in self.ignored_files:
                    continue
                
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, self.root_dir)
                
                # Update activity data if it doesn't exist
                if rel_path not in self.activity_data:
                    self._update_file_activity(filepath)
                    continue
                
                activity_info = self.activity_data[rel_path]
                last_activity = max(activity_info['last_access'], activity_info['last_modified'])
                
                # Check if the file has been inactive for too long
                if (current_time - last_activity) > self.inactivity_threshold:
                    self._move_to_inactive(filepath)
    
    def _check_inactive_files_for_activity(self, current_time):
        """Check files in the inactive folder for recent activity"""
        if not os.path.exists(self.inactive_path):
            return
        
        for dirpath, _, filenames in os.walk(self.inactive_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                # Get the relative path inside the inactive folder
                rel_path_in_inactive = os.path.relpath(filepath, self.inactive_path)
                
                # Get actual file information
                try:
                    # Check if the file has been accessed recently
                    access_time = os.path.getatime(filepath)
                    modified_time = os.path.getmtime(filepath)
                    last_activity = max(access_time, modified_time)
                    
                    # If the file was accessed since the last check, move it back to root
                    if (current_time - last_activity) < self.inactivity_threshold:
                        self._move_to_root(filepath, rel_path_in_inactive)
                except Exception as e:
                    logging.error(f"Error checking inactive file {filepath}: {e}")
    
    def _move_to_inactive(self, filepath):
        """Move a file to the inactive folder"""
        try:
            # Get the path relative to the root
            rel_path = os.path.relpath(filepath, self.root_dir)
            # Destination path in the inactive folder
            dest_path = os.path.join(self.inactive_path, rel_path)
            
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Move the file
            shutil.move(filepath, dest_path)
            logging.info(f"Moved inactive file to storage: {rel_path}")
            
            # Update activity data
            if rel_path in self.activity_data:
                del self.activity_data[rel_path]
                
        except Exception as e:
            logging.error(f"Error moving file to inactive folder: {filepath} - {e}")
    
    def _move_to_root(self, filepath, rel_path_in_inactive):
        """Move a file from the inactive folder back to the root"""
        try:
            # Destination path in the root directory
            dest_path = os.path.join(self.root_dir, rel_path_in_inactive)
            
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Move the file
            shutil.move(filepath, dest_path)
            logging.info(f"Moved active file back to root: {rel_path_in_inactive}")
            
            # Update activity data
            self._update_file_activity(dest_path)
                
        except Exception as e:
            logging.error(f"Error moving file to root: {filepath} - {e}")

# Add missing import
import shutil