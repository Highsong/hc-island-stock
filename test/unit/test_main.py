#!/usr/bin/env python3
"""Test the main app function directly"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def test_app():
    """Test the main app functionality"""
    try:
        import streamlit as st
        from visualization.dashboard_layout import DashboardLayout
        from analysis.financial_metrics import FinancialMetrics
        from analysis.trend_analysis import TrendAnalysis
        from analysis.insights_generator import InsightsGenerator
        from data_extraction.stock_data_source import StockDataSource
        from utils.helpers import detect_new_reports, extract_year_from_filename
        from utils.cache_manager import cache_manager

        print("All imports successful")

        # Test the get_available_years function logic
        pdf_files = detect_new_reports()
        years = [extract_year_from_filename(f) for f in pdf_files]
        available_years = sorted([y for y in years if y != '未知年份'], reverse=True)

        print(f"Available years: {available_years}")

        if not available_years:
            print("No available years - this would cause the app to show warning message")
            return False

        print("✓ App has data to work with")

        # Try to create dashboard
        dashboard = DashboardLayout()
        print("✓ Dashboard created")

        # Try basic setup
        dashboard.setup_page()
        print("✓ Page setup completed")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_app()
    if success:
        print("\nApp appears ready for use!")
    else:
        print("\nApp has issues that need to be resolved.")