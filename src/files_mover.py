import os
import shutil
import logging
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(message)s',
                   datefmt='%Y-%m-%d %H:%M:%S')

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, files_mover):
        self.files_mover = files_mover
        
    def on_created(self, event):
        if event.is_directory:
            self.files_mover.process_directory(event.src_path)
        else:
            self.files_mover.process_file(event.src_path)

class FilesMover:
    def __init__(self, source_dir, destination_dir, rules, conflict_mode="replace"):
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.rules = rules
        self.conflict_mode = conflict_mode  # Options: "replace", "skip", "rename"
        self.logger = logging.getLogger(__name__)
        self.is_monitoring = False
        self.observer = Observer()
        self.event_handler = FileEventHandler(self)

    def process_file(self, file_path):
        """Process a single file."""
        try:
            # Skip if it's a directory
            if os.path.isdir(file_path):
                return False
                
            # Get file information
            filename = os.path.basename(file_path)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Find matching rule
            matching_rule = next(
                (rule for rule in self.rules if file_ext in rule['extensions']),
                None
            )
            
            if matching_rule:
                # Create destination directory path
                dest_dir = os.path.join(self.destination_dir, matching_rule['folder'])
                os.makedirs(dest_dir, exist_ok=True)
                
                # Determine destination path
                dest_path = os.path.join(dest_dir, filename)
                
                # Handle file conflicts
                if os.path.exists(dest_path):
                    if self.conflict_mode == "skip":
                        self.logger.info(f"Skipped (already exists): {filename}")
                        return False
                    elif self.conflict_mode == "rename":
                        # Find a new name by appending a number
                        base_name, ext = os.path.splitext(dest_path)
                        counter = 1
                        while os.path.exists(f"{base_name}_{counter}{ext}"):
                            counter += 1
                        dest_path = f"{base_name}_{counter}{ext}"
                        self.logger.info(f"Renamed due to conflict: {filename} -> {os.path.basename(dest_path)}")
                    # For "replace" mode, we just continue with the move operation
                
                # Remember source directory to check if it becomes empty
                source_dir = os.path.dirname(file_path)
                
                # Move the file
                shutil.move(file_path, dest_path)
                self.logger.info(f"Moved file: {filename} to {matching_rule['folder']}")
                
                # Check if source directory is now empty and clean it up
                if source_dir != self.source_dir and os.path.exists(source_dir) and len(os.listdir(source_dir)) == 0:
                    try:
                        os.rmdir(source_dir)
                        self.logger.info(f"Removed empty directory: {os.path.relpath(source_dir, self.source_dir)}")
                    except OSError as e:
                        self.logger.warning(f"Could not remove empty directory: {os.path.relpath(source_dir, self.source_dir)}: {str(e)}")
                        
                return True
            else:
                self.logger.info(f"No matching rule found for file: {filename}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing file {os.path.basename(file_path)}: {str(e)}")
            return False

    def process_directory(self, dir_path):
        """Process a directory."""
        try:
            # Make sure we're working with a directory
            if not os.path.isdir(dir_path):
                return False
                
            # Get the relative path from source to the directory
            rel_path = os.path.relpath(dir_path, self.source_dir)
            
            # Create the destination directory
            dest_dir_path = os.path.join(self.destination_dir, rel_path)
            if not os.path.exists(dest_dir_path):
                os.makedirs(dest_dir_path, exist_ok=True)
                self.logger.info(f"Created directory: {rel_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error processing directory {os.path.basename(dir_path)}: {str(e)}")
            return False
            
    def process_existing_files(self):
        """Process all existing files in the source directory."""
        try:
            # First process directories first to ensure structure is preserved
            for dirpath, dirnames, filenames in os.walk(self.source_dir):
                # Process all directories first to create structure
                for dirname in dirnames:
                    full_dir_path = os.path.join(dirpath, dirname)
                    self.process_directory(full_dir_path)
                    
            # Then process all files
            for dirpath, _, filenames in os.walk(self.source_dir):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    self.process_file(file_path)
                    
        except Exception as e:
            self.logger.error(f"Error processing existing files: {str(e)}")

    def start_monitoring(self):
        """Start monitoring the source directory."""
        if self.is_monitoring:
            self.logger.warning("Monitoring is already running")
            return False
            
        try:
            self.is_monitoring = True
            self.logger.info("Starting file monitoring...")
            
            # Process existing files first
            self.process_existing_files()
            
            # Set up and start the observer
            self.observer = Observer()
            self.observer.schedule(self.event_handler, self.source_dir, recursive=False)
            self.observer.start()
            self.logger.info("File monitoring started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {str(e)}")
            self.is_monitoring = False
            return False

    def stop_monitoring(self):
        """Stop monitoring the source directory."""
        if not self.is_monitoring:
            return
            
        self.observer.stop()
        self.observer.join()
        self.is_monitoring = False
        self.logger.info("File monitoring stopped")

class FilesMoverGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Files Mover")
        self.root.geometry("800x600")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', padding=5)
        self.style.configure('Status.TLabel', padding=5)
        
        # Variables
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        self.monitoring_status = tk.StringVar(value="Status: Not Monitoring")
        self.conflict_mode = tk.StringVar(value="replace")
        
        # Default rules
        self.rules = [
            {"extensions": [".txt", ".doc", ".docx", ".pdf"], "folder": "documents"},
            {"extensions": [".jpg", ".jpeg", ".png", ".gif"], "folder": "images"},
            {"extensions": [".mp3", ".wav", ".flac"], "folder": "music"},
            {"extensions": [".mp4", ".avi", ".mkv"], "folder": "videos"}
        ]
        
        self.create_widgets()
        self.files_mover = None
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Directory selection section
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection", padding="5")
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Source directory
        ttk.Label(dir_frame, text="Source Directory:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(dir_frame, textvariable=self.source_dir, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_source).grid(row=0, column=2)
        
        # Destination directory
        ttk.Label(dir_frame, text="Destination Directory:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(dir_frame, textvariable=self.dest_dir, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_dest).grid(row=1, column=2)
        
        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Conflict mode selection
        ttk.Label(options_frame, text="When files exist in destination:").grid(row=0, column=0, sticky=tk.W)
        conflict_combo = ttk.Combobox(options_frame, textvariable=self.conflict_mode, width=20)
        conflict_combo['values'] = ['replace', 'skip', 'rename']
        conflict_combo.current(0)
        conflict_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring).grid(row=0, column=1, padx=5)
        
        # Status label
        status_label = ttk.Label(main_frame, textvariable=self.monitoring_status, style='Status.TLabel')
        status_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure logging to GUI
        self.setup_logging()
        
        # Make the grid expandable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def setup_logging(self):
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                self.text_widget.after(0, append)
        
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        
    def browse_source(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_dir.set(directory)
            
    def browse_dest(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dest_dir.set(directory)
            
    def start_monitoring(self):
        if not self.source_dir.get() or not self.dest_dir.get():
            logging.error("Please select both source and destination directories")
            return
            
        if not self.files_mover:
            self.files_mover = FilesMover(
                self.source_dir.get(),
                self.dest_dir.get(),
                self.rules,
                conflict_mode=self.conflict_mode.get()
            )
            
        if self.files_mover.start_monitoring():
            self.monitoring_status.set("Status: Monitoring Active")
            
    def stop_monitoring(self):
        if self.files_mover:
            self.files_mover.stop_monitoring()
            self.monitoring_status.set("Status: Not Monitoring")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FilesMoverGUI()
    app.run() 