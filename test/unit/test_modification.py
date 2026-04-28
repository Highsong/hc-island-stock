#!/usr/bin/env python3
"""Test the modification - check if year inputs are removed"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def test_year_inputs():
    """Test that year inputs are properly handled"""
    print("Testing year input modifications...")

    # Read the modified app_new.py file
    with open('src/app_new.py', 'r') as f:
        content = f.read()

    # Check if the year input section is correctly modified
    lines = content.split('\n')
    year_input_section_found = False
    start_button_found = False

    for i, line in enumerate(lines):
        if '开始分析' in line or 'start analysis' in line.lower():
            start_button_found = True
            print(f"✓ Start analysis button found at line {i+1}")

            # Look for year inputs after the button (should be limited)
            j = i + 1
            while j < len(lines) and ('text_input' not in lines[j] or '年份' not in lines[j]):
                j += 1

            if j < len(lines) and ('text_input' in lines[j] and '年份' in lines[j]):
                print(f"✗ Year input still found after start button at line {j+1}")
                year_input_section_found = True
            else:
                print("✓ No year inputs found below start button")

    if not start_button_found:
        print("✗ Start analysis button not found")

    if not year_input_section_found:
        print("✓ Year input section properly removed")

    return not year_input_section_found

if __name__ == '__main__':
    success = test_year_inputs()
    if success:
        print("\n✅ Modification successful - year inputs removed from below start button")
    else:
        print("\n❌ Modification incomplete - year inputs still present")