import subprocess
import sys
import os
import platform

def install_packages():
    """
    Install required packages from requirements.txt
    
    Returns:
        bool: True if installation was successful, False otherwise
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut to run the application"""
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        batch_file = os.path.join(script_dir, "run_file_mover.bat")
        
        if platform.system() == "Windows":
            # For Windows, create a shortcut (.lnk) file
            import winshell
            from win32com.client import Dispatch
            
            shortcut_path = os.path.join(desktop_path, "File Mover.lnk")
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = batch_file
            shortcut.WorkingDirectory = script_dir
            shortcut.IconLocation = os.path.join(script_dir, "file_mover_icon.ico")
            shortcut.save()
            return True
        else:
            # For Linux/Mac, create a shell script
            shortcut_path = os.path.join(desktop_path, "File Mover.sh")
            with open(shortcut_path, 'w') as f:
                f.write(f'#!/bin/sh\ncd "{script_dir}"\npython file_mover_gui.py\n')
            os.chmod(shortcut_path, 0o755)  # Make executable
            return True
    except Exception as e:
        print(f"Failed to create desktop shortcut: {e}")
        return False

def main():
    """Main installation function"""
    print("=" * 60)
    print("     File Mover - Installation Setup     ")
    print("=" * 60)
    print()
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"Using Python {python_version}")
    
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
        print("WARNING: Python 3.6 or higher is recommended")
        print(f"Current Python version is {python_version}")
        print()
    
    # Install required packages
    print("Installing required packages...")
    if install_packages():
        print("All required packages installed successfully!")
    else:
        print("Failed to install packages from requirements.txt")
        print("Please install them manually:")
        print("pip install -r requirements.txt")
    
    # Ask to create desktop shortcut
    print("\nWould you like to create a desktop shortcut? (y/n)")
    response = input().strip().lower()
    
    if response in ('y', 'yes'):
        try:
            # For Windows, we need pywin32 and winshell for shortcut creation
            if platform.system() == "Windows":
                for package in ["pywin32", "winshell"]:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                
                if create_desktop_shortcut():
                    print("Desktop shortcut created successfully!")
                else:
                    print("Failed to create desktop shortcut")
            else:
                if create_desktop_shortcut():
                    print("Desktop shortcut created successfully!")
                else:
                    print("Failed to create desktop shortcut")
        except Exception as e:
            print(f"Error creating shortcut: {e}")
    
    print("\nSetup completed!")
    print("\nTo run the application:")
    print("1. Double-click 'run_file_mover.bat' (Windows)")
    print("   OR")
    print("2. Run 'python file_mover_gui.py' for the GUI")
    print("3. Run 'python file_mover_cli.py --help' for CLI options")
    print("\nThank you for installing File Mover!")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 