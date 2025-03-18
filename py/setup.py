"""
FilesMover - Setup and Installation Script

This script handles the setup and installation of the FilesMover application.
It installs required packages, creates application directories, and optionally
creates a desktop shortcut.

Functions:
    install_packages: Install required packages from requirements.txt
    create_desktop_shortcut: Create a desktop shortcut for the application
    create_app_data_directory: Create directories for logs and settings
    run_setup: Run the complete setup process
"""

import subprocess
import sys
import os
import platform

def install_packages():
    """
    Install required packages from requirements.txt
    
    This function uses pip to install all packages listed in the requirements.txt
    file, which are necessary for the application to run.
    
    Returns:
        bool: True if installation was successful, False otherwise
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def create_desktop_shortcut():
    """
    Create a desktop shortcut to run the application
    
    This function creates a platform-specific shortcut on the user's desktop
    that can be used to launch the application. On Windows, it creates a .lnk file,
    and on Linux/macOS, it creates a shell script.
    
    Returns:
        bool: True if the shortcut was created successfully, False otherwise
    """
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        batch_file = os.path.join(script_dir, "run.bat")
        
        if platform.system() == "Windows":
            # For Windows, create a shortcut (.lnk) file
            import winshell
            from win32com.client import Dispatch
            
            shortcut_path = os.path.join(desktop_path, "FilesMover.lnk")
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = batch_file
            shortcut.WorkingDirectory = script_dir
            shortcut.IconLocation = os.path.join(script_dir, "scripts", "file_mover.ico")
            shortcut.Description = "FilesMover - Automatically move and organize files"
            shortcut.save()
            return True
        else:
            # For Linux/macOS, create a shell script
            shortcut_path = os.path.join(desktop_path, "FilesMover.sh")
            with open(shortcut_path, 'w') as f:
                f.write(f'#!/bin/bash\ncd "{script_dir}"\n./run.bat\n')
            os.chmod(shortcut_path, 0o755)
            return True
    except Exception as e:
        print(f"Error creating desktop shortcut: {e}")
        return False

def create_app_data_directory():
    """
    Create application data directory for logs and settings
    
    This function creates the necessary directories for storing application
    logs and settings in the user's home directory.
    
    Returns:
        bool: True if the directories were created successfully, False otherwise
    """
    try:
        app_data_dir = os.path.join(os.path.expanduser("~"), ".file_mover")
        logs_dir = os.path.join(app_data_dir, "logs")
        
        # Create directories if they don't exist
        os.makedirs(app_data_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
        
        print(f"Created application data directory: {app_data_dir}")
        return True
    except Exception as e:
        print(f"Error creating application data directory: {e}")
        return False

def run_setup():
    """
    Run the setup process
    
    This function orchestrates the complete setup process, including
    installing packages, creating application directories, and optionally
    creating a desktop shortcut based on user input.
    """
    print("="*50)
    print("FilesMover - Setup")
    print("="*50)
    print()
    
    # Step 1: Install required packages
    print("Step 1: Installing required packages...")
    if install_packages():
        print("✓ Packages installed successfully")
    else:
        print("✗ Failed to install packages")
        print("  Please run: pip install -r requirements.txt")
    print()
    
    # Step 2: Create application data directory
    print("Step 2: Creating application data directory...")
    if create_app_data_directory():
        print("✓ Application data directory created")
    else:
        print("✗ Failed to create application data directory")
    print()
    
    # Step 3: Create desktop shortcut (optional)
    create_shortcut = input("Would you like to create a desktop shortcut? (y/n): ").lower() == 'y'
    if create_shortcut:
        print("Step 3: Creating desktop shortcut...")
        if create_desktop_shortcut():
            print("✓ Desktop shortcut created")
        else:
            print("✗ Failed to create desktop shortcut")
    else:
        print("Skipping desktop shortcut creation")
    print()
    
    # Setup complete
    print("="*50)
    print("Setup complete!")
    print("="*50)
    print()
    print("You can now run the application using:")
    print(" - run.bat (from the application directory)")
    if create_shortcut:
        print(" - FilesMover shortcut (from your desktop)")
    print()
    print("Command-line usage:")
    print(" - scripts\\run_file_mover.bat --cli (for CLI mode)")
    print(" - scripts\\run_file_mover.bat (for GUI mode)")
    print()
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    run_setup() 