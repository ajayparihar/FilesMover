import os
import shutil
import time

source = r'C:\Users\ajays\OneDrive\Desktop\Source'
destination = r'C:\Users\ajays\OneDrive\Desktop\Dest'

def move_files():
    while True:
        # List all files and folders in the source directory
        for item in os.listdir(source):
            source_item = os.path.join(source, item)
            destination_item = os.path.join(destination, item)

            try:
                # Check if the destination already exists and delete it if it does
                if os.path.exists(destination_item):
                    if os.path.isfile(destination_item):
                        os.remove(destination_item)
                    elif os.path.isdir(destination_item):
                        shutil.rmtree(destination_item)
                # Check if it's a file or folder and move it
                if os.path.isfile(source_item):
                    shutil.move(source_item, destination_item)
                    print(f'Moved file: {source_item} -> {destination_item}')
                elif os.path.isdir(source_item):
                    shutil.move(source_item, destination_item)
                    print(f'Moved folder: {source_item} -> {destination_item}')
            except Exception as e:
                print(f'Error moving {source_item}: {e}')
        
        # Wait for a short period before checking again (e.g., 1 second)
        time.sleep(1)

if __name__ == "__main__":
    print(f"Monitoring {source} for new files/folders...")
    move_files()
