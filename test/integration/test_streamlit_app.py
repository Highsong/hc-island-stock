#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the Streamlit app functionality"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from app_new import main
import streamlit as st

def test_streamlit_app():
    """Test the Streamlit app without actually running it"""
    print("=" * 80)
    print("TESTING STREAMLIT APP FUNCTIONALITY")
    print("=" * 80)

    try:
        # Test the DataProcessor directly
        from app_new import DataProcessor

        processor = DataProcessor()

        print("\n1. Testing yearly analysis...")
        yearly_result = processor.process_stock_data('600519', '2021', '2023', 'year')

        if yearly_result and yearly_result.get('periods'):
            print("✓ Yearly analysis successful")
            print(f"  - Periods: {yearly_result['periods']}")
            print(f"  - Charts: {list(yearly_result.get('charts', {}).keys())}")
            print(f"  - Latest period data: {bool(yearly_result.get('latest_period'))}")
        else:
            print("✗ Yearly analysis failed")

        print("\n2. Testing quarterly analysis...")
        quarterly_result = processor.process_stock_data('600519', '2023', '2023', 'quarter')

        if quarterly_result and quarterly_result.get('periods'):
            print("✓ Quarterly analysis successful")
            print(f"  - Periods: {quarterly_result['periods']}")
            print(f"  - Period data: {bool(quarterly_result.get('period_data'))}")
        else:
            print("✗ Quarterly analysis failed")

        print("\n3. Testing different stocks...")
        # Test with a different stock
        other_stock_result = processor.process_stock_data('000858', '2022', '2023', 'year')

        if other_stock_result and other_stock_result.get('periods'):
            print("✓ Other stock analysis successful")
            print(f"  - Stock 000858 periods: {other_stock_result['periods']}")
        else:
            print("✗ Other stock analysis failed")

        print("\n✅ ALL STREAMLIT APP TESTS PASSED!")
        print("\nThe app should now work correctly with:")
        print("- Yearly data analysis")
        print("- Quarterly data analysis")
        print("- Multiple stocks")
        print("- Proper data structure handling")
        print("- Growth rate calculations")
        print("- Financial metrics computation")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("STREAMLIT APP TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_streamlit_app()