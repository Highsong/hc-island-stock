#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detailed request logging for AKShare interface calls"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def detailed_request_logging():
    """Print detailed request information before AKShare calls"""
    print("=" * 80)
    print("DETAILED REQUEST LOGGING FOR 600519 PROFIT STATEMENT 2025")
    print("=" * 80)

    try:
        import akshare as ak
        import pandas as pd

        stock_code = "600519"
        target_year = "2025"

        print(f"目标股票: {stock_code}")
        print(f"目标年份: {target_year}")
        print(f"AKShare版本: {getattr(ak, '__version__', 'Unknown')}")
        print()

        # 1. 测试东方财富利润表接口 - 打印详细请求信息
        print("1. 东方财富利润表接口详细请求信息:")
        print("-" * 60)

        # 打印调用前的参数
        print("[请求前] 参数信息:")
        print(f"  函数名: ak.stock_profit_sheet_by_report_em")
        print(f"  股票代码: {stock_code}")
        print(f"  参数类型: str")
        print(f"  标准化股票代码: {stock_code}")
        print()

        # 尝试获取函数签名
        try:
            import inspect
            sig = inspect.signature(ak.stock_profit_sheet_by_report_em)
            print(f"[请求前] 函数签名: {sig}")
            print()
        except Exception as e:
            print(f"[请求前] 无法获取函数签名: {e}")
            print()

        # 打印调用信息
        print("[请求中] 调用信息:")
        print(f"  调用语句: ak.stock_profit_sheet_by_report_em('{stock_code}')")
        print(f"  调用时间: {pd.Timestamp.now()}")
        print()

        # 执行调用并捕获结果
        try:
            print("[请求执行] 开始调用...")
            result = ak.stock_profit_sheet_by_report_em(stock_code)
            print(f"[请求完成] 调用成功")
            print(f"[响应结果] 返回类型: {type(result)}")
            print(f"[响应结果] 是否为None: {result is None}")

            if result is not None:
                print(f"[响应结果] DataFrame形状: {result.shape}")
                print(f"[响应结果] 是否为空: {result.empty}")
                if hasattr(result, 'columns'):
                    print(f"[响应结果] 列名: {list(result.columns)}")
                if hasattr(result, 'index'):
                    print(f"[响应结果] 索引: {list(result.index)}")
            else:
                print("[响应结果] 返回None")

        except Exception as e:
            print(f"[请求异常] 调用失败: {type(e).__name__}: {e}")
            print(f"[请求异常] 异常详情: {str(e)}")
            import traceback
            print(f"[请求异常] 堆栈跟踪:")
            traceback.print_exc()

        print()

        # 2. 测试新浪利润表接口 - 打印详细请求信息
        print("2. 新浪利润表接口详细请求信息:")
        print("-" * 60)

        # 打印调用前的参数
        print("[请求前] 参数信息:")
        print(f"  函数名: ak.stock_financial_report_sina")
        print(f"  股票代码: {stock_code}")
        print(f"  symbol参数: '利润表'")
        print(f"  参数类型: str, str")
        print()

        # 尝试获取函数签名
        try:
            sig = inspect.signature(ak.stock_financial_report_sina)
            print(f"[请求前] 函数签名: {sig}")
            print()
        except Exception as e:
            print(f"[请求前] 无法获取函数签名: {e}")
            print()

        # 打印调用信息
        print("[请求中] 调用信息:")
        print(f"  调用语句: ak.stock_financial_report_sina('{stock_code}', symbol='利润表')")
        print(f"  调用时间: {pd.Timestamp.now()}")
        print()

        # 执行调用并捕获结果
        try:
            print("[请求执行] 开始调用...")
            result_sina = ak.stock_financial_report_sina(stock_code, symbol="利润表")
            print(f"[请求完成] 调用成功")
            print(f"[响应结果] 返回类型: {type(result_sina)}")
            print(f"[响应结果] 是否为None: {result_sina is None}")

            if result_sina is not None:
                print(f"[响应结果] DataFrame形状: {result_sina.shape}")
                print(f"[响应结果] 是否为空: {result_sina.empty}")

                if hasattr(result_sina,