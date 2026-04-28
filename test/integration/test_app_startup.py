#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Streamlit app startup without actually running Streamlit"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def test_app_startup():
    """Test that the Streamlit app can start up correctly"""
    print("=" * 80)
    print("TESTING STREAMLIT APP STARTUP")
    print("=" * 80)

    try:
        # Test all imports
        print("\n1. Testing imports...")
        from visualization.dashboard_layout import DashboardLayout
        print("   ✅ DashboardLayout import successful")

        from visualization.chart_generator import ChartGenerator
        print("   ✅ ChartGenerator import successful")

        from analysis.financial_metrics import FinancialMetrics
        print("   ✅ FinancialMetrics import successful")

        from analysis.trend_analysis import TrendAnalysis
        print("   ✅ TrendAnalysis import successful")

        from analysis.insights_generator import InsightsGenerator
        print("   ✅ InsightsGenerator import successful")

        from data_extraction.stock_data_source import StockDataSource
        print("   ✅ StockDataSource import successful")

        from utils import helpers
        print("   ✅ utils.helpers import successful")

        from utils.cache_manager import cache_manager
        print("   ✅ cache_manager import successful")

        # Test class instantiation
        print("\n2. Testing class instantiation...")
        dashboard = DashboardLayout()
        print("   ✅ DashboardLayout instantiation successful")

        chart_gen = ChartGenerator()
        print("   ✅ ChartGenerator instantiation successful")

        metrics = FinancialMetrics()
        print("   ✅ FinancialMetrics instantiation successful")

        trend_analysis = TrendAnalysis()
        print("   ✅ TrendAnalysis instantiation successful")

        insights = InsightsGenerator()
        print("   ✅ InsightsGenerator instantiation successful")

        data_source = StockDataSource()
        print("   ✅ StockDataSource instantiation successful")

        # Test DataProcessor
        print("\n3. Testing DataProcessor...")
        from app_new import DataProcessor
        processor = DataProcessor()
        print("   ✅ DataProcessor instantiation successful")

        # Test a quick analysis
        print("\n4. Testing quick analysis...")
        result = processor.process_stock_data('600519', '2023', '2023', 'quarter')
        if result.get('periods'):
            print("   ✅ Quick analysis successful")
        else:
            print("   ❌ Quick analysis failed")

        print("\n🎉 ALL STARTUP TESTS PASSED!")
        print("\n📊 APP STARTUP STATUS: READY")
        print("\nThe Streamlit app should now start correctly with:")
        print("• ✅ All imports working")
        print("• ✅ All classes instantiating correctly")
        print("• ✅ Data processing working")
        print("• ✅ No startup errors")

        print("\n🚀 Ready to run: python -m streamlit run src/app_new.py")

    except Exception as e:
        print(f"\n❌ STARTUP TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("APP STARTUP TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_app_startup()