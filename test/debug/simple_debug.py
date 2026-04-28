#!/usr/bin/env python3
"""Simple debug script for Streamlit app"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

print("Testing Streamlit app components...")

try:
    # Test basic imports
    import streamlit as st
    from visualization.dashboard_layout import DashboardLayout
    from visualization.chart_generator import ChartGenerator
    from analysis.financial_metrics import FinancialMetrics
    from analysis.trend_analysis import TrendAnalysis
    from analysis.insights_generator import InsightsGenerator
    from data_extraction.stock_data_source import StockDataSource
    from utils.helpers import detect_new_reports, extract_year_from_filename, load_processed_data, save_processed_data, format_percentage
    from utils.cache_manager import cache_manager

    print("All imports successful")

    # Test data detection
    pdf_files = detect_new_reports()
    years = [extract_year_from_filename(f) for f in pdf_files]
    print(f"Detected {len(pdf_files)} PDF files with years: {years}")

    # Test dashboard creation
    dashboard = DashboardLayout()
    print("Dashboard created successfully")

    # Try to call setup_page method
    try:
        dashboard.setup_page()
        print("setup_page() called successfully")
    except Exception as e:
        print(f"setup_page() failed: {e}")
        import traceback
        traceback.print_exc()

    print("\nBasic tests completed!")

except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()