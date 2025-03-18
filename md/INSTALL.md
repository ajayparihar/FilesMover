# FilesMover Installation Guide

This document provides detailed instructions for installing and setting up the FilesMover application.

**Version:** 0.2.0  
**Developer:** Bheb Developer

## Prerequisites

Before installing FilesMover, ensure you have the following:

- **Python 3.6 or higher** - The application is written in Python and requires version 3.6 or later
- **Administrative privileges** (for creating desktop shortcuts and application data directories)

## Installation Methods

There are two ways to install FilesMover:

### 1. Using the Installation Script (Recommended)

The easiest way to install FilesMover is to use the included installation script:

1. Open a command prompt or terminal
2. Navigate to the FilesMover directory
3. Run the installation script:

   ```
   cd scripts
   install.bat
   ```

The script will:
- Check for Python installation
- Install required packages from requirements.txt
- Optionally create a desktop shortcut
- Set up application data directories

### 2. Manual Installation

If you prefer to install manually, follow these steps:

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Create application data directory:
   ```python
   import os
   app_data_dir = os.path.join(os.path.expanduser("~"), ".file_mover", "logs")
   os.makedirs(app_data_dir, exist_ok=True)
   ```

3. (Optional) Run setup.py to create a desktop shortcut:
   ```
   python setup.py
   ```

## Verifying Installation

To verify that FilesMover is correctly installed:

1. Run the application:
   ```
   scripts\run_file_mover.bat
   ```

2. The application GUI should appear, allowing you to set source and destination directories

## Troubleshooting

### Common Issues

1. **Python not found**
   - Ensure Python is installed and added to your system PATH
   - Try running `python --version` in a command prompt to verify

2. **Package installation fails**
   - Try running pip with elevated privileges: `pip install -r requirements.txt --user`
   - Check your internet connection
   - Ensure pip is up to date: `python -m pip install --upgrade pip`

3. **Application won't start**
   - Check that all dependencies were properly installed
   - Try running in CLI mode to see any error messages: `scripts\run_file_mover.bat --cli`

## Uninstallation

To uninstall FilesMover:

1. Delete the FilesMover directory
2. Remove the application data directory:
   ```
   %USERPROFILE%\.file_mover
   ```
3. Remove any desktop shortcuts

## Additional Resources

- See README.md for usage instructions
- Check the application's Help tab for more information 