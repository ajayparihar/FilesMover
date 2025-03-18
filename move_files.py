import os
import shutil
import time
import logging

# Configure source and destination paths
source = r'C:\Users\ajays\OneDrive\Desktop\Source'
destination = r'C:\Users\ajays\OneDrive\Desktop\Dest'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def move_item(src_path, dest_path):
    """
    Moves a file or folder from source to destination.
    If the destination already exists, it is removed first.
    
    Args:
        src_path: Path to the source item
        dest_path: Path to the destination item
    """
    try:
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

def monitor_directory():
    """
    Continuously monitors the source directory for new files and folders
    and moves them to the destination directory.
    """
    logging.info(f"Monitoring {source} for new files/folders...")
    
    while True:
        try:
            # List all files and folders in the source directory
            for item in os.listdir(source):
                source_item = os.path.join(source, item)
                destination_item = os.path.join(destination, item)
                move_item(source_item, destination_item)
                
        except Exception as e:
            logging.error(f"Error scanning directory: {e}")
            
        # Wait for a short period before checking again (e.g., 1 second)
        time.sleep(1)

def main():
    """
    Main function to ensure source and destination directories exist
    and start the monitoring process.
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
    
    # Start monitoring
    monitor_directory()

if __name__ == "__main__":
    main()
