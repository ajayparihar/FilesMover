"""
Graphical user interface for the FilesMover utility.

This module provides a GUI interface to use the file mover functionality.
It includes a tabbed interface with main controls, settings, and help sections.

Classes:
    QueueHandler: Custom logging handler for thread-safe logging to GUI
    FileMoverGUI: Main GUI class for the FilesMover application
    CreateToolTip: Utility class for creating tooltips on widgets

Functions:
    main: Entry point function to run the GUI application
"""

import os
import time
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import queue
import json
from .core import FileProcessor, DirectoryMonitor
import sys

# Define settings file path
APP_DATA_DIR = os.path.join(os.path.expanduser('~'), '.file_mover')
SETTINGS_FILE = os.path.join(APP_DATA_DIR, 'settings.json')

# Queue for thread-safe logging between threads and GUI
log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    """
    Custom logging handler to redirect logs to a queue.
    
    This handler enables thread-safe logging by placing log records
    in a queue for later processing by the GUI thread.
    
    Attributes:
        log_queue (Queue): Queue for storing log records
    """
    def __init__(self, log_queue):
        """
        Initialize the queue handler.
        
        Args:
            log_queue (Queue): Queue to store log records
        """
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        """
        Place the log record in the queue.
        
        Args:
            record (LogRecord): Log record to be queued
        """
        self.log_queue.put(record)

# Configure logging for GUI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Add queue handler to the root logger
queue_handler = QueueHandler(log_queue)
logging.getLogger().addHandler(queue_handler)

class FileMoverGUI:
    """
    Main GUI class for the FilesMover application.
    
    This class implements the graphical user interface for the FilesMover utility,
    providing controls for file monitoring, settings management, and activity logging.
    
    Attributes:
        root (Tk): Root Tkinter window
        source_var (StringVar): Source directory path
        dest_var (StringVar): Destination directory path
        status_var (StringVar): Current status message
        file_count_var (StringVar): Count of processed files
        conflict_mode_var (StringVar): How to handle file conflicts
        preserve_timestamps_var (BooleanVar): Whether to preserve file timestamps
        confirm_deletions_var (BooleanVar): Whether to confirm file deletions
        recursive_monitoring_var (BooleanVar): Whether to monitor subdirectories
        processing_delay_var (DoubleVar): Delay before processing new files
        processor (FileProcessor): The file processor instance
        monitoring (bool): Whether file monitoring is active
        log_text (ScrolledText): Text widget for displaying logs
        monitor_button (Button): Button for toggling monitoring state
    """
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root (Tk): Root Tkinter window
        """
        self.root = root
        self.root.title("FilesMover")
        self.root.geometry("800x600")
        self.root.minsize(650, 500)
        
        # Ensure app data directory exists
        os.makedirs(APP_DATA_DIR, exist_ok=True)
        
        # Initialize variables
        self.source_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Desktop', 'Source'))
        self.dest_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Desktop', 'Dest'))
        self.status_var = tk.StringVar(value="Ready")
        self.file_count_var = tk.StringVar(value="Files: 0")
        
        # New settings variables
        self.conflict_mode_var = tk.StringVar(value="replace")
        self.preserve_timestamps_var = tk.BooleanVar(value=True)
        self.confirm_deletions_var = tk.BooleanVar(value=True)
        self.recursive_monitoring_var = tk.BooleanVar(value=False)
        self.processing_delay_var = tk.DoubleVar(value=0.5)
        
        # File processor
        self.processor = None
        self.monitoring = False
        
        # Setup GUI styles
        self.setup_styles()
        
        # Create widgets
        self.create_widgets()
        
        # Load settings
        self.load_settings()
        
        # Set up log display updater
        self.update_log_display()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """
        Create and configure ttk styles for the application.
        
        This method sets up the visual styles for the various widgets
        used in the application, ensuring a consistent look and feel.
        """
        style = ttk.Style()
        
        # Main styles
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TCheckbutton", background="#f0f0f0", font=("Segoe UI", 10))
        
        # Header style
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        
        # Status bar style
        style.configure("Status.TLabel", background="#e0e0e0", relief="sunken", padding=3)
    
    def create_widgets(self):
        """
        Create all GUI widgets and arrange them in the window.
        
        This method sets up the main layout of the application, including
        the tabbed interface and status bar.
        """
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        main_tab = ttk.Frame(notebook, padding="10")
        settings_tab = ttk.Frame(notebook, padding="10")
        help_tab = ttk.Frame(notebook, padding="10")
        
        notebook.add(main_tab, text="Main")
        notebook.add(settings_tab, text="Settings")
        notebook.add(help_tab, text="Help")
        
        # Fill the tabs with content
        self.create_main_tab(main_tab)
        self.create_settings_tab(settings_tab)
        self.create_help_tab(help_tab)
        
        # Status bar at the bottom
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Status.TLabel")
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        file_count_label = ttk.Label(status_frame, textvariable=self.file_count_var, style="Status.TLabel")
        file_count_label.pack(side=tk.RIGHT, padx=5)
        
    def create_main_tab(self, parent):
        """
        Create the main tab content with directory controls and log display.
        
        Args:
            parent (Frame): Parent frame to contain the widgets
        """
        # Directory frame
        dir_frame = ttk.LabelFrame(parent, text="Directories", padding="10")
        dir_frame.pack(fill=tk.X, pady=5)
        
        # Source directory
        source_label = ttk.Label(dir_frame, text="Source:")
        source_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        source_entry = ttk.Entry(dir_frame, textvariable=self.source_var, width=50)
        source_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        source_button = ttk.Button(dir_frame, text="Browse...", command=self.browse_source)
        source_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Destination directory
        dest_label = ttk.Label(dir_frame, text="Destination:")
        dest_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        dest_entry = ttk.Entry(dir_frame, textvariable=self.dest_var, width=50)
        dest_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        dest_button = ttk.Button(dir_frame, text="Browse...", command=self.browse_destination)
        dest_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Configure grid for directory frame
        dir_frame.columnconfigure(1, weight=1)
        
        # Action buttons
        action_frame = ttk.Frame(parent, padding="5")
        action_frame.pack(fill=tk.X, pady=5)
        
        monitor_button = ttk.Button(action_frame, text="Start Monitoring", command=self.toggle_monitoring)
        monitor_button.pack(side=tk.LEFT, padx=5)
        self.monitor_button = monitor_button
        
        move_all_button = ttk.Button(action_frame, text="Move All Files", command=self.move_all_items)
        move_all_button.pack(side=tk.LEFT, padx=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=70, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Log buttons
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.pack(fill=tk.X, pady=5)
        
        clear_log_button = ttk.Button(log_button_frame, text="Clear Log", command=self.clear_log)
        clear_log_button.pack(side=tk.LEFT, padx=5)
        
        save_log_button = ttk.Button(log_button_frame, text="Save Log", command=self.save_log)
        save_log_button.pack(side=tk.LEFT, padx=5)
    
    def create_settings_tab(self, parent):
        """
        Create the settings tab content with configuration options.
        
        Args:
            parent (Frame): Parent frame to contain the widgets
        """
        # Create a canvas with scrollbar for settings
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # File Handling Settings
        file_handling_frame = ttk.LabelFrame(scrollable_frame, text="File Handling", padding="10")
        file_handling_frame.pack(fill=tk.X, pady=5)
        
        # Conflict handling
        conflict_frame = ttk.Frame(file_handling_frame)
        conflict_frame.pack(fill=tk.X, pady=5)
        
        conflict_label = ttk.Label(conflict_frame, text="When file exists in destination:")
        conflict_label.pack(side=tk.LEFT, padx=5)
        
        conflict_combo = ttk.Combobox(
            conflict_frame, 
            textvariable=self.conflict_mode_var,
            values=["replace", "skip", "rename"],
            state="readonly",
            width=15
        )
        conflict_combo.pack(side=tk.LEFT, padx=5)
        
        # Add event handler to save settings when conflict mode changes
        conflict_combo.bind("<<ComboboxSelected>>", lambda e: self.save_settings())
        
        # Add tooltip for conflict handling
        CreateToolTip(
            conflict_combo, 
            "Choose how to handle files with the same name:\n"
            "- Replace: Overwrite existing files\n"
            "- Skip: Keep existing files, don't move new ones\n"
            "- Rename: Add a number to new files to avoid conflicts"
        )
        
        # Preserve timestamps option
        preserve_cb = ttk.Checkbutton(
            file_handling_frame, 
            text="Preserve file timestamps when moving", 
            variable=self.preserve_timestamps_var,
            command=self.save_settings
        )
        preserve_cb.pack(anchor=tk.W, pady=5)
        
        CreateToolTip(
            preserve_cb, 
            "When enabled, moved files will keep their original creation,\n"
            "modification, and access times."
        )
        
        # Confirm deletions option
        confirm_cb = ttk.Checkbutton(
            file_handling_frame, 
            text="Confirm before deleting or replacing files", 
            variable=self.confirm_deletions_var,
            command=self.save_settings
        )
        confirm_cb.pack(anchor=tk.W, pady=5)
        
        CreateToolTip(
            confirm_cb, 
            "When enabled, you'll be asked to confirm before any file is deleted\n"
            "or replaced in the destination directory."
        )
        
        # Performance Settings
        performance_frame = ttk.LabelFrame(scrollable_frame, text="Performance", padding="10")
        performance_frame.pack(fill=tk.X, pady=5)
        
        # Recursive monitoring option
        recursive_cb = ttk.Checkbutton(
            performance_frame, 
            text="Monitor subdirectories recursively", 
            variable=self.recursive_monitoring_var,
            command=self.save_settings
        )
        recursive_cb.pack(anchor=tk.W, pady=5)
        
        CreateToolTip(
            recursive_cb, 
            "When enabled, FilesMover will monitor all subdirectories\n"
            "within the source directory for file changes."
        )
        
        # Processing delay
        delay_frame = ttk.Frame(performance_frame)
        delay_frame.pack(fill=tk.X, pady=5)
        
        delay_label = ttk.Label(delay_frame, text="Processing delay (seconds):")
        delay_label.pack(side=tk.LEFT, padx=5)
        
        delay_entry = ttk.Entry(delay_frame, textvariable=self.processing_delay_var, width=10)
        delay_entry.pack(side=tk.LEFT, padx=5)
        
        # Add event handler to save settings when delay value changes
        delay_entry.bind("<FocusOut>", lambda e: self.save_settings())
        delay_entry.bind("<Return>", lambda e: self.save_settings())
        
        CreateToolTip(
            delay_entry, 
            "Delay before processing newly detected files.\n"
            "Useful to ensure files are completely written\n"
            "before being moved. Recommended: 0.5-2.0 seconds."
        )
        
        # Settings buttons
        settings_button_frame = ttk.Frame(scrollable_frame)
        settings_button_frame.pack(fill=tk.X, pady=15)
        
        save_settings_button = ttk.Button(settings_button_frame, text="Save Settings", command=self.save_settings)
        save_settings_button.pack(side=tk.RIGHT, padx=5)
        
        reset_settings_button = ttk.Button(settings_button_frame, text="Reset to Defaults", command=self.reset_settings)
        reset_settings_button.pack(side=tk.RIGHT, padx=5)
    
    def reset_settings(self):
        """
        Reset all settings to default values.
        """
        # Confirm with user
        if not messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            return
            
        # Reset to defaults
        self.source_var.set(os.path.join(os.path.expanduser('~'), 'Desktop', 'Source'))
        self.dest_var.set(os.path.join(os.path.expanduser('~'), 'Desktop', 'Dest'))
        self.conflict_mode_var.set("replace")
        self.preserve_timestamps_var.set(True)
        self.confirm_deletions_var.set(True)
        self.recursive_monitoring_var.set(False)
        self.processing_delay_var.set(0.5)
        
        # Save the default settings
        self.save_settings()
        
        self.log_message("Settings reset to defaults.")
    
    def create_help_tab(self, parent):
        """
        Create the help tab content with usage instructions.
        
        Args:
            parent (Frame): Parent frame to contain the widgets
        """
        # Help content
        help_frame = ttk.Frame(parent, padding="10")
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        help_label = ttk.Label(
            help_frame, 
            text="FilesMover Help", 
            style="Header.TLabel"
        )
        help_label.pack(anchor=tk.W, pady=10)
        
        help_text = scrolledtext.ScrolledText(help_frame, wrap=tk.WORD, width=70, height=15)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        help_content = """
FilesMover is a utility for organizing and moving files between directories.

Basic Usage:
1. Set the source and destination directories in the Main tab.
2. Click "Start Monitoring" to monitor the source directory for new files.
3. Use "Move All Files" to process all existing files at once.

File Handling:
- You can choose how to handle conflicts when files already exist in the destination.
- Enable "Preserve timestamps" to maintain the original file timestamps.
- Enable "Confirm deletions" for added protection of important destination files.

Performance:
- Enable recursive monitoring to watch all subdirectories within the source.
- Adjust the processing delay to ensure files are completely written before being moved.

Tips:
- The source and destination must be different directories.
- You can save your settings for future sessions.
- Check the activity log for detailed information about file operations.
"""
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    def browse_source(self):
        """
        Open a directory selection dialog for the source directory.
        
        This method displays a directory browser dialog to select the
        source directory and updates the corresponding variable.
        """
        directory = filedialog.askdirectory(initialdir=self.source_var.get())
        if directory:
            self.source_var.set(directory)
            self.log_message(f"Source directory set to: {os.path.normpath(directory)}")
            # Save settings after updating source
            self.save_settings()
    
    def browse_destination(self):
        """
        Open a directory selection dialog for the destination directory.
        
        This method displays a directory browser dialog to select the
        destination directory and updates the corresponding variable.
        """
        directory = filedialog.askdirectory(initialdir=self.dest_var.get())
        if directory:
            self.dest_var.set(directory)
            self.log_message(f"Destination directory set to: {os.path.normpath(directory)}")
            # Save settings after updating destination
            self.save_settings()
    
    def toggle_monitoring(self):
        """
        Start or stop file monitoring based on current state.
        
        This method toggles the monitoring state, updating the button text
        and status message accordingly.
        """
        if self.monitoring:
            self.stop_monitoring()
            self.monitor_button.config(text="Start Monitoring")
            self.status_var.set("Ready")
        else:
            if self.validate_directories():
                self.start_monitoring()
                self.monitor_button.config(text="Stop Monitoring")
                self.status_var.set("Monitoring...")
    
    def move_all_items(self):
        """
        Process all files in the source directory at once.
        
        This method creates a FileProcessor instance to move all files
        from the source to the destination directory in a separate thread.
        """
        if not self.validate_directories():
            return
        
        source = self.source_var.get()
        destination = self.dest_var.get()
        
        self.log_message(f"Moving all files from {os.path.normpath(source)} to {os.path.normpath(destination)}...")
        self.status_var.set("Processing files...")
        
        # Create a processor for one-time use
        processor = FileProcessor(
            source=source,
            destination=destination,
            activity_tracking=False,  # Always disable activity tracking
            conflict_mode=self.conflict_mode_var.get(),
            preserve_timestamps=self.preserve_timestamps_var.get(),
            confirm_operations=self.confirm_deletions_var.get(),
            recursive=self.recursive_monitoring_var.get(),
            processing_delay=self.processing_delay_var.get()
        )
        
        # Run in a separate thread to avoid freezing GUI
        thread = threading.Thread(target=self.run_move_all_with_progress, args=(processor,))
        thread.daemon = True
        thread.start()
    
    def run_move_all_with_progress(self, processor):
        """
        Run the move_all operation in a thread with progress updates.
        
        Args:
            processor (FileProcessor): The file processor to use
        """
        try:
            count = processor.process_all()
            self.update_file_count(count)
            self.log_message(f"Successfully moved {count} files/folders.", logging.INFO)
            self.root.after(0, lambda: self.status_var.set("Ready"))
        except Exception as e:
            self.log_message(f"Error processing files: {e}", logging.ERROR)
            self.root.after(0, lambda: self.status_var.set("Error"))
    
    def validate_directories(self):
        """
        Validate source and destination directories.
        
        This method checks that the source and destination directories are
        valid and creates them if they don't exist.
        
        Returns:
            bool: True if the directories are valid, False otherwise
        """
        source = self.source_var.get()
        destination = self.dest_var.get()
        
        # Check if source and destination are provided
        if not source or not destination:
            messagebox.showerror("Error", "Please specify both source and destination directories.")
            return False
        
        # Check if source and destination are the same
        if os.path.normpath(source) == os.path.normpath(destination):
            messagebox.showerror("Error", "Source and destination directories cannot be the same.")
            return False
        
        # Check if source directory exists or create it
        if not os.path.exists(source):
            try:
                os.makedirs(source)
                self.log_message(f"Created source directory: {os.path.normpath(source)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create source directory: {e}")
                return False
        
        # Check if destination directory exists or create it
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                self.log_message(f"Created destination directory: {os.path.normpath(destination)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create destination directory: {e}")
                return False
        
        return True
    
    def start_monitoring(self):
        """
        Start monitoring files in the source directory.
        
        This method creates a FileProcessor and DirectoryMonitor instance and starts 
        monitoring the source directory for file changes.
        """
        source = self.source_var.get()
        destination = self.dest_var.get()
        
        self.log_message("First moving all existing files before starting monitoring...")
        
        # Create the file processor
        try:
            file_processor = FileProcessor(
                source=source,
                destination=destination,
                activity_tracking=False,  # Always disable activity tracking
                conflict_mode=self.conflict_mode_var.get(),
                preserve_timestamps=self.preserve_timestamps_var.get(),
                confirm_operations=self.confirm_deletions_var.get(),
                recursive=self.recursive_monitoring_var.get(),
                processing_delay=self.processing_delay_var.get(),
                process_existing=True
            )
        except Exception as e:
            logging.error(f"Failed to initialize FileProcessor: {e}")
            messagebox.showerror("Initialization Error", "Failed to initialize the file processor. Please check the logs for more details.")
            return
        
        # Process all existing files first
        try:
            count = file_processor.process_all()
            self.update_file_count(count)
            self.log_message(f"Successfully moved {count} existing files/folders.", logging.INFO)
        except Exception as e:
            self.log_message(f"Error processing existing files: {e}", logging.ERROR)
        
        # Create and start monitor
        try:
            directory_monitor = DirectoryMonitor(
                processor=file_processor,
                poll_interval=1.0  # Default 1 second interval
            )
            
            if directory_monitor.start():
                self.monitor = directory_monitor
                self.processor = file_processor
                self.monitoring = True
                
                self.log_message(f"Started monitoring {os.path.normpath(source)} for changes.")
            else:
                self.log_message("Failed to start monitoring.", logging.ERROR)
        except Exception as e:
            self.log_message(f"Error starting monitor: {e}", logging.ERROR)
    
    def stop_monitoring(self):
        """
        Stop monitoring files in the source directory.
        
        This method stops the directory monitor and updates the monitoring state.
        """
        if self.monitor:
            self.monitor.stop()
            self.monitor = None
            self.processor = None
            self.monitoring = False
            self.log_message("Stopped monitoring.")
    
    def update_file_count(self, count=None):
        """
        Update the file count in the status bar.
        
        Args:
            count (int, optional): Number of files processed
        """
        if count is not None:
            self.file_count_var.set(f"Files: {count}")
    
    def log_message(self, message, level=logging.INFO):
        """
        Log a message to both the log file and GUI.
        
        Args:
            message (str): The message to log
            level (int, optional): Logging level
        """
        logging.log(level, message)
    
    def clear_log(self):
        """
        Clear the log display in the GUI.
        
        This method removes all text from the log display widget.
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def save_log(self):
        """
        Save log contents to a file.
        
        This method opens a file save dialog and writes the log display
        contents to the selected file.
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Log"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Log saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save log: {e}")
    
    def save_settings(self):
        """
        Save current settings to a file.
        
        This method saves the current source, destination, and other
        settings to a JSON file for later use.
        """
        # Ensure directory exists
        try:
            os.makedirs(APP_DATA_DIR, exist_ok=True)
            
            settings = {
                'source': self.source_var.get(),
                'destination': self.dest_var.get(),
                'conflict_mode': self.conflict_mode_var.get(),
                'preserve_timestamps': self.preserve_timestamps_var.get(),
                'confirm_deletions': self.confirm_deletions_var.get(),
                'recursive_monitoring': self.recursive_monitoring_var.get(),
                'processing_delay': self.processing_delay_var.get()
            }
            
            # Use a temporary file for atomic write
            temp_file = f"{SETTINGS_FILE}.tmp"
            try:
                with open(temp_file, 'w') as f:
                    json.dump(settings, f, indent=4)
                
                # On Windows, we need to remove the destination file first
                if os.path.exists(SETTINGS_FILE):
                    os.remove(SETTINGS_FILE)
                    
                # Rename temp file to the real settings file
                os.rename(temp_file, SETTINGS_FILE)
                
                self.log_message("Settings saved successfully.")
                return True
            except Exception as e:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                self.log_message(f"Error saving settings: {e}", logging.ERROR)
                return False
                
        except Exception as e:
            self.log_message(f"Error preparing settings directory: {e}", logging.ERROR)
            return False
    
    def load_settings(self):
        """
        Load settings from a file.
        
        This method loads previously saved settings from a JSON file
        and applies them to the current instance. It also validates
        that directories exist and creates them if necessary.
        """
        if not os.path.exists(SETTINGS_FILE):
            self.log_message("No saved settings found. Using defaults.")
            # If using defaults, make sure the default directories exist
            self._ensure_directories_exist(self.source_var.get(), self.dest_var.get())
            return
        
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
            
            source_dir = settings.get('source', '')
            dest_dir = settings.get('destination', '')
            
            # Apply settings
            if source_dir:
                self.source_var.set(source_dir)
            
            if dest_dir:
                self.dest_var.set(dest_dir)
            
            # Load new settings
            if 'conflict_mode' in settings:
                self.conflict_mode_var.set(settings['conflict_mode'])
            
            if 'preserve_timestamps' in settings:
                self.preserve_timestamps_var.set(settings['preserve_timestamps'])
            
            if 'confirm_deletions' in settings:
                self.confirm_deletions_var.set(settings['confirm_deletions'])
            
            if 'recursive_monitoring' in settings:
                self.recursive_monitoring_var.set(settings['recursive_monitoring'])
            
            if 'processing_delay' in settings:
                self.processing_delay_var.set(settings['processing_delay'])
            
            # Validate that directories exist
            self._ensure_directories_exist(source_dir, dest_dir)
            
            self.log_message("Settings loaded successfully.")
        except Exception as e:
            self.log_message(f"Error loading settings: {e}", logging.ERROR)
    
    def _ensure_directories_exist(self, source_dir, dest_dir):
        """
        Ensure the specified directories exist, creating them if needed.
        
        Args:
            source_dir (str): Path to the source directory
            dest_dir (str): Path to the destination directory
            
        Returns:
            bool: True if both directories exist after this method, False otherwise
        """
        # Ensure source directory exists
        if not os.path.exists(source_dir):
            try:
                os.makedirs(source_dir)
                self.log_message(f"Created source directory: {os.path.normpath(source_dir)}")
            except Exception as e:
                self.log_message(f"Failed to create source directory: {e}", logging.WARNING)
                return False
                
        # Ensure destination directory exists
        if not os.path.exists(dest_dir):
            try:
                os.makedirs(dest_dir)
                self.log_message(f"Created destination directory: {os.path.normpath(dest_dir)}")
            except Exception as e:
                self.log_message(f"Failed to create destination directory: {e}", logging.WARNING)
                return False
                
        return True
    
    def update_log_display(self):
        """
        Update the log display with new messages from the queue.
        
        This method processes any pending log records in the queue
        and adds them to the log display widget.
        """
        while True:
            try:
                record = log_queue.get_nowait()
                self.display_log_record(record)
            except queue.Empty:
                break
        
        # Schedule this method to run again after 100ms
        self.root.after(100, self.update_log_display)
    
    def display_log_record(self, record):
        """
        Display a log record in the text widget.
        
        Args:
            record (LogRecord): The log record to display
        """
        msg = self.format_log_record(record)
        
        # Update text widget
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)  # Scroll to the bottom
        self.log_text.config(state=tk.DISABLED)
    
    def format_log_record(self, record):
        """
        Format a log record for display.
        
        Args:
            record (LogRecord): The log record to format
            
        Returns:
            str: Formatted log message
        """
        return f"{record.asctime} - {record.getMessage()}"
    
    def on_closing(self):
        """
        Handle window closing event.
        
        This method checks if monitoring is active before closing
        and prompts the user for confirmation if needed.
        It also saves current settings before exiting.
        """
        # Always save settings before closing
        self.save_settings()
        
        if self.monitoring:
            if messagebox.askyesno("Confirm Exit", "File monitoring is active. Do you want to exit anyway?"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()

class CreateToolTip:
    """
    Create a tooltip for a given widget.
    
    This utility class provides a tooltip popup when hovering over
    a widget with additional information.
    
    Attributes:
        widget (Widget): The widget to attach the tooltip to
        text (str): The tooltip text to display
        tooltip (Toplevel): The tooltip window (when visible)
    """
    
    def __init__(self, widget, text):
        """
        Initialize the tooltip.
        
        Args:
            widget (Widget): The widget to attach the tooltip to
            text (str): The tooltip text to display
        """
        self.widget = widget
        self.text = text
        self.tooltip = None
        
        # Bind events
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
    
    def enter(self, event=None):
        """
        Display the tooltip when the mouse enters the widget.
        
        Args:
            event (Event, optional): The mouse event
        """
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()
    
    def leave(self, event=None):
        """Remove the tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def run_gui():
    """
    Main entry point for the FilesMover graphical user interface.
    
    This function creates the Tkinter root window, initializes the GUI,
    and starts the main event loop.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        # Create main window
        root = tk.Tk()
        root.title("FilesMover")
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   "resources", "icons", "file_mover.ico")
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except Exception:
            # Skip icon if unavailable
            pass
        
        # Set default window size (80% of screen)
        width = root.winfo_screenwidth() * 0.8
        height = root.winfo_screenheight() * 0.8
        root.geometry(f"{int(width)}x{int(height)}")
        
        # Create application
        app = FileMoverGUI(root)
        
        # Start the main loop
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error starting GUI: {str(e)}")
        return 1

# For backward compatibility
main = run_gui

if __name__ == "__main__":
    sys.exit(run_gui()) 