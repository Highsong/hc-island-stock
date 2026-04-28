#!/usr/bin/env python3
"""Debug version of the app to identify startup issues"""

import sys
import os
import traceback

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/src')

def test_step(step_name, test_func):
    """Helper to test a step and catch any errors"""
    print(f"Testing {step_name}...")
    try:
        result = test_func()
        print(f"✓ {step_name} passed")
        return True
    except Exception as e:
        print(f"✗ {step_name} failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("Starting debug test of Streamlit app...")

    # Test 1: Basic imports
    def test_imports():
        import streamlit as st
        from visualization.dashboard_layout import DashboardLayout
        from visualization.chart_generator import ChartGenerator
        from analysis.financial_metrics import FinancialMetrics
        from analysis.trend_analysis import TrendAnalysis
        from analysis.insights_generator import InsightsGenerator
        from data_extraction.stock_data_source import StockDataSource
        from utils.helpers import load_processed_data, save_processed_data, format_percentage, detect_new_reports, extract_year_from_filename, validate_stock_code, format_stock_display_name, get_market_type, format_financial_value, calculate_growth_rate, get_period_display_name
        from utils.cache_manager import cache_manager
        return True

    if not test_step("basic imports", test_imports):
        return False

    # Test 2: Data detection
    def test_data_detection():
        from utils.helpers import detect_new_reports, extract_year_from_filename
        pdf_files = detect_new_reports()
        years = [extract_year_from_filename(f) for f in pdf_files]
        return len(years) > 0

    if not test_step("data detection", test_data_detection):
        return False

    # Test 3: Dashboard setup simulation
    def test_dashboard_setup():
        dashboard = DashboardLayout()
        # Just test that we can create the object
        return hasattr(dashboard, 'setup_page')

    if not test_step("dashboard creation", test_dashboard_setup):
        return False

    print("\n🎉 All basic tests passed!")
    return True

if __name__ == '__main__':
    try:
        success = main()
        if success:
            print("\nApp should work now - trying to run Streamlit...")
            import subprocess
            subprocess.run([sys.executable, "-m", "streamlit", "run", "src/app_new.py", "--server.headless=true"])
        else:
            print("\nSome tests failed - check the errors above")
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()