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
from .core import FileProcessor

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
        activity_tracking_var (BooleanVar): Whether activity tracking is enabled
        inactive_threshold_var (DoubleVar): Threshold in days for inactivity
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
        
        # Initialize variables
        self.source_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Desktop', 'Source'))
        self.dest_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Desktop', 'Dest'))
        self.status_var = tk.StringVar(value="Ready")
        self.file_count_var = tk.StringVar(value="Files: 0")
        self.activity_tracking_var = tk.BooleanVar(value=False)
        self.inactive_threshold_var = tk.DoubleVar(value=7.0)
        
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
        # Activity tracking settings
        activity_frame = ttk.LabelFrame(parent, text="Activity Tracking", padding="10")
        activity_frame.pack(fill=tk.X, pady=5)
        
        activity_cb = ttk.Checkbutton(
            activity_frame, 
            text="Enable activity-based file organization", 
            variable=self.activity_tracking_var
        )
        activity_cb.pack(anchor=tk.W, pady=5)
        
        # Add tooltip to the activity tracking checkbox
        CreateToolTip(
            activity_cb, 
            "When enabled, files that haven't been accessed for the specified period\n"
            "will be moved to a special folder and restored when accessed."
        )
        
        # Threshold settings
        threshold_frame = ttk.Frame(activity_frame)
        threshold_frame.pack(fill=tk.X, pady=5)
        
        threshold_label = ttk.Label(threshold_frame, text="Inactivity threshold (days):")
        threshold_label.pack(side=tk.LEFT, padx=5)
        
        threshold_entry = ttk.Entry(threshold_frame, textvariable=self.inactive_threshold_var, width=10)
        threshold_entry.pack(side=tk.LEFT, padx=5)
        
        # Settings buttons
        settings_button_frame = ttk.Frame(parent)
        settings_button_frame.pack(fill=tk.X, pady=15)
        
        save_settings_button = ttk.Button(settings_button_frame, text="Save Settings", command=self.save_settings)
        save_settings_button.pack(side=tk.RIGHT, padx=5)
    
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

Activity Tracking:
When enabled, files that haven't been accessed for the specified threshold 
will be moved to a special "_inactive_files" folder. If an inactive file is 
accessed, it will automatically be moved back to its original location.

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
            self.log_message(f"Source directory set to: {directory}")
    
    def browse_destination(self):
        """
        Open a directory selection dialog for the destination directory.
        
        This method displays a directory browser dialog to select the
        destination directory and updates the corresponding variable.
        """
        directory = filedialog.askdirectory(initialdir=self.dest_var.get())
        if directory:
            self.dest_var.set(directory)
            self.log_message(f"Destination directory set to: {directory}")
    
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
        
        self.log_message(f"Moving all files from {source} to {destination}...")
        self.status_var.set("Processing files...")
        
        # Create a processor for one-time use
        processor = FileProcessor(
            source=source,
            destination=destination,
            activity_tracking=self.activity_tracking_var.get(),
            inactivity_threshold=self.inactive_threshold_var.get() * 24 * 60 * 60
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
                self.log_message(f"Created source directory: {source}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create source directory: {e}")
                return False
        
        # Check if destination directory exists or create it
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                self.log_message(f"Created destination directory: {destination}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create destination directory: {e}")
                return False
        
        return True
    
    def start_monitoring(self):
        """
        Start monitoring files in the source directory.
        
        This method creates a FileProcessor instance and starts monitoring
        the source directory for file changes.
        """
        source = self.source_var.get()
        destination = self.dest_var.get()
        
        # First move all existing files
        self.log_message("First moving all existing files before starting monitoring...")
        
        # Create the file processor
        self.processor = FileProcessor(
            source=source,
            destination=destination,
            activity_tracking=self.activity_tracking_var.get(),
            inactivity_threshold=self.inactive_threshold_var.get() * 24 * 60 * 60
        )
        
        # Process all existing files first
        try:
            count = self.processor.process_all()
            self.update_file_count(count)
            self.log_message(f"Successfully moved {count} existing files/folders.", logging.INFO)
        except Exception as e:
            self.log_message(f"Error processing existing files: {e}", logging.ERROR)
        
        # Start monitoring
        self.processor.start_monitoring()
        self.monitoring = True
        
        self.log_message(f"Started monitoring {source} for changes.")
    
    def stop_monitoring(self):
        """
        Stop monitoring files in the source directory.
        
        This method stops the file processor and updates the monitoring state.
        """
        if self.processor:
            self.processor.stop_monitoring()
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
        
        This method saves the current source, destination, and activity
        tracking settings to a JSON file for later use.
        """
        # Ensure directory exists
        os.makedirs(APP_DATA_DIR, exist_ok=True)
        
        settings = {
            'source': self.source_var.get(),
            'destination': self.dest_var.get(),
            'activity_tracking': self.activity_tracking_var.get(),
            'inactive_threshold': self.inactive_threshold_var.get()
        }
        
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
            
            self.log_message("Settings saved successfully.")
        except Exception as e:
            self.log_message(f"Error saving settings: {e}", logging.ERROR)
    
    def load_settings(self):
        """
        Load settings from a file.
        
        This method loads previously saved settings from a JSON file
        and applies them to the current instance.
        """
        if not os.path.exists(SETTINGS_FILE):
            self.log_message("No saved settings found. Using defaults.")
            return
        
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
            
            # Apply settings
            if 'source' in settings:
                self.source_var.set(settings['source'])
            
            if 'destination' in settings:
                self.dest_var.set(settings['destination'])
            
            if 'activity_tracking' in settings:
                self.activity_tracking_var.set(settings['activity_tracking'])
            
            if 'inactive_threshold' in settings:
                self.inactive_threshold_var.set(settings['inactive_threshold'])
            
            self.log_message("Settings loaded successfully.")
        except Exception as e:
            self.log_message(f"Error loading settings: {e}", logging.ERROR)
    
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
        """
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

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = FileMoverGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 