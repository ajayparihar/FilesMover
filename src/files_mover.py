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
        if not event.is_directory:
            self.files_mover.process_file(event.src_path)

class FilesMover:
    def __init__(self, source_dir, destination_dir, rules):
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.rules = rules
        self.logger = logging.getLogger(__name__)
        self.is_monitoring = False
        self.observer = Observer()
        self.event_handler = FileEventHandler(self)

    def process_file(self, file_path):
        """Process a single file."""
        try:
            filename = os.path.basename(file_path)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Find matching rule
            matching_rule = next(
                (rule for rule in self.rules if file_ext in rule['extensions']),
                None
            )
            
            if matching_rule:
                dest_dir = os.path.join(self.destination_dir, matching_rule['folder'])
                os.makedirs(dest_dir, exist_ok=True)
                
                dest_path = os.path.join(dest_dir, filename)
                shutil.move(file_path, dest_path)
                self.logger.info(f"Moved file: {filename} to {matching_rule['folder']}")
            else:
                self.logger.info(f"No matching rule found for file: {filename}")
                
        except Exception as e:
            self.logger.error(f"Error processing file {filename}: {str(e)}")

    def process_existing_files(self):
        """Process all existing files in the source directory."""
        try:
            for filename in os.listdir(self.source_dir):
                file_path = os.path.join(self.source_dir, filename)
                if not os.path.isdir(file_path):
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
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring).grid(row=0, column=1, padx=5)
        
        # Status label
        status_label = ttk.Label(main_frame, textvariable=self.monitoring_status, style='Status.TLabel')
        status_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
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
                self.rules
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