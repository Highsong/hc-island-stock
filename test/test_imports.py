#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入问题的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("开始测试模块导入...")

try:
    print("1. 测试基本导入...")
    import pandas as pd
    print("   [OK] pandas 导入成功")

    import plotly
    print("   [OK] plotly 导入成功")

    import streamlit as st
    print("   [OK] streamlit 导入成功")

except ImportError as e:
    print(f"   [FAIL] 基本包导入失败: {e}")
    print("   请先运行: pip install -r requirements.txt")
    sys.exit(1)

try:
    print("\n2. 测试项目模块导入...")

    # 测试各个模块的导入
    from src.visualization.dashboard_layout import DashboardLayout
    print("   [OK] DashboardLayout 导入成功")

    from src.visualization.chart_generator import ChartGenerator
    print("   [OK] ChartGenerator 导入成功")

    from src.analysis.financial_metrics import FinancialMetrics
    print("   [OK] FinancialMetrics 导入成功")

    from src.analysis.trend_analysis import TrendAnalysis
    print("   [OK] TrendAnalysis 导入成功")

    from src.analysis.insights_generator import InsightsGenerator
    print("   [OK] InsightsGenerator 导入成功")

    from src.data_extraction.stock_data_source import StockDataSource
    print("   [OK] StockDataSource 导入成功")

    from src.utils.helpers import *
    print("   [OK] helpers 导入成功")

    from src.utils.cache_manager import cache_manager
    print("   [OK] cache_manager 导入成功")

except ImportError as e:
    print(f"   [FAIL] 项目模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. 测试类实例化...")

try:
    dashboard = DashboardLayout()
    print("   [OK] DashboardLayout 实例化成功")

    chart_gen = ChartGenerator()
    print("   [OK] ChartGenerator 实例化成功")

    metrics = FinancialMetrics()
    print("   [OK] FinancialMetrics 实例化成功")

    trend = TrendAnalysis()
    print("   [OK] TrendAnalysis 实例化成功")

    insights = InsightsGenerator()
    print("   [OK] InsightsGenerator 实例化成功")

    data_source = StockDataSource()
    print("   [OK] StockDataSource 实例化成功")

except Exception as e:
    print(f"   [FAIL] 类实例化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[OK] 所有导入测试通过!")
print("\n4. 测试主要功能...")

try:
    # 测试数据源基本功能
    print("   测试数据源...")
    stock_info = data_source.get_stock_info("600519")
    print(f"   [OK] 股票信息获取成功: {stock_info.get('name', 'Unknown')}")

    # 测试缓存管理器
    print("   测试缓存管理器...")
    cache_manager.set({"test": "data"}, "test", "test_key")
    cached = cache_manager.get("test", "test", "test_key")
    print(f"   [OK] 缓存测试成功: {cached}")

except Exception as e:
    print(f"   [WARN] 功能测试遇到问题: {e}")
    # 这不是致命错误，继续

print("\n[OK] 导入和基本功能测试完成!")