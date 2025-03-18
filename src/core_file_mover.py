import os
import shutil
import time
import logging
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

class FileHandler(FileSystemEventHandler):
    """
    Handler for file system events (creation or modification).
    Processes files and directories by moving them to the destination.
    """
    
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        
    def on_created(self, event):
        """Called when a file or directory is created"""
        self._process_event(event)
        
    def on_modified(self, event):
        """Called when a file or directory is modified"""
        self._process_event(event)
        
    def _process_event(self, event):
        """Process file system events for files and directories"""
        src_path = event.src_path
        # Get the relative path from the source directory
        rel_path = os.path.relpath(src_path, self.source)
        # Construct the destination path
        dest_path = os.path.join(self.destination, rel_path)
        
        # Wait for any file operations to complete
        time.sleep(0.5)
        
        # Only process if the source path still exists
        if os.path.exists(src_path):
            move_item(src_path, dest_path)

def move_item(src_path, dest_path):
    """
    Moves a file or folder from source to destination.
    If the destination already exists, it is removed first.
    
    Args:
        src_path: Path to the source item
        dest_path: Path to the destination item
    """
    try:
        # Create the destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        # Check if the destination already exists and delete it if it does
        if os.path.exists(dest_path):
            if os.path.isfile(dest_path):
                os.remove(dest_path)
                logging.info(f'Removed existing file: {dest_path}')
            elif os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
                logging.info(f'Removed existing directory: {dest_path}')
        
        # Check if it's a file or folder and move it
        if os.path.isfile(src_path):
            shutil.move(src_path, dest_path)
            logging.info(f'Moved file: {src_path} -> {dest_path}')
        elif os.path.isdir(src_path):
            shutil.move(src_path, dest_path)
            logging.info(f'Moved directory: {src_path} -> {dest_path}')
    except Exception as e:
        logging.error(f'Error moving {src_path}: {e}')
        return False
    return True

def process_all_items(source, destination):
    """
    Process all existing items in the source directory and move them to the destination.
    
    Args:
        source: Source directory path
        destination: Destination directory path
    
    Returns:
        int: Number of items processed
    """
    count = 0
    try:
        # List all items in the source directory
        for item in os.listdir(source):
            source_item = os.path.join(source, item)
            destination_item = os.path.join(destination, item)
            
            # Process files and directories
            if move_item(source_item, destination_item):
                count += 1
                
            # If it's a directory and it still exists (meaning it wasn't moved),
            # recursively process its contents
            if os.path.isdir(source_item) and os.path.exists(source_item):
                count += process_all_items(source_item, os.path.join(destination, item))
    except Exception as e:
        logging.error(f"Error processing items: {e}")
    
    return count

def start_monitoring(source, destination):
    """
    Start monitoring a directory for changes and move files to destination.
    
    Args:
        source: Source directory path
        destination: Destination directory path
    
    Returns:
        tuple: (Observer, FileHandler) - The watchdog observer and event handler
    """
    # Ensure source and destination directories exist
    if not os.path.exists(source):
        logging.error(f"Source directory does not exist: {source}")
        return None, None
    
    if not os.path.exists(destination):
        try:
            os.makedirs(destination)
            logging.info(f"Created destination directory: {destination}")
        except Exception as e:
            logging.error(f"Error creating destination directory: {e}")
            return None, None
    
    # Set up the observer with the event handler
    event_handler = FileHandler(source, destination)
    observer = Observer()
    observer.schedule(event_handler, source, recursive=True)
    
    # Start the observer
    observer.start()
    logging.info(f"Started monitoring {source} for new files/folders...")
    
    return observer, event_handler 