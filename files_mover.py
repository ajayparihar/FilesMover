import os
import shutil
import logging
from watchdog.observers import Observer

class FilesMover:
    def __init__(self, source_dir, destination_dir, rules):
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.rules = rules
        self.logger = logging.getLogger(__name__)
        self.is_monitoring = False
        self.observer = Observer()

    def process_existing_files(self):
        """Process all existing files in the source directory."""
        try:
            # Get all files in the source directory
            for filename in os.listdir(self.source_dir):
                file_path = os.path.join(self.source_dir, filename)
                
                # Skip if it's a directory
                if os.path.isdir(file_path):
                    continue
                    
                # Get file extension
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Find matching rule
                matching_rule = None
                for rule in self.rules:
                    if file_ext in rule['extensions']:
                        matching_rule = rule
                        break
                
                if matching_rule:
                    # Create destination directory if it doesn't exist
                    dest_dir = os.path.join(self.destination_dir, matching_rule['folder'])
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    # Move the file
                    dest_path = os.path.join(dest_dir, filename)
                    try:
                        shutil.move(file_path, dest_path)
                        self.logger.info(f"Moved existing file: {filename} to {matching_rule['folder']}")
                    except Exception as e:
                        self.logger.error(f"Error moving existing file {filename}: {str(e)}")
                else:
                    self.logger.info(f"No matching rule found for existing file: {filename}")
                    
        except Exception as e:
            self.logger.error(f"Error processing existing files: {str(e)}")

    def start_monitoring(self):
        """Start monitoring the source directory."""
        if self.is_monitoring:
            self.logger.warning("Monitoring is already running")
            return
            
        self.is_monitoring = True
        self.logger.info("Starting file monitoring...")
        
        # Process existing files first
        self.process_existing_files()
        
        # Start the file system observer
        self.observer.start()
        self.logger.info("File monitoring started successfully") 