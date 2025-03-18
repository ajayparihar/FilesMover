# pip install watchdog
import os
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure source and destination paths
source = r'C:\Users\ajays\OneDrive\Desktop\Source'
destination = r'C:\Users\ajays\OneDrive\Desktop\Dest'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class FileHandler(FileSystemEventHandler):
    """
    Handler for file system events (creation or modification).
    Processes files and directories by moving them to the destination.
    """
    
    def on_created(self, event):
        """Called when a file or directory is created"""
        self._process_event(event)
        
    def on_modified(self, event):
        """Called when a file or directory is modified"""
        self._process_event(event)
        
    def _process_event(self, event):
        """Process file system events for files and directories"""
        # Skip directory creation events that might be triggered during file creation
        if event.is_directory:
            return
            
        src_path = event.src_path
        # Get the relative path from the source directory
        rel_path = os.path.relpath(src_path, source)
        # Construct the destination path
        dest_path = os.path.join(destination, rel_path)
        
        # Wait for any file operations to complete
        time.sleep(0.5)
        
        # Only process if the file still exists (to avoid processing deleted files)
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

def main():
    """
    Main function to start monitoring the source directory
    using watchdog's event-driven approach.
    """
    # Ensure source and destination directories exist
    if not os.path.exists(source):
        logging.error(f"Source directory does not exist: {source}")
        return
    
    if not os.path.exists(destination):
        try:
            os.makedirs(destination)
            logging.info(f"Created destination directory: {destination}")
        except Exception as e:
            logging.error(f"Error creating destination directory: {e}")
            return
    
    # Process any existing files in the source directory
    for item in os.listdir(source):
        source_item = os.path.join(source, item)
        destination_item = os.path.join(destination, item)
        move_item(source_item, destination_item)
    
    # Set up the observer with the event handler
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, source, recursive=True)
    
    # Start the observer
    observer.start()
    
    logging.info(f"Started monitoring {source} for new files/folders...")
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the observer gracefully on keyboard interrupt
        observer.stop()
        logging.info("File monitoring stopped.")
    
    # Wait for the observer to complete
    observer.join()

if __name__ == "__main__":
    main() 