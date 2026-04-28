#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive test for AKshare network calls"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def test_akshare_availability():
    """Test AKshare import and basic functionality"""
    print("=== Testing AKshare Availability ===")

    try:
        import akshare as ak
        print("AKshare imported successfully")

        # Test basic AKshare functionality
        print("Testing basic AKshare functions...")

        # Test stock list (should be safe)
        try:
            stock_list = ak.stock_zh_a_spot()
            print(f"✓ Stock list retrieved: {len(stock_list)} stocks")
        except Exception as e:
            print(f"Stock list failed: {e}")

        return True
    except ImportError:
        print("AKshare not available")
        return False
    except Exception as e:
        print(f"AKshare import error: {e}")
        return False

def test_financial_data_calls():
    """Test financial data API calls"""
    print("\n=== Testing Financial Data API Calls ===")

    try:
        import akshare as ak

        # Test stock used in the system
        test_stocks = ["600519", "000858", "000001"]

        for stock_code in test_stocks:
            print(f"\nTesting stock: {stock_code}")

            # Test income statement
            try:
                print(f"  Testing income statement for {stock_code}...")
                df_income = ak.stock_profit_sheet_by_report_em(stock_code)
                print(f"  Income statement: {len(df_income)} records")
                if len(df_income) > 0:
                    print(f"    Sample data: {df_income.iloc[0].to_dict()}")
            except Exception as e:
                print(f"  Income statement failed: {e}")

            time.sleep(1)  # Be respectful to the API

            # Test balance sheet
            try:
                print(f"  Testing balance sheet for {stock_code}...")
                df_balance = ak.stock_balance_sheet_by_report_em(stock_code)
                print(f"  Balance sheet: {len(df_balance)} records")
            except Exception as e:
                print(f"  Balance sheet failed: {e}")

            time.sleep(1)

            # Test cash flow
            try:
                print(f"  Testing cash flow for {stock_code}...")
                df_cash = ak.stock_cash_flow_sheet_by_report_em(stock_code)
                print(f"  Cash flow: {len(df_cash)} records")
            except Exception as e:
                print(f"  Cash flow failed: {e}")

            time.sleep(1)

    except Exception as e:
        print(f"Financial data test failed: {e}")
        return False

    return True

def test_stock_data_source_integration():
    """Test integration with StockDataSource"""
    print("\n=== Testing StockDataSource Integration ===")

    from data_extraction.stock_data_source import StockDataSource

    data_source = StockDataSource()

    # Test with a known stock
    test_stocks = ["600519", "000858"]

    for stock_code in test_stocks:
        print(f"\nTesting StockDataSource with {stock_code}:")

        try:
            # Test basic data retrieval
            result = data_source.get_stock_financial_data(stock_code, "2022", "2023")
            print(f"  Data retrieved: {len(result)} years")

            if result:
                year = list(result.keys())[0]
                year_data = result[year]
                print(f"  Sample year {year}:")
                print(f"    Income: {bool(year_data.get('income_statement'))}")
                print(f"    Balance: {bool(year_data.get('balance_sheet'))}")
                print(f"    Cash Flow: {bool(year_data.get('cash_flow'))}")

        except Exception as e:
            print(f"  Failed for {stock_code}: {e}")

        time.sleep(2)  # Be respectful to the API

    return True

def test_retry_mechanism():
    """Test the retry mechanism"""
    print("\n=== Testing Retry Mechanism ===")

    from data_extraction.stock_data_source import StockDataSource

    data_source = StockDataSource()

    # Test with a function that fails
    def failing_func(stock_code, period):
        raise Exception("Simulated network failure")

    try:
        result = data_source._fetch_with_retry(failing_func, "test", "year")
        print(f"Retry mechanism handled failure: {len(result)} items")
        return True
    except Exception as e:
        print(f"Retry mechanism failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing AKshare Network Calls")
    print("=" * 50)

    results = []

    # Test 1: AKshare availability
    results.append(test_akshare_availability())

    # Test 2: Financial data calls
    results.append(test_financial_data_calls())

    # Test 3: Integration
    results.append(test_stock_data_source_integration())

    # Test 4: Retry mechanism
    results.append(test_retry_mechanism())

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Passed: {sum(results)}/{len(results)}")

    if all(results):
        print("All tests passed!")
    else:
        print("Some tests failed - check output above")

    return all(results)

if __name__ == "__main__":
    main()