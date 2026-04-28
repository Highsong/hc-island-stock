#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the behavior when API calls fail - should return no data"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..', 'src'))

def test_api_failure_behavior():
    """Test that API failures return no data instead of sample data"""
    print("=== Testing API Failure Behavior ===")
    print("Expected: API failures should return empty dict, not sample data")
    print()

    try:
        from data_extraction.stock_data_source import StockDataSource

        # Create data source and clear cache
        data_source = StockDataSource()
        data_source.cache_manager.clear_all()

        # Test stocks that are likely to fail
        test_cases = [
            ("600519", "A股 - 贵州茅台"),
            ("000858", "A股 - 五粮液"),
            ("0700.HK", "港股 - 腾讯")
        ]

        all_passed = True

        for stock_code, description in test_cases:
            print(f"Testing {description} ({stock_code})...")

            # Call the main function
            result = data_source.get_stock_financial_data(stock_code, "2022", "2023")

            # Check result
            if result is None:
                print(f"  ❌ FAIL: Got None instead of empty dict")
                all_passed = False
            elif isinstance(result, dict) and len(result) == 0:
                print(f"  ✅ PASS: Got empty dict (no data returned)")
            elif isinstance(result, dict) and len(result) > 0:
                print(f"  ❌ FAIL: Got data when API should have failed")
                print(f"     Keys: {list(result.keys())}")
                all_passed = False
            else:
                print(f"  ❌ FAIL: Got unexpected result type: {type(result)}")
                all_passed = False

            print()

        # Test summary
        print("=" * 50)
        if all_passed:
            print("✅ ALL TESTS PASSED: API failures correctly return no data")
        else:
            print("❌ SOME TESTS FAILED: Check output above")
        print("=" * 50)

        return all_passed

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_failure_behavior()
    exit(0 if success else 1)