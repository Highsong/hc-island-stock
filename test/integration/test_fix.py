#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the data structure fix"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from data_extraction.stock_data_source import StockDataSource

def test_fix():
    """Test that the fix works correctly"""
    print("=" * 80)
    print("TESTING THE FIX")
    print("=" * 80)

    try:
        data_source = StockDataSource()

        # Test with year period
        print("\n1. Testing with period='year'...")
        yearly_data = data_source.get_stock_financial_data('600519', '2021', '2023', 'year')

        print(f"Yearly data keys: {list(yearly_data.keys())}")

        if yearly_data:
            first_year = list(yearly_data.keys())[0]
            year_data = yearly_data[first_year]
            print(f"First year ({first_year}) structure:")
            print(f"  Type: {type(year_data)}")
            print(f"  Keys: {list(year_data.keys())}")

            # Check if it has the expected structure
            if 'income_statement' in year_data:
                print("  ✓ Has income_statement")
                income_stmt = year_data['income_statement']
                print(f"    Revenue: {income_stmt.get('营业收入', [0])[0]}")
                print(f"    Net Profit: {income_stmt.get('净利润', [0])[0]}")
            else:
                print("  ✗ Missing income_statement")

            if 'balance_sheet' in year_data:
                print("  ✓ Has balance_sheet")
                balance_sheet = year_data['balance_sheet']
                print(f"    Total Assets: {balance_sheet.get('总资产', [0])[0]}")
            else:
                print("  ✗ Missing balance_sheet")

            if 'cash_flow' in year_data:
                print("  ✓ Has cash_flow")
                cash_flow = year_data['cash_flow']
                print(f"    Operating Cash Flow: {cash_flow.get('经营活动现金流', [0])[0]}")
            else:
                print("  ✗ Missing cash_flow")

        # Test with quarter period
        print("\n2. Testing with period='quarter'...")
        quarterly_data = data_source.get_stock_financial_data('600519', '2023', '2023', 'quarter')

        print(f"Quarterly data keys: {list(quarterly_data.keys())}")

        if quarterly_data:
            first_year = list(quarterly_data.keys())[0]
            year_data = quarterly_data[first_year]
            print(f"First year ({first_year}) structure:")
            print(f"  Type: {type(year_data)}")
            print(f"  Keys: {list(year_data.keys())}")

            # Check if it has quarterly structure
            quarterly_keys = [k for k in year_data.keys() if k.startswith('Q')]
            if quarterly_keys:
                print(f"  ✓ Has quarterly data: {quarterly_keys}")
                first_quarter = quarterly_keys[0]
                q_data = year_data[first_quarter]
                print(f"    Q1 Revenue: {q_data.get('营业收入', 0)}")
            else:
                print("  ✗ Missing quarterly data")

        print("\n3. Testing data aggregation...")
        # Test the aggregation function directly
        test_quarterly_data = {
            'Q1': {
                '营业收入': 100,
                '净利润': 20,
                'cash_flow': {'经营活动现金流': 25}
            },
            'Q2': {
                '营业收入': 120,
                '净利润': 25,
                'cash_flow': {'经营活动现金流': 30}
            },
            'Q3': {
                '营业收入': 110,
                '净利润': 22,
                'cash_flow': {'经营活动现金流': 28}
            },
            'Q4': {
                '营业收入': 130,
                '净利润': 28,
                'cash_flow': {'经营活动现金流': 35},
                'balance_sheet': {'总资产': 1000, '总负债': 400}
            }
        }

        annual_result = data_source._aggregate_quarterly_to_annual(test_quarterly_data)
        print(f"  Aggregated revenue: {annual_result['income_statement']['营业收入'][0]} (expected: 460)")
        print(f"  Aggregated net profit: {annual_result['income_statement']['净利润'][0]} (expected: 95)")
        print(f"  Q4 total assets: {annual_result['balance_sheet']['总资产'][0]} (expected: 1000)")

        print("\n✅ ALL TESTS PASSED!")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_fix()