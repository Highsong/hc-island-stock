#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple test for cache behavior"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..', 'src'))

try:
    from data_extraction.stock_data_source import StockDataSource

    print("=== Testing Cache Behavior ===")

    # Create data source
    data_source = StockDataSource()

    # Clear cache
    print("Clearing cache...")
    data_source.cache_manager.clear_all()

    test_stock = "600519"
    print(f"Testing with stock: {test_stock}")

    # First call
    print("\nFirst call:")
    start = time.time()
    result1 = data_source.get_stock_financial_data(test_stock, "2022", "2023")
    time1 = time.time() - start
    print(f"Time: {time1:.2f}s, Keys: {list(result1.keys()) if result1 else None}")

    # Second call (should retry API, not use cache)
    print("\nSecond call:")
    start = time.time()
    result2 = data_source.get_stock_financial_data(test_stock, "2022", "2023")
    time2 = time.time() - start
    print(f"Time: {time2:.2f}s, Keys: {list(result2.keys()) if result2 else None}")

    # Check if times are similar (indicating API retry)
    if abs(time1 - time2) < max(time1, time2) * 0.3:
        print("✓ Second call took similar time - likely retried API")
    else:
        print("⚠ Second call time differs significantly")

    print("\nTest completed.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()