import os
import shutil
import time
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Queue for thread-safe logging between watchdog thread and GUI
log_queue = queue.Queue()

# Custom logging handler to redirect logs to the queue
class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Add queue handler to the root logger
queue_handler = QueueHandler(log_queue)
logging.getLogger().addHandler(queue_handler)

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
            self.move_item(src_path, dest_path)

    def move_item(self, src_path, dest_path):
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

class FileMoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Mover")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Set GUI style
        style = ttk.Style()
        style.theme_use('clam')  # Use a modern theme if available
        
        # Initialize variables
        self.source_path = tk.StringVar(value=os.path.expanduser("~/Desktop/Source"))
        self.destination_path = tk.StringVar(value=os.path.expanduser("~/Desktop/Dest"))
        self.is_monitoring = False
        self.observer = None
        self.event_handler = None
        
        # Create GUI components
        self.create_widgets()
        
        # Set up log display updater
        self.update_log_display()
        
    def create_widgets(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create and configure directory selection frame
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Settings", padding="10")
        dir_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Source directory selection
        ttk.Label(dir_frame, text="Source Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(dir_frame, textvariable=self.source_path, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)
        
        # Destination directory selection
        ttk.Label(dir_frame, text="Destination Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(dir_frame, textvariable=self.destination_path, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_destination).grid(row=1, column=2, padx=5, pady=5)
        
        # Configure grid columns to expand
        dir_frame.columnconfigure(1, weight=1)
        
        # Controls frame
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start/Stop buttons
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Add move all button for one-time processing
        self.move_all_button = ttk.Button(control_frame, text="Move All Now", command=self.move_all_items)
        self.move_all_button.pack(side=tk.LEFT, padx=5)
        
        # Create log display
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrolled text for log display
        self.log_display = scrolledtext.ScrolledText(log_frame, width=80, height=15)
        self.log_display.pack(fill=tk.BOTH, expand=True)
        self.log_display.config(state=tk.DISABLED)  # Make read-only
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_source(self):
        directory = filedialog.askdirectory(initialdir=self.source_path.get())
        if directory:
            self.source_path.set(directory)
    
    def browse_destination(self):
        directory = filedialog.askdirectory(initialdir=self.destination_path.get())
        if directory:
            self.destination_path.set(directory)
    
    def process_all_items_in_directory(self, source_dir, destination_dir, event_handler):
        """Recursively process all files and folders in a directory"""
        try:
            # Process all items including empty folders
            for item in os.listdir(source_dir):
                source_item = os.path.join(source_dir, item)
                # Calculate the relative path to maintain directory structure
                rel_path = os.path.relpath(source_item, self.source_path.get())
                destination_item = os.path.join(self.destination_path.get(), rel_path)
                
                # If it's a directory, recursively process its contents first
                if os.path.isdir(source_item):
                    # Check if the directory is empty
                    if not os.listdir(source_item):
                        # It's an empty directory, move it directly
                        event_handler.move_item(source_item, destination_item)
                    else:
                        # Process contents first, then the directory will be empty and can be moved
                        self.process_all_items_in_directory(source_item, destination_item, event_handler)
                        # After processing contents, move the now-empty directory
                        if os.path.exists(source_item):  # Check if still exists (might have been moved already)
                            event_handler.move_item(source_item, destination_item)
                else:
                    # It's a file, move it
                    event_handler.move_item(source_item, destination_item)
        except Exception as e:
            logging.error(f"Error processing directory {source_dir}: {e}")
    
    def move_all_items(self):
        """Move all items from source to destination once"""
        source = self.source_path.get()
        destination = self.destination_path.get()
        
        # Validate directories
        if not os.path.exists(source):
            try:
                os.makedirs(source)
                logging.info(f"Created source directory: {source}")
            except Exception as e:
                logging.error(f"Error creating source directory: {e}")
                return
        
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                logging.info(f"Created destination directory: {destination}")
            except Exception as e:
                logging.error(f"Error creating destination directory: {e}")
                return
        
        # Create event handler for moving items
        event_handler = FileHandler(source, destination)
        
        # Update status
        self.status_var.set(f"Moving all items from {source} to {destination}...")
        
        # Run in a separate thread to avoid freezing the GUI
        threading.Thread(
            target=self.process_all_items_in_directory, 
            args=(source, destination, event_handler),
            daemon=True
        ).start()
    
    def start_monitoring(self):
        source = self.source_path.get()
        destination = self.destination_path.get()
        
        # Validate directories
        if not os.path.exists(source):
            try:
                os.makedirs(source)
                logging.info(f"Created source directory: {source}")
            except Exception as e:
                logging.error(f"Error creating source directory: {e}")
                return
        
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                logging.info(f"Created destination directory: {destination}")
            except Exception as e:
                logging.error(f"Error creating destination directory: {e}")
                return
        
        # Setup observer with the event handler
        self.event_handler = FileHandler(source, destination)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, source, recursive=True)
        
        # Start the observer in a separate thread
        self.observer.start()
        self.is_monitoring = True
        
        # Process any existing items in the source directory, including empty folders
        threading.Thread(
            target=self.process_all_items_in_directory, 
            args=(source, destination, self.event_handler),
            daemon=True
        ).start()
        
        # Update GUI states
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.move_all_button.config(state=tk.DISABLED)
        self.status_var.set(f"Monitoring {source} for changes...")
        logging.info(f"Started monitoring {source} for new files/folders...")
    
    def stop_monitoring(self):
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            
            # Update GUI states
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.move_all_button.config(state=tk.NORMAL)
            self.status_var.set("Monitoring stopped")
            logging.info("File monitoring stopped.")
    
    def update_log_display(self):
        # Process all log records currently in the queue
        while True:
            try:
                record = log_queue.get_nowait()
                self.log_display.config(state=tk.NORMAL)  # Make writable
                self.log_display.insert(tk.END, f"{record.asctime} - {record.message}\n")
                self.log_display.see(tk.END)  # Scroll to the end
                self.log_display.config(state=tk.DISABLED)  # Make read-only again
            except queue.Empty:
                break
        
        # Schedule this method to run again after 100ms
        self.root.after(100, self.update_log_display)
    
    def on_closing(self):
        # Stop monitoring when the application is closed
        if self.is_monitoring:
            self.stop_monitoring()
        self.root.destroy()

def main():
    # Create the main window
    root = tk.Tk()
    app = FileMoverGUI(root)
    
    # Set up window close event
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main() 