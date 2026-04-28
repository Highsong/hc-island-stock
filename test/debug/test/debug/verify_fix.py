#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the fix by checking the code changes"""

import re

def check_file_for_sample_data_calls():
    """Check if the stock_data_source.py file still has sample data calls"""
    file_path = "src/data_extraction/stock_data_source.py"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("=== Checking for sample data generation calls ===")

    # Check for _generate_sample_data calls
    sample_data_calls = re.findall(r'_generate_sample_data\(', content)
    print(f"Found {len(sample_data_calls)} calls to _generate_sample_data")

    # Check for _generate_enhanced_sample_data calls
    enhanced_calls = re.findall(r'_generate_enhanced_sample_data\(', content)
    print(f"Found {len(enhanced_calls)} calls to _generate_enhanced_sample_data")

    # Check for "使用示例数据" messages
    sample_messages = re.findall(r'使用示例数据', content)
    print(f"Found {len(sample_messages)} '使用示例数据' messages")

    # Check for "不返回数据" messages (new messages)
    no_data_messages = re.findall(r'不返回数据', content)
    print(f"Found {len(no_data_messages)} '不返回数据' messages")

    print("\n=== Analysis ===")

    if len(sample_data_calls) == 0 and len(enhanced_calls) == 0:
        print("✅ PASS: No direct sample data generation calls found")
    else:
        print("❌ FAIL: Still found sample data generation calls")

    if len(no_data_messages) > 0:
        print("✅ PASS: Found 'no data return' messages (good)")
    else:
        print("❌ FAIL: No 'no data return' messages found")

    # Show the actual lines that contain sample data calls
    if sample_data_calls or enhanced_calls:
        print("\n=== Lines with sample data calls ===")
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '_generate_sample_data(' in line or '_generate_enhanced_sample_data(' in line:
                print(f"Line {i}: {line.strip()}")

    # Show the new no-data messages
    if no_data_messages:
        print("\n=== Lines with 'no data' messages ===")
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '不返回数据' in line:
                print(f"Line {i}: {line.strip()}")

if __name__ == "__main__":
    check_file_for_sample_data_calls()