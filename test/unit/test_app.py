#!/usr/bin/env python3
"""Test script for the Streamlit app to identify issues"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

try:
    # Test all imports that the main app uses
    import streamlit as st
    from visualization.dashboard_layout import DashboardLayout
    from visualization.chart_generator import ChartGenerator
    from analysis.financial_metrics import FinancialMetrics
    from analysis.trend_analysis import TrendAnalysis
    from analysis.insights_generator import InsightsGenerator
    from data_extraction.stock_data_source import StockDataSource
    from utils.helpers import *

    print("All imports successful")

    # Test data detection function
    from utils.helpers import detect_new_reports, extract_year_from_filename

    pdf_files = detect_new_reports()
    print(f"Detected {len(pdf_files)} PDF files")
    years = [extract_year_from_filename(f) for f in pdf_files]
    print(f"Extracted years: {years}")

    # Test cache manager
    from utils.cache_manager import cache_manager
    print("Cache manager imported successfully")

    print("\nApp appears to have no major import or setup issues!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()