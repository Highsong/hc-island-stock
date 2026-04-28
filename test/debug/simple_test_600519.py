#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单测试600519股票2025年利润表数据的调试脚本"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_600519_direct():
    """直接测试600519股票利润表接口"""
    print("开始直接测试600519股票利润表接口...")

    try:
        import akshare as ak
        print(f"AKShare版本: {getattr(ak, '__version__', 'Unknown')}")
        print(f"AKShare模块路径: {ak.__file__}")
    except ImportError as e:
        print(f"AKShare导入失败: {e}")
        return

    stock_code = "600519"

    print(f"\n{'='*100}")
    print(f"测试目标: 股票{stock_code} 利润表数据")
    print(f"测试时间: {__import__('datetime').datetime.now().isoformat()}")
    print(f"{'='*100}\n")

    # 测试东方财富利润表接口
    print("测试东方财富利润表接口:")
    print(f"调用: ak.stock_profit_sheet_by_report_em('{stock_code}')")

    # 打印详细的输入报文
    request_params = {
        "stock_code": stock_code,
        "api_name": "ak.stock_profit_sheet_by_report_em",
        "target_year": "2025"
    }
    print(f"输入报文参数: {request_params}")

    try:
        df = ak.stock_profit_sheet_by_report_em(stock_code)
        print(f"接口调用完成，返回类型: {type(df)}")

        if df is None:
            print("ERROR: 东方财富利润表接口返回None")
        elif hasattr(df, 'empty') and df.empty:
            print("ERROR: 东方财富利润表接口返回空DataFrame")
        else:
            print(f"SUCCESS: 东方财富利润表接口成功: {len(df)} 条记录")
            if hasattr(df, 'columns'):
                print(f"DataFrame列名: {list(df.columns)}")
            if hasattr(df, 'head'):
                print(f"DataFrame前几行: {df.head().to_dict()}")

    except Exception as e:
        print(f"ERROR: 东方财富利润表接口调用异常: {type(e).__name__}: {e}")

    # 测试新浪利润表接口
    print(f"\n测试新浪利润表接口:")
    print(f"调用: ak.stock_financial_report_sina('{stock_code}', symbol='利润表')")

    # 打印新浪接口的输入报文
    sina_request_params = {
        "stock_code": stock_code,
        "symbol": "利润表",
        "api_name": "ak.stock_financial_report_sina",
        "target_year": "2025"
    }
    print(f"新浪接口输入报文参数: {sina_request_params}")

    try:
        df = ak.stock_financial_report_sina(stock_code, symbol="利润表")
        print(f"新浪接口调用完成，返回类型: {type(df)}")

        if df is None:
            print("ERROR: 新浪利润表接口返回None")
        elif hasattr(df, 'empty') and df.empty:
            print("ERROR: 新浪利润表接口返回空DataFrame")
        else:
            print(f"SUCCESS: 新浪利润表接口成功: {len(df)} 条记录")
            if hasattr(df, 'columns'):
                print(f"DataFrame列名: {list(df.columns)}")
            if hasattr(df, 'shape'):
                print(f"DataFrame形状: {df.shape}")

    except Exception as e:
        print(f"ERROR: 新浪利润表接口调用异常: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_600519_direct()