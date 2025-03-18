import os
import time
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import queue
import json
from core_file_mover import start_monitoring, process_all_items, move_item

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

class FileMoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Mover")
        self.root.geometry("800x600")
        self.root.minsize(650, 500)
        
        # Initialize variables
        self.source_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Desktop', 'Source'))
        self.dest_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Desktop', 'Dest'))
        self.status_var = tk.StringVar(value="Ready")
        self.file_count_var = tk.StringVar(value="Files: 0")
        self.monitoring = False
        self.observer = None
        self.auto_start = tk.BooleanVar(value=False)
        self.auto_create_dirs = tk.BooleanVar(value=True)
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        
        # Load settings
        self.load_settings()
        
        # Update log display periodically
        self.update_log_display()
        
        # Start monitoring if auto-start is enabled
        if self.auto_start.get():
            self.start_monitoring()
            
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        # Create and configure ttk styles
        style = ttk.Style()
        
        # Configure button styles
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Secondary.TButton', font=('Segoe UI', 10))
        
        # Configure frame styles
        style.configure('Card.TFrame', background='#f5f5f5', relief='raised')
        
        # Configure label styles
        style.configure('Status.TLabel', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'))
        
        # Configure entry styles
        style.configure('Path.TEntry', font=('Segoe UI', 9))
        
    def create_widgets(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create tabs
        main_tab = ttk.Frame(notebook, padding=10)
        settings_tab = ttk.Frame(notebook, padding=10)
        help_tab = ttk.Frame(notebook, padding=10)
        
        notebook.add(main_tab, text="Main")
        notebook.add(settings_tab, text="Settings")
        notebook.add(help_tab, text="Help")
        
        # Main Tab
        self.create_main_tab(main_tab)
        
        # Settings Tab
        self.create_settings_tab(settings_tab)
        
        # Help Tab
        self.create_help_tab(help_tab)
        
        # Status bar
        status_bar = ttk.Frame(main_frame)
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
        status_label = ttk.Label(status_bar, textvariable=self.status_var, style='Status.TLabel')
        status_label.pack(side=tk.LEFT)
        
        file_count_label = ttk.Label(status_bar, textvariable=self.file_count_var, style='Status.TLabel')
        file_count_label.pack(side=tk.RIGHT)
        
    def create_main_tab(self, parent):
        # Directory frame
        dir_frame = ttk.LabelFrame(parent, text="Directories", padding=10)
        dir_frame.pack(fill=tk.X, pady=5)
        
        # Source directory
        ttk.Label(dir_frame, text="Source Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        source_entry = ttk.Entry(dir_frame, textvariable=self.source_var, width=50, style='Path.TEntry')
        source_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        browse_source_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_source)
        browse_source_btn.grid(row=0, column=2, pady=5)
        
        # Destination directory
        ttk.Label(dir_frame, text="Destination Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        dest_entry = ttk.Entry(dir_frame, textvariable=self.dest_var, width=50, style='Path.TEntry')
        dest_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        browse_dest_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_destination)
        browse_dest_btn.grid(row=1, column=2, pady=5)
        
        dir_frame.columnconfigure(1, weight=1)
        
        # Create tooltips for the directory fields
        CreateToolTip(source_entry, "The directory to monitor for new files")
        CreateToolTip(dest_entry, "The directory where files will be moved to")
        
        # Action frame
        action_frame = ttk.Frame(parent, padding=5)
        action_frame.pack(fill=tk.X, pady=10)
        
        # Start/Stop monitoring button
        self.monitor_btn = ttk.Button(
            action_frame, 
            text="Start Monitoring", 
            command=self.toggle_monitoring,
            style='Primary.TButton',
            width=20
        )
        self.monitor_btn.pack(side=tk.LEFT, padx=5)
        
        # Move All button
        move_all_btn = ttk.Button(
            action_frame, 
            text="Move All Items Now", 
            command=self.move_all_items,
            style='Secondary.TButton',
            width=20
        )
        move_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Create tooltips for the buttons
        CreateToolTip(self.monitor_btn, "Start or stop automatic file monitoring")
        CreateToolTip(move_all_btn, "Move all existing files in the source directory now")
        
        # Log frame
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Log buttons frame
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        clear_log_btn = ttk.Button(log_btn_frame, text="Clear Log", command=self.clear_log)
        clear_log_btn.pack(side=tk.LEFT, padx=5)
        
        save_log_btn = ttk.Button(log_btn_frame, text="Save Log", command=self.save_log)
        save_log_btn.pack(side=tk.LEFT, padx=5)
        
    def create_settings_tab(self, parent):
        settings_frame = ttk.Frame(parent, padding=5)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Auto-start monitoring
        auto_start_check = ttk.Checkbutton(
            settings_frame, 
            text="Auto-start monitoring when application opens", 
            variable=self.auto_start,
            command=self.save_settings
        )
        auto_start_check.pack(anchor=tk.W, pady=5)
        
        # Auto-create directories
        auto_create_dirs_check = ttk.Checkbutton(
            settings_frame, 
            text="Automatically create directories if they don't exist", 
            variable=self.auto_create_dirs,
            command=self.save_settings
        )
        auto_create_dirs_check.pack(anchor=tk.W, pady=5)
        
        # Add tooltips
        CreateToolTip(auto_start_check, "Start monitoring automatically when you open the app")
        CreateToolTip(auto_create_dirs_check, "Create source and destination directories if they don't exist")
        
    def create_help_tab(self, parent):
        help_frame = ttk.Frame(parent, padding=5)
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        # Help text
        help_text = scrolledtext.ScrolledText(help_frame, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert help content
        help_content = """
        # File Mover Help
        
        ## Quick Start Guide
        
        1. Set your source directory (the folder to monitor)
        2. Set your destination directory (where files will be moved to)
        3. Click "Start Monitoring" to begin automatic file monitoring
        4. Any files added to the source directory will be moved to the destination
        
        ## Features
        
        - **Real-time Monitoring**: Files are moved as soon as they appear in the source directory
        - **Manual Processing**: Use "Move All Items Now" to process existing files
        - **Directory Preservation**: Maintains folder structure when moving files
        - **Activity Logging**: All operations are logged with timestamps
        
        ## Tips and Tricks
        
        - You can set the app to auto-start monitoring in the Settings tab
        - If the destination already has a file with the same name, it will be overwritten
        - Check the Activity Log for details about each operation
        - Save the log to keep a record of file movements
        
        ## Troubleshooting
        
        - If files aren't moving, ensure both directories exist and are accessible
        - Files that are currently in use by other applications may not move
        - Check the Activity Log for any error messages
        """
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
        
    def browse_source(self):
        """Open dialog to browse for source directory"""
        folder_path = filedialog.askdirectory(
            title="Select Source Directory",
            initialdir=self.source_var.get()
        )
        if folder_path:
            self.source_var.set(folder_path)
            self.save_settings()
            
    def browse_destination(self):
        """Open dialog to browse for destination directory"""
        folder_path = filedialog.askdirectory(
            title="Select Destination Directory",
            initialdir=self.dest_var.get()
        )
        if folder_path:
            self.dest_var.set(folder_path)
            self.save_settings()
    
    def toggle_monitoring(self):
        """Toggle monitoring state (start/stop)"""
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def move_all_items(self):
        """Process all items in the source directory"""
        source = self.source_var.get()
        destination = self.dest_var.get()
        
        if not self.validate_directories():
            return
        
        # Update UI
        self.status_var.set("Processing all items...")
        self.root.update_idletasks()
        
        # Process in a separate thread to avoid freezing the UI
        thread = threading.Thread(
            target=self.run_move_all_with_progress,
            args=(source, destination),
            daemon=True
        )
        thread.start()
    
    def run_move_all_with_progress(self, source, destination):
        """Run the move all operation with progress updates"""
        try:
            count = process_all_items(source, destination)
            self.update_file_count(count)
            self.log_message(f"Processed {count} items")
            self.status_var.set("Ready")
        except Exception as e:
            self.log_message(f"Error processing items: {e}", logging.ERROR)
            self.status_var.set("Error")
    
    def validate_directories(self):
        """Validate source and destination directories"""
        source = self.source_var.get()
        destination = self.dest_var.get()
        
        # Check if paths are provided
        if not source or not destination:
            messagebox.showwarning(
                "Missing Directory", 
                "Please provide both source and destination directories."
            )
            return False
        
        # Check if source exists
        if not os.path.exists(source):
            if self.auto_create_dirs.get():
                try:
                    os.makedirs(source)
                    self.log_message(f"Created source directory: {source}")
                except Exception as e:
                    messagebox.showerror(
                        "Error", 
                        f"Could not create source directory: {e}"
                    )
                    return False
            else:
                messagebox.showerror(
                    "Directory Not Found", 
                    f"Source directory does not exist: {source}\n\nEnable auto-create directories in Settings or create it manually."
                )
                return False
        
        # Check if destination exists
        if not os.path.exists(destination):
            if self.auto_create_dirs.get():
                try:
                    os.makedirs(destination)
                    self.log_message(f"Created destination directory: {destination}")
                except Exception as e:
                    messagebox.showerror(
                        "Error", 
                        f"Could not create destination directory: {e}"
                    )
                    return False
            else:
                messagebox.showerror(
                    "Directory Not Found", 
                    f"Destination directory does not exist: {destination}\n\nEnable auto-create directories in Settings or create it manually."
                )
                return False
        
        return True
    
    def start_monitoring(self):
        """Start monitoring the source directory"""
        if not self.validate_directories():
            return
        
        source = self.source_var.get()
        destination = self.dest_var.get()
        
        # Start monitoring in a new thread
        self.observer, handler = start_monitoring(source, destination)
        
        if not self.observer:
            messagebox.showerror("Error", "Failed to start monitoring")
            return
        
        self.monitoring = True
        self.monitor_btn.config(text="Stop Monitoring")
        self.status_var.set("Monitoring active")
        self.log_message(f"Started monitoring {source} for changes")
    
    def stop_monitoring(self):
        """Stop monitoring the source directory"""
        if self.observer:
            self.observer.stop()
            # Wait for the observer to stop
            self.observer.join()
            self.observer = None
            
        self.monitoring = False
        self.monitor_btn.config(text="Start Monitoring")
        self.status_var.set("Ready")
        self.log_message("Stopped monitoring")
    
    def update_file_count(self, count=None):
        """Update the file count display"""
        if count is not None:
            self.file_count_var.set(f"Files: {count}")
        else:
            self.file_count_var.set("Files: -")
    
    def log_message(self, message, level=logging.INFO):
        """Add a message to the log with the specified level"""
        logging.log(level, message)
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def save_log(self):
        """Save log contents to a file"""
        # Generate default filename with timestamp
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        default_filename = f"file_mover_log_{timestamp}.log"
        default_path = os.path.join(os.path.expanduser('~'), '.file_mover', 'logs', default_filename)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=default_filename,
            initialdir=os.path.dirname(default_path)
        )
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Log saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        # Create settings directory if it doesn't exist
        if not os.path.exists(APP_DATA_DIR):
            os.makedirs(APP_DATA_DIR)
        
        settings = {
            'source_dir': self.source_var.get(),
            'dest_dir': self.dest_var.get(),
            'auto_start': self.auto_start.get(),
            'auto_create_dirs': self.auto_create_dirs.get()
        }
        
        try:
            with open(SETTINGS_FILE, 'w') as file:
                json.dump(settings, file)
        except Exception as e:
            self.log_message(f"Error saving settings: {e}", logging.ERROR)
    
    def load_settings(self):
        """Load settings from file"""
        if not os.path.exists(SETTINGS_FILE):
            return
        
        try:
            with open(SETTINGS_FILE, 'r') as file:
                settings = json.load(file)
                
            if 'source_dir' in settings:
                self.source_var.set(settings['source_dir'])
            if 'dest_dir' in settings:
                self.dest_var.set(settings['dest_dir'])
            if 'auto_start' in settings:
                self.auto_start.set(settings['auto_start'])
            if 'auto_create_dirs' in settings:
                self.auto_create_dirs.set(settings['auto_create_dirs'])
                
        except Exception as e:
            self.log_message(f"Error loading settings: {e}", logging.ERROR)
    
    def update_log_display(self):
        """Update the log display with messages from the queue"""
        while True:
            try:
                # Get a log record from the queue, but don't block
                record = log_queue.get_nowait()
                
                # Format the log message
                formatted_msg = self.format_log_record(record)
                
                # Display the log message
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, formatted_msg + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
                
                # Mark the task as done
                log_queue.task_done()
            except queue.Empty:
                # No more items in the queue
                break
        
        # Schedule the next update
        self.root.after(100, self.update_log_display)
    
    def format_log_record(self, record):
        """Format a log record for display"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))
        
        # Color coding based on log level
        if record.levelno >= logging.ERROR:
            return f"{timestamp} - ERROR: {record.getMessage()}"
        elif record.levelno >= logging.WARNING:
            return f"{timestamp} - WARNING: {record.getMessage()}"
        else:
            return f"{timestamp} - {record.getMessage()}"
    
    def on_closing(self):
        """Handle window closing event"""
        if self.monitoring:
            self.stop_monitoring()
        
        # Save settings
        self.save_settings()
        
        # Close the window
        self.root.destroy()

class CreateToolTip:
    """
    Creates a tooltip for a given widget
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        
    def enter(self, event=None):
        # Display the tooltip
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create the tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, wraplength=250,
                         background="#ffffe0", relief="solid", borderwidth=1)
        label.pack(padx=2, pady=2)
    
    def leave(self, event=None):
        # Remove the tooltip
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def main():
    # Create the main window
    root = tk.Tk()
    
    # Create the GUI
    app = FileMoverGUI(root)
    
    # Set icon if available
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "file_mover_icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 