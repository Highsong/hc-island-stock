#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner for Stock Analysis System
Provides easy access to run different categories of tests
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_demos():
    """Run all demo scripts"""
    print("Running Demo Scripts...")
    print("=" * 50)

    demo_dir = Path("demos")
    demo_files = list(demo_dir.glob("demo_*.py"))

    if not demo_files:
        print("No demo files found")
        return

    for demo_file in demo_files:
        print(f"\nRunning {demo_file.name}...")
        print("-" * 30)
        try:
            result = subprocess.run([sys.executable, str(demo_file)],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✓ {demo_file.name} completed successfully")
                if result.stdout:
                    print("Output:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
            else:
                print(f"✗ {demo_file.name} failed")
                print("Error:", result.stderr)
        except subprocess.TimeoutExpired:
            print(f"⚠ {demo_file.name} timed out (60s)")
        except Exception as e:
            print(f"✗ {demo_file.name} error: {e}")

def run_unit_tests():
    """Run unit tests"""
    print("Running Unit Tests...")
    print("=" * 50)

    unit_dir = Path("unit")
    test_files = list(unit_dir.glob("test_*.py"))

    if not test_files:
        print("No unit test files found")
        return

    for test_file in test_files:
        print(f"\nRunning {test_file.name}...")
        try:
            result = subprocess.run([sys.executable, str(test_file)],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✓ {test_file.name} passed")
            else:
                print(f"✗ {test_file.name} failed")
                print("Error:", result.stderr)
        except subprocess.TimeoutExpired:
            print(f"⚠ {test_file.name} timed out (30s)")
        except Exception as e:
            print(f"✗ {test_file.name} error: {e}")

def run_integration_tests():
    """Run integration tests"""
    print("Running Integration Tests...")
    print("=" * 50)

    integration_dir = Path("integration")
    test_files = list(integration_dir.glob("test_*.py"))

    if not test_files:
        print("No integration test files found")
        return

    for test_file in test_files:
        print(f"\nRunning {test_file.name}...")
        try:
            result = subprocess.run([sys.executable, str(test_file)],
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"✓ {test_file.name} passed")
            else:
                print(f"✗ {test_file.name} failed")
                print("Error:", result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
        except subprocess.TimeoutExpired:
            print(f"⚠ {test_file.name} timed out (120s)")
        except Exception as e:
            print(f"✗ {test_file.name} error: {e}")

def run_debug_tests():
    """Run debug tests"""
    print("Running Debug Tests...")
    print("=" * 50)

    debug_dir = Path("debug")
    test_files = list(debug_dir.glob("test_*.py"))

    if not test_files:
        print("No debug test files found")
        return

    for test_file in test_files:
        print(f"\nRunning {test_file.name}...")
        try:
            result = subprocess.run([sys.executable, str(test_file)],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✓ {test_file.name} completed")
            else:
                print(f"✗ {test_file.name} failed")
                print("Error:", result.stderr)
        except subprocess.TimeoutExpired:
            print(f"⚠ {test_file.name} timed out (60s)")
        except Exception as e:
            print(f"✗ {test_file.name} error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Run Stock Analysis System tests')
    parser.add_argument('--category', choices=['demos', 'unit', 'integration', 'debug', 'all'],
                       default='all', help='Test category to run (default: all)')

    args = parser.parse_args()

    # Change to test directory
    os.chdir(Path(__file__).parent)

    print(f"Stock Analysis System Test Runner")
    print(f"Category: {args.category}")
    print("=" * 60)

    if args.category == 'all':
        run_demos()
        print("\n" + "=" * 60)
        run_unit_tests()
        print("\n" + "=" * 60)
        run_integration_tests()
        print("\n" + "=" * 60)
        run_debug_tests()
    elif args.category == 'demos':
        run_demos()
    elif args.category == 'unit':
        run_unit_tests()
    elif args.category == 'integration':
        run_integration_tests()
    elif args.category == 'debug':
        run_debug_tests()

    print("\n" + "=" * 60)
    print("Test execution completed!")

if __name__ == "__main__":
    main()