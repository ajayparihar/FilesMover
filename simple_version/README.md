# FilesMover Simple

A simplified version of FilesMover that uses only Python and its standard libraries. This utility monitors a source directory and moves files to a destination directory.

## Features

- **Simple File Moving**: Automatically move files from one directory to another
- **Directory Monitoring**: Watch for new files and move them when they're stable
- **Conflict Resolution**: Choose how to handle file conflicts (rename, overwrite, skip)
- **Preservation**: Option to preserve file timestamps during moves
- **Recursive Operation**: Process files in subdirectories
- **One-time Processing**: Option to process existing files once and exit
- **Pure Python**: Uses only Python standard libraries, no external dependencies

## Usage

You can run the utility directly:

```
python simple_version/files_mover_simple.py [options]
```

Or use the provided launcher script:

```
python run_simple.py [options]
```

### Command Line Options

- `-s, --source`: Source directory path (default: ~/Desktop/Source)
- `-d, --destination`: Destination directory path (default: ~/Desktop/Dest)
- `-c, --conflict`: How to handle file conflicts: rename, overwrite, skip (default: rename)
- `-p, --preserve-timestamps`: Preserve file creation/modification times (default: True)
- `-r, --recursive`: Process subdirectories recursively (default: True)
- `-i, --interval`: Poll interval in seconds (default: 1.0)
- `-a, --min-age`: Minimum file age in seconds before processing (default: 0.5)
- `-o, --one-time`: Process existing files once and exit
- `-v, --verbose`: Enable verbose logging

## Example

Process all files in Downloads folder and move them to an organized folder:

```
python run_simple.py -s ~/Downloads -d ~/Documents/Organized -o
```

Monitor Desktop for new files and move them to a backup folder:

```
python run_simple.py -s ~/Desktop -d ~/Backup
```

## Requirements

- Python 3.7 or higher
- No external dependencies - uses only Python standard libraries 