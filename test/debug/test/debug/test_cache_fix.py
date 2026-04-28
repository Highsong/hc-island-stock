#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test cache fix to ensure sample data is not cached"""

import sys
import os
import time
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src'))

def test_cache_behavior():
    """Test that sample data is not cached and API is retried on each call"""
    print("=== Testing Cache Behavior Fix ===")

    try:
        from data_extraction.stock_data_source import StockDataSource

        # Create data source
        data_source = StockDataSource()

        # Clear any existing cache first
        print("Clearing existing cache...")
        data_source.cache_manager.clear_all()

        test_stock = "600519"  # Use a stock that will likely fail
        print(f"\nTesting with stock: {test_stock}")

        # First call - should try API, fail, and return sample data
        print("\n--- First call (should try API, fail, return sample data) ---")
        start_time = time.time()
        result1 = data_source.get_stock_financial_data(test_stock, "2022", "2023")
        time1 = time.time() - start_time
        print(f"First call took: {time1:.2f} seconds")
        print(f"Result type: {type(result1)}")
        print(f"Result keys: {list(result1.keys()) if result1 else 'None'}")

        # Check if any cache was created
        cache_files_before = [f for f in os.listdir("data/cache") if f.endswith('.json')]
        print(f"Cache files after first call: {len(cache_files_before)}")

        # Second call - should try API again (not use cache), fail again, return sample data
        print("\n--- Second call (should try API again, not use cache) ---")
        start_time = time.time()
        result2 = data_source.get_stock_financial_data(test_stock, "2022", "2023")
        time2 = time.time() - start_time
        print(f"Second call took: {time2:.2f} seconds")
        print(f"Result type: {type(result2)}")
        print(f"Result keys: {list(result2.keys()) if result2 else 'None'}")

        # Check cache again
        cache_files_after = [f for f in os.listdir("data/cache") if f.endswith('.json')]
        print(f"Cache files after second call: {len(cache_files_after)}")

        # Third call with force_refresh=True - should definitely try API again
        print("\n--- Third call (force_refresh=True) ---")
        start_time = time.time()
        result3 = data_source.get_stock_financial_data(test_stock, "2022", "2023", force_refresh=True)
        time3 = time.time() - start_time
        print(f"Third call took: {time3:.2f} seconds")
        print(f"Result type: {type(result3)}")
        print(f"Result keys: {list(result3.keys()) if result3 else 'None'}")

        # Analyze results
        print("\n--- Analysis ---")
        if result1 == result2 == result3:
            print("✓ All results are identical (expected for sample data)")
        else:
            print("⚠ Results differ between calls")

        if time2 < time1 * 0.5:  # Second call should not be dramatically faster
            print("⚠ Second call was suspiciously fast - might be using cache")
        else:
            print("✓ Second call took reasonable time - likely retried API")

        if len(cache_files_after) == len(cache_files_before) == 0:
            print("✓ No cache files created (expected since API failed)")
        else:
            print(f"⚠ Cache files detected: {cache_files_after}")

        # Test with a mock success scenario
        print("\n--- Testing successful API scenario ---")
        # Create a mock successful result
        mock_real_data = {
            '2023': {
                'income_statement': {'营业收入': [1000], '净利润': [150]},
                'balance_sheet': {'总资产': [2000], '总负债': [600]},
                'cash_flow': {'经营活动现金流': [165]}
            }
        }

        # Manually cache this "real" data
        data_source.cache_manager.set(mock_real_data, test_stock, "financial", "year")
        print("Manually cached mock real data")

        # Now call again - should use cached data
        print("Calling with cached real data available...")
        start_time = time.time()
        result4 = data_source.get_stock_financial_data(test_stock, "2022", "2023")
        time4 = time.time() - start_time
        print(f"Cached call took: {time4:.2f} seconds")

        if result4 == mock_real_data:
            print("✓ Correctly used cached real data")
        else:
            print("⚠ Did not use cached real data as expected")

        if time4 < time1 * 0.3:  # Cached call should be much faster
            print("✓ Cached call was much faster")
        else:
            print("⚠ Cached call was not significantly faster")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cache_behavior()