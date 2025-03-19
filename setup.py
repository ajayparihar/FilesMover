#!/usr/bin/env python3
"""
Setup script for FilesMover package.
"""

from setuptools import setup, find_packages
import os

# Get the long description from the README file
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get version from the package
version = {}
with open(os.path.join("src", "file_mover", "__init__.py")) as f:
    exec(f.read(), version)

setup(
    name="files-mover",
    version=version["__version__"],
    description="A utility for organizing and moving files automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=version["__author__"],
    author_email="example@example.com",
    url="https://github.com/example/files-mover",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "files-mover=file_mover.main:main",
            "files-mover-cli=file_mover.cli:run_cli",
            "files-mover-gui=file_mover.gui:run_gui",
        ],
    },
    install_requires=[],
    keywords="files, organization, utility, file management",
    project_urls={
        "Bug Reports": "https://github.com/example/files-mover/issues",
        "Source": "https://github.com/example/files-mover",
    },
) 