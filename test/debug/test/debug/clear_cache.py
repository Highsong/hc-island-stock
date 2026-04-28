#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive cache clearing script
This script ensures all cached data is completely removed
"""

import os
import sys
import shutil
from pathlib import Path

def clear_all_cache():
    """Clear all cache files and directories"""
    print("=" * 60)
    print("CLEARING ALL CACHE AND TEMPORARY FILES")
    print("=" * 60)

    # Initialize counters
    files_removed = 0
    dirs_removed = 0

    # 1. Clear main cache directory
    cache_dir = Path("data/cache")
    if cache_dir.exists():
        print(f"\nClearing {cache_dir}...")
        for file_path in cache_dir.glob("*"):
            try:
                if file_path.is_file():
                    file_path.unlink()
                    files_removed += 1
                    print(f"  ✓ Removed: {file_path.name}")
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    dirs_removed += 1
                    print(f"  ✓ Removed directory: {file_path.name}")
            except Exception as e:
                print(f"  ✗ Failed to remove {file_path}: {e}")
        print(f"  Cleared {cache_dir}")
    else:
        print(f"\nCache directory {cache_dir} not found, creating...")
        cache_dir.mkdir(parents=True, exist_ok=True)

    # 2. Clear processed data
    processed_dir = Path("data/processed_data")
    if processed_dir.exists():
        print(f"\nClearing {processed_dir}...")
        for file_path in processed_dir.glob("*"):
            try:
                if file_path.is_file():
                    file_path.unlink()
                    files_removed += 1
                    print(f"  ✓ Removed: {file_path.name}")
            except Exception as e:
                print(f"  ✗ Failed to remove {file_path}: {e}")
        print(f"  Cleared {processed_dir}")

    # 3. Clear Python cache directories
    print(f"\nClearing Python cache directories...")
    for path in Path(".").rglob("__pycache__"):
        try:
            shutil.rmtree(path)
            dirs_removed += 1
            print(f"  ✓ Removed: {path}")
        except Exception as e:
            print(f"  ✗ Failed to remove {path}: {e}")

    # 4. Clear .pyc files
    print(f"\nClearing .pyc files...")
    for path in Path(".").rglob("*.pyc"):
        try:
            path.unlink()
            files_removed += 1
        except Exception as e:
            print(f"  ✗ Failed to remove {path}: {e}")

    # 5. Clear temporary files
    print(f"\nClearing temporary files...")
    temp_patterns = ["*.tmp", "*.temp", "*.log"]
    for pattern in temp_patterns:
        for path in Path(".").glob(pattern):
            try:
                path.unlink()
                files_removed += 1
                print(f"  ✓ Removed: {path.name}")
            except Exception as e:
                print(f"  ✗ Failed to remove {path}: {e}")

    # 6. Clear test debug cache if exists
    test_cache_dir = Path("test/debug/data/cache")
    if test_cache_dir.exists():
        print(f"\nClearing test debug cache...")
        for file_path in test_cache_dir.glob("*"):
            try:
                if file_path.is_file():
                    file_path.unlink()
                    files_removed += 1
                    print(f"  ✓ Removed: {file_path.name}")
            except Exception as e:
                print(f"  ✗ Failed to remove {file_path}: {e}")

    print(f"\n" + "=" * 60)
    print(f"CACHE CLEARING COMPLETED")
    print(f"Files removed: {files_removed}")
    print(f"Directories removed: {dirs_removed}")
    print(f"=" * 60)

    # Verify cache is cleared by trying to import and clear programmatically
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..', 'src'))
        from utils.cache_manager import cache_manager
        print(f"\nProgrammatic cache verification:")
        cache_manager.clear_all()
        print("  ✓ Programmatic cache clearing completed")
    except Exception as e:
        print(f"  ⚠ Programmatic cache clearing failed: {e}")

if __name__ == "__main__":
    clear_all_cache()
    print("\nCache clearing completed. Press Enter to exit...")
    input()