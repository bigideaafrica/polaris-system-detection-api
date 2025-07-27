#!/usr/bin/env python3
"""
🌟 Polaris System Detection API - Cleanup Script
Remove temporary files, cache, and build artifacts
"""

import os
import shutil
from pathlib import Path


def remove_directory(path):
    """Remove directory if it exists"""
    if path.exists() and path.is_dir():
        print(f"🗑️  Removing {path}")
        shutil.rmtree(path)
        return True
    return False


def remove_file(path):
    """Remove file if it exists"""
    if path.exists() and path.is_file():
        print(f"🗑️  Removing {path}")
        path.unlink()
        return True
    return False


def main():
    """Clean up project"""
    print("🌟 ================================")
    print("🌟  POLARIS CLEANUP SCRIPT")
    print("🌟 ================================")
    
    project_root = Path(".")
    removed_count = 0
    
    # Python cache directories
    cache_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "build",
        "develop-eggs",
        "dist",
        "downloads",
        "eggs",
        ".eggs",
        "lib",
        "lib64",
        "parts",
        "sdist",
        "var",
        "wheels",
        "*.egg-info",
        ".installed.cfg",
        "*.egg",
    ]
    
    # Find and remove Python cache
    for root, dirs, files in os.walk(project_root):
        root_path = Path(root)
        
        # Remove cache directories
        for dir_name in dirs[:]:  # Use slice to avoid modification during iteration
            if dir_name == "__pycache__":
                cache_path = root_path / dir_name
                if remove_directory(cache_path):
                    removed_count += 1
                dirs.remove(dir_name)  # Don't descend into removed directory
        
        # Remove cache files
        for file_name in files:
            if file_name.endswith(('.pyc', '.pyo', '.pyd')):
                file_path = root_path / file_name
                if remove_file(file_path):
                    removed_count += 1
    
    # Remove other temporary files
    temp_files = [
        ".coverage",
        "coverage.xml",
        "*.log",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
    ]
    
    for pattern in temp_files:
        if pattern.startswith("."):
            # Directory
            temp_path = project_root / pattern
            if remove_directory(temp_path):
                removed_count += 1
        else:
            # File pattern
            for file_path in project_root.glob(pattern):
                if remove_file(file_path):
                    removed_count += 1
    
    print(f"\n🌟 Cleanup completed! Removed {removed_count} items.")
    print("🌟 ================================")


if __name__ == "__main__":
    main() 