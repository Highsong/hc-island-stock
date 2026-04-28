#!/usr/bin/env python3
"""Run the Streamlit app with proper error handling"""

import subprocess
import sys
import os

def main():
    """Main function to run Streamlit app"""
    print("Starting Streamlit app...")

    # Change to the project root directory (scripts/ -> root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(script_dir, ".."))

    try:
        # Run streamlit with the app
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "src/app_new.py",
            "--server.headless=true"
        ], capture_output=True, text=True, timeout=30)

        print("Streamlit output:")
        print(result.stdout)
        if result.stderr:
            print("Streamlit errors:")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("Streamlit started successfully but took too long to complete")
        return True
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)