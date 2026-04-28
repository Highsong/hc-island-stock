#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock Analysis System Starter
Alternative to batch file for better cross-platform compatibility
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clear_cache():
    """Clear all cache files and temporary data"""
    print("=" * 60)
    print("CLEARING ALL CACHE AND TEMPORARY FILES")
    print("=" * 60)

    files_removed = 0
    dirs_removed = 0

    # Clear main cache directory
    cache_dir = Path("data/cache")
    if cache_dir.exists():
        print(f"Clearing {cache_dir}...")
        for file_path in cache_dir.glob("*"):
            try:
                if file_path.is_file():
                    file_path.unlink()
                    files_removed += 1
                    print(f"  [OK] Removed: {file_path.name}")
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    dirs_removed += 1
                    print(f"  [OK] Removed directory: {file_path.name}")
            except Exception as e:
                print(f"  [FAIL] Failed to remove {file_path}: {e}")
        print(f"  Cleared {cache_dir}")
    else:
        print(f"Cache directory {cache_dir} not found, creating...")
        cache_dir.mkdir(parents=True, exist_ok=True)

    # Clear processed data
    processed_dir = Path("data/processed_data")
    if processed_dir.exists():
        print(f"\nClearing {processed_dir}...")
        for file_path in processed_dir.glob("*"):
            try:
                if file_path.is_file():
                    file_path.unlink()
                    files_removed += 1
                    print(f"  [OK] Removed: {file_path.name}")
            except Exception as e:
                print(f"  [FAIL] Failed to remove {file_path}: {e}")
        print(f"  Cleared {processed_dir}")

    # Clear Python cache directories
    print(f"\nClearing Python cache directories...")
    for path in Path(".").rglob("__pycache__"):
        try:
            shutil.rmtree(path)
            dirs_removed += 1
            print(f"  [OK] Removed: {path}")
        except Exception as e:
            print(f"  [FAIL] Failed to remove {path}: {e}")

    # Clear .pyc files
    print(f"\nClearing .pyc files...")
    for path in Path(".").rglob("*.pyc"):
        try:
            path.unlink()
            files_removed += 1
        except Exception as e:
            print(f"  [FAIL] Failed to remove {path}: {e}")

    # Clear temporary files
    print(f"\nClearing temporary files...")
    temp_patterns = ["*.tmp", "*.temp"]
    for pattern in temp_patterns:
        for path in Path(".").glob(pattern):
            try:
                path.unlink()
                files_removed += 1
                print(f"  [OK] Removed: {path.name}")
            except Exception as e:
                print(f"  [FAIL] Failed to remove {path}: {e}")

    print(f"\n" + "=" * 60)
    print(f"CACHE CLEARING COMPLETED")
    print(f"Files removed: {files_removed}")
    print(f"Directories removed: {dirs_removed}")
    print(f"=" * 60)

def kill_existing_streamlit():
    """Kill any existing Streamlit processes"""
    print("Checking for existing Streamlit processes...")
    try:
        if sys.platform.startswith('win'):
            # Windows
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                capture_output=True, text=True
            )
            if 'streamlit' in result.stdout.lower():
                print("Found running Streamlit instance, closing it...")
                subprocess.run(
                    ['taskkill', '/F', '/FI', 'IMAGENAME eq python.exe', '/FI', 'WINDOWTITLE eq streamlit'],
                    capture_output=True
                )
                print("Closed old instance")
            else:
                print("No running Streamlit instance found")
        else:
            # Unix-like systems
            result = subprocess.run(
                ['ps', 'aux'], capture_output=True, text=True
            )
            if 'streamlit' in result.stdout.lower():
                print("Found running Streamlit instance, closing it...")
                subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
                print("Closed old instance")
            else:
                print("No running Streamlit instance found")
    except Exception as e:
        print(f"Error checking/killing processes: {e}")

def main():
    """Main function"""
    # 切换到项目根目录（scripts/ 的上级）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(script_dir, ".."))
    print("Starting Stock Analysis System")
    print("=" * 50)

    # Check for cache clear parameter
    clear_cache_flag = len(sys.argv) > 1 and sys.argv[1] == "--clear-cache"

    if clear_cache_flag:
        clear_cache()
        print()

    # Kill existing Streamlit processes
    kill_existing_streamlit()
    print()

    # Start the application
    print("Starting application...")
    print("Please open browser at: http://localhost:8501")
    print("Press Ctrl+C to stop application")
    print()

    try:
        subprocess.run(["streamlit", "run", "src/app_new.py"])
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()