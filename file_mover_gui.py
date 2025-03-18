import os
import shutil
import time
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import queue
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define settings file path
APP_DATA_DIR = os.path.join(os.path.expanduser('~'), '.file_mover')
SETTINGS_FILE = os.path.join(APP_DATA_DIR, 'settings.json')

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
        self.root.title("File Mover - Automated File Management Tool")
        self.root.geometry("850x650")
        self.root.minsize(650, 450)
        
        # Set app icon if available
        try:
            self.root.iconbitmap("file_mover_icon.ico")
        except:
            pass  # Icon not found, use default
        
        # Set GUI style
        self.setup_styles()
        
        # Initialize variables with default values
        self.source_path = tk.StringVar(value=os.path.expanduser("~/Desktop/Source"))
        self.destination_path = tk.StringVar(value=os.path.expanduser("~/Desktop/Dest"))
        self.is_monitoring = False
        self.observer = None
        self.event_handler = None
        self.file_count = tk.IntVar(value=0)
        self.file_count_label = None
        self.auto_start = tk.BooleanVar(value=False)
        self.auto_create_dirs = tk.BooleanVar(value=True)
        
        # Load saved settings if they exist
        self.load_settings()
        
        # Create GUI components
        self.create_widgets()
        
        # Set up log display updater
        self.update_log_display()
        
        # Set up the close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Auto-start monitoring if enabled
        if self.auto_start.get():
            # Use after to delay the start until the GUI is fully loaded
            self.root.after(1000, self.start_monitoring)
    
    def setup_styles(self):
        """Set up the visual styles for the application"""
        style = ttk.Style()
        
        # Try to use a more modern theme if available
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
        elif 'winnative' in available_themes:
            style.theme_use('winnative')
        
        # Configure custom styles
        style.configure('TButton', font=('Segoe UI', 9))
        style.configure('TLabel', font=('Segoe UI', 9))
        style.configure('TFrame', background='#f0f0f0')
        style.configure('Header.TLabel', font=('Segoe UI', 10, 'bold'))
        
        # Configure the button styles
        style.configure('Green.TButton', foreground='dark green')
        style.configure('Red.TButton', foreground='dark red')
        style.configure('Blue.TButton', foreground='navy')
        
    def create_widgets(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with app description
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        ttk.Label(header_frame, text="File Mover", font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="- Automatically move files from source to destination", 
                 font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Main tab
        main_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(main_tab, text="Main")
        
        # Settings tab
        settings_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(settings_tab, text="Settings")
        
        # Help tab
        help_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(help_tab, text="Help")
        
        # ------- MAIN TAB CONTENT -------
        
        # Create and configure directory selection frame
        dir_frame = ttk.LabelFrame(main_tab, text="Directory Settings", padding="10")
        dir_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Source directory selection
        ttk.Label(dir_frame, text="Source Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        source_entry = ttk.Entry(dir_frame, textvariable=self.source_path, width=50)
        source_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        CreateToolTip(source_entry, "The directory to monitor for new files")
        
        browse_source_btn = ttk.Button(dir_frame, text="Browse...", command=self.browse_source)
        browse_source_btn.grid(row=0, column=2, padx=5, pady=5)
        CreateToolTip(browse_source_btn, "Select the source directory")
        
        # Destination directory selection
        ttk.Label(dir_frame, text="Destination Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        dest_entry = ttk.Entry(dir_frame, textvariable=self.destination_path, width=50)
        dest_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        CreateToolTip(dest_entry, "Where files will be moved to")
        
        browse_dest_btn = ttk.Button(dir_frame, text="Browse...", command=self.browse_destination)
        browse_dest_btn.grid(row=1, column=2, padx=5, pady=5)
        CreateToolTip(browse_dest_btn, "Select the destination directory")
        
        # Configure grid columns to expand
        dir_frame.columnconfigure(1, weight=1)
        
        # Controls frame
        control_frame = ttk.LabelFrame(main_tab, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start/Stop buttons
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", 
                                      command=self.start_monitoring, style='Green.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        CreateToolTip(self.start_button, "Start monitoring the source directory for new files")
        
        self.stop_button = ttk.Button(control_frame, text="Stop Monitoring", 
                                     command=self.stop_monitoring, state=tk.DISABLED, style='Red.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        CreateToolTip(self.stop_button, "Stop the monitoring process")
        
        # Add move all button for one-time processing
        self.move_all_button = ttk.Button(control_frame, text="Move All Files Now", 
                                         command=self.move_all_items, style='Blue.TButton')
        self.move_all_button.pack(side=tk.LEFT, padx=5)
        CreateToolTip(self.move_all_button, "Move all existing files in the source directory now")
        
        # Add file counter
        self.file_count_label = ttk.Label(control_frame, text="Files moved: 0")
        self.file_count_label.pack(side=tk.RIGHT, padx=10)
        
        # Create log display
        log_frame = ttk.LabelFrame(main_tab, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(log_controls, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT)
        ttk.Button(log_controls, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)
        
        # Scrolled text for log display
        self.log_display = scrolledtext.ScrolledText(log_frame, width=80, height=15)
        self.log_display.pack(fill=tk.BOTH, expand=True)
        self.log_display.config(state=tk.DISABLED)  # Make read-only
        
        # ------- SETTINGS TAB CONTENT -------
        settings_frame = ttk.Frame(settings_tab)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Function to save when settings change
        def on_setting_change(*args):
            self.save_settings()
        
        # Auto-start option
        auto_start_check = ttk.Checkbutton(settings_frame, text="Auto-start monitoring when application launches", 
                                         variable=self.auto_start, command=on_setting_change)
        auto_start_check.pack(anchor=tk.W, padx=10, pady=10)
        
        # Auto-create directories option
        auto_create_check = ttk.Checkbutton(settings_frame, text="Auto-create directories if they don't exist", 
                                         variable=self.auto_create_dirs, command=on_setting_change)
        auto_create_check.pack(anchor=tk.W, padx=10, pady=5)
        
        # Save settings button - still useful for confirmations
        ttk.Button(settings_frame, text="Save Settings", command=self.save_settings).pack(anchor=tk.W, padx=10, pady=10)
        
        # ------- HELP TAB CONTENT -------
        help_frame = ttk.Frame(help_tab)
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        help_text = """
File Mover Help

How to use this application:

1. Set the Source Directory - This is the folder you want to monitor for new files
2. Set the Destination Directory - This is where files will be moved to
3. Click "Start Monitoring" to begin automatic file moving
4. Click "Stop Monitoring" to pause the process
5. Click "Move All Files Now" to immediately process all existing files

Features:
- Files and folders are moved automatically when they appear in the source directory
- Original directory structure is preserved in the destination
- Existing files in the destination are overwritten
- Activity is logged in the log window
- All settings and directory locations are automatically saved
- Settings will persist between application restarts

Tips:
- You can save your log for future reference
- The application can be set to start monitoring automatically on launch in the Settings tab
- Source and destination paths are automatically saved when you change them
- Settings are saved in ~/.file_mover/settings.json
        """
        
        help_display = scrolledtext.ScrolledText(help_frame, width=80, height=20)
        help_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_display.insert(tk.END, help_text)
        help_display.config(state=tk.DISABLED)  # Make read-only
        
        # Status bar with progressbar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate', length=150)
        self.progress_bar.pack(side=tk.RIGHT, padx=(0, 10), pady=2)
        
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=0, pady=0)
    
    def browse_source(self):
        directory = filedialog.askdirectory(initialdir=self.source_path.get())
        if directory:
            self.source_path.set(directory)
            
            # Create the directory if it doesn't exist and auto-create is enabled
            if self.auto_create_dirs.get() and not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    self.log_message(f"Created source directory: {directory}")
                except Exception as e:
                    self.log_message(f"Error creating source directory: {e}", level=logging.ERROR)
            
            # Save settings when directory changes
            self.save_settings()
    
    def browse_destination(self):
        directory = filedialog.askdirectory(initialdir=self.destination_path.get())
        if directory:
            self.destination_path.set(directory)
            
            # Create the directory if it doesn't exist and auto-create is enabled
            if self.auto_create_dirs.get() and not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    self.log_message(f"Created destination directory: {directory}")
                except Exception as e:
                    self.log_message(f"Error creating destination directory: {e}", level=logging.ERROR)
                    
            # Save settings when directory changes
            self.save_settings()
    
    def process_all_items_in_directory(self, source_dir, destination_dir, event_handler):
        """Recursively process all files and folders in a directory"""
        try:
            # Process all items including empty folders
            if not os.path.exists(source_dir):
                self.log_message(f"Source directory does not exist: {source_dir}", level=logging.ERROR)
                return
                
            # Reset file counter
            files_moved = 0
            
            # Get total files to process for progress tracking
            total_files = sum([len(files) for _, _, files in os.walk(source_dir)])
            
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
                        sub_files_moved = self.process_all_items_in_directory(source_item, destination_item, event_handler)
                        files_moved += sub_files_moved
                        
                        # After processing contents, move the now-empty directory
                        if os.path.exists(source_item):  # Check if still exists (might have been moved already)
                            event_handler.move_item(source_item, destination_item)
                else:
                    # It's a file, move it
                    event_handler.move_item(source_item, destination_item)
                    files_moved += 1
                    
                    # Update file count on GUI thread
                    self.root.after(0, self.update_file_count, files_moved)
                    
            # Return the number of files moved for tracking
            return files_moved
                    
        except Exception as e:
            self.log_message(f"Error processing directory {source_dir}: {e}", level=logging.ERROR)
            return 0
    
    def move_all_items(self):
        """Move all items from source to destination once"""
        source = self.source_path.get()
        destination = self.destination_path.get()
        
        # Validate directories
        if not self.validate_directories():
            return
        
        # Create event handler for moving items
        event_handler = FileHandler(source, destination)
        
        # Update status and start progress bar
        self.status_var.set(f"Moving all items from {source} to {destination}...")
        self.progress_bar.start()
        self.move_all_button.config(state=tk.DISABLED)
        
        # Reset file counter
        self.file_count.set(0)
        
        # Run in a separate thread to avoid freezing the GUI
        thread = threading.Thread(
            target=self.run_move_all_with_cleanup, 
            args=(source, destination, event_handler),
            daemon=True
        )
        thread.start()
    
    def run_move_all_with_cleanup(self, source, destination, event_handler):
        """Run move all process with proper cleanup"""
        try:
            files_moved = self.process_all_items_in_directory(source, destination, event_handler)
            
            # Update status when complete
            self.root.after(0, lambda: self.status_var.set(f"Moved {files_moved} files/folders successfully"))
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.move_all_button.config(state=tk.NORMAL))
            
            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo("Operation Complete", 
                                                   f"Successfully moved {files_moved} files/folders"))
        except Exception as e:
            # Handle any unexpected exceptions
            self.root.after(0, lambda: self.log_message(f"Error during file move operation: {e}", level=logging.ERROR))
            self.root.after(0, lambda: self.status_var.set("Error during operation"))
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.move_all_button.config(state=tk.NORMAL))
    
    def validate_directories(self):
        """Validate source and destination directories"""
        source = self.source_path.get()
        destination = self.destination_path.get()
        
        if not source or not destination:
            messagebox.showerror("Error", "Both source and destination directories must be specified")
            return False
            
        # Check if directories are the same
        if os.path.normpath(source) == os.path.normpath(destination):
            messagebox.showerror("Error", "Source and destination directories cannot be the same")
            return False
            
        # Check if destination is a subdirectory of source (would cause infinite recursion)
        if os.path.commonpath([source]) == os.path.commonpath([source, destination]) and source != destination:
            messagebox.showerror("Error", "Destination cannot be a subdirectory of source")
            return False
        
        # Check/create source directory
        if not os.path.exists(source):
            if self.auto_create_dirs.get():
                try:
                    os.makedirs(source)
                    self.log_message(f"Created source directory: {source}")
                except Exception as e:
                    self.log_message(f"Error creating source directory: {e}", level=logging.ERROR)
                    messagebox.showerror("Error", f"Could not create source directory: {e}")
                    return False
            else:
                messagebox.showerror("Error", f"Source directory does not exist: {source}")
                return False
        
        # Check/create destination directory
        if not os.path.exists(destination):
            if self.auto_create_dirs.get():
                try:
                    os.makedirs(destination)
                    self.log_message(f"Created destination directory: {destination}")
                except Exception as e:
                    self.log_message(f"Error creating destination directory: {e}", level=logging.ERROR)
                    messagebox.showerror("Error", f"Could not create destination directory: {e}")
                    return False
            else:
                messagebox.showerror("Error", f"Destination directory does not exist: {destination}")
                return False
                
        return True
    
    def start_monitoring(self):
        """Start monitoring the source directory for changes"""
        source = self.source_path.get()
        destination = self.destination_path.get()
        
        # Validate directories
        if not self.validate_directories():
            return
            
        # Create event handler
        self.event_handler = FileHandler(source, destination)
        
        # Create and start observer
        self.observer = Observer()
        self.observer.schedule(self.event_handler, source, recursive=True)
        self.observer.start()
        
        # Update status
        self.is_monitoring = True
        self.status_var.set(f"Monitoring {source} for changes...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start progress bar animation to indicate active monitoring
        self.progress_bar.start()
        
        # Log start of monitoring
        self.log_message(f"Started monitoring {source} for changes")
    
    def stop_monitoring(self):
        """Stop monitoring the source directory"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            
        # Update status
        self.is_monitoring = False
        self.status_var.set("Monitoring stopped")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Stop progress bar animation
        self.progress_bar.stop()
        
        # Log stop of monitoring
        self.log_message("Stopped monitoring")
        
    def update_file_count(self, count=None):
        """Update the file count display"""
        if count is None:
            count = self.file_count.get() + 1
            self.file_count.set(count)
        
        if self.file_count_label:
            self.file_count_label.config(text=f"Files moved: {count}")
    
    def log_message(self, message, level=logging.INFO):
        """Add a message to the log directly from the GUI"""
        logging.log(level, message)
    
    def clear_log(self):
        """Clear the log display"""
        self.log_display.config(state=tk.NORMAL)
        self.log_display.delete(1.0, tk.END)
        self.log_display.config(state=tk.DISABLED)
        
    def save_log(self):
        """Save the log to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Log File"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.log_display.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Log saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")
    
    def save_settings(self):
        """Save current settings to a JSON file"""
        settings = {
            'source_path': self.source_path.get(),
            'destination_path': self.destination_path.get(),
            'auto_start': self.auto_start.get(),
            'auto_create_dirs': self.auto_create_dirs.get()
        }
        
        try:
            # Ensure directory exists
            if not os.path.exists(APP_DATA_DIR):
                os.makedirs(APP_DATA_DIR)
                
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
                
            self.log_message("Settings saved successfully")
            messagebox.showinfo("Settings Saved", "Your settings have been saved successfully")
        except Exception as e:
            self.log_message(f"Error saving settings: {e}", level=logging.ERROR)
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def load_settings(self):
        """Load settings from JSON file if it exists"""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                
                # Apply loaded settings
                if 'source_path' in settings:
                    self.source_path.set(settings['source_path'])
                
                if 'destination_path' in settings:
                    self.destination_path.set(settings['destination_path'])
                
                if 'auto_start' in settings:
                    self.auto_start.set(settings['auto_start'])
                
                if 'auto_create_dirs' in settings:
                    self.auto_create_dirs.set(settings['auto_create_dirs'])
                
                logging.info("Settings loaded successfully")
            except Exception as e:
                logging.error(f"Error loading settings: {e}")
                # Continue with default settings
        else:
            logging.info("No settings file found, using defaults")
    
    def update_log_display(self):
        """Process all log records currently in the queue"""
        while True:
            try:
                record = log_queue.get_nowait()
                self.log_display.config(state=tk.NORMAL)
                
                # Add a tag for error messages to highlight them
                if record.levelno >= logging.ERROR:
                    self.log_display.tag_config('error', foreground='red')
                    self.log_display.insert(tk.END, self.format_log_record(record) + '\n', 'error')
                elif record.levelno >= logging.WARNING:
                    self.log_display.tag_config('warning', foreground='orange')
                    self.log_display.insert(tk.END, self.format_log_record(record) + '\n', 'warning')
                else:
                    self.log_display.insert(tk.END, self.format_log_record(record) + '\n')
                
                self.log_display.see(tk.END)  # Auto-scroll to the end
                self.log_display.config(state=tk.DISABLED)
                
                # Increment file count for move operations
                if "Moved file:" in record.message or "Moved directory:" in record.message:
                    self.update_file_count()
                    
            except queue.Empty:
                break
                
        # Schedule to run again after 100ms
        self.root.after(100, self.update_log_display)
    
    def format_log_record(self, record):
        """Format a log record into a string for display"""
        return f"{record.asctime} - {record.message}"
    
    def on_closing(self):
        """Save settings and stop monitoring when the application is closed"""
        # Save current settings
        try:
            self.save_settings()
        except:
            pass  # Ignore errors on close
            
        # Stop monitoring if active
        if self.is_monitoring:
            self.stop_monitoring()
        self.root.destroy()

class CreateToolTip:
    """
    Create a tooltip for a given widget.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        
    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, 
                        background="#ffffe0", relief="solid", borderwidth=1,
                        padding=(5, 3))
        label.pack()
        
    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def main():
    # Create the main window
    root = tk.Tk()
    app = FileMoverGUI(root)
    
    # Set the closing protocol
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main() 