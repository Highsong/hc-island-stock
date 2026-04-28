#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test enhanced AKShare error logging"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from src.data_extraction.stock_data_source import StockDataSource

def test_enhanced_error_logging():
    """Test the enhanced error logging functionality"""
    print("=== Testing Enhanced AKShare Error Logging ===")

    data_source = StockDataSource()

    # Test with stocks that are likely to fail
    test_stocks = ["600519", "000858", "000001"]

    for stock_code in test_stocks:
        print(f"\n--- Testing stock: {stock_code} ---")

        try:
            # Test financial data retrieval (should log detailed errors)
            result = data_source.get_stock_financial_data(stock_code, "2022", "2023")
            print(f"Data retrieval completed for {stock_code}")

            if result:
                print(f"  Retrieved data for {len(result)} years")
            else:
                print(f"  No data retrieved (expected due to AKShare issues)")

        except Exception as e:
            print(f"Unexpected error for {stock_code}: {e}")

        time.sleep(2)  # Be respectful to the API

    # Test stock search (should also log errors)
    print(f"\n--- Testing stock search ---")
    try:
        search_results = data_source.search_stocks("茅台")
        print(f"Search completed: {len(search_results)} results")
    except Exception as e:
        print(f"Search failed: {e}")

    print(f"\n--- Checking error log ---")
    error_log_path = os.path.join("data", "cache", "akshare_errors.log")
    if os.path.exists(error_log_path):
        print(f"Error log created at: {error_log_path}")
        try:
            with open(error_log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                print(f"Total error entries: {len(lines)}")
                if lines:
                    print("\nLast 5 error entries:")
                    for line in lines[-5:]:
                        try:
                            error_entry = eval(line.strip())  # Safe since it's our own log format
                            print(f"  {error_entry['timestamp']} - {error_entry['api_name']} - {error_entry['error_type']}")
                        except:
                            print(f"  {line.strip()}")
        except Exception as e:
            print(f"Failed to read error log: {e}")
    else:
        print("No error log found")

if __name__ == "__main__":
    test_enhanced_error_logging()