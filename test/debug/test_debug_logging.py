#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试调试日志功能"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_debug_logging():
    """测试调试日志功能"""
    print("开始测试调试日志功能...")

    try:
        import akshare as ak
        print(f"AKShare版本: {getattr(ak, '__version__', 'Unknown')}")
    except ImportError as e:
        print(f"AKShare导入失败: {e}")
        return

    stock_code = "600519"
    period = "year"

    print(f"\n{'='*100}")
    print(f"测试目标: 股票{stock_code} 2025年利润表数据")
    print(f"测试时间: {datetime.now().isoformat()}")
    print(f"{'='*100}\n")

    # 模拟我们修改后的_get_income_statement方法的调试输出
    print(f"\n{'='*80}")
    print(f"准备调用利润表接口")
    print(f"股票代码: {stock_code}")
    print(f"数据周期: {period}")
    print(f"目标年份: 2025")
    print(f"接口调用时间: {datetime.now().isoformat()}")
    print(f"{'='*80}\n")

    # 打印详细的输入报文信息 - 东方财富接口
    request_params = {
        "stock_code": stock_code,
        "period": period,
        "target_year": "2025",
        "api_name": "ak.stock_profit_sheet_by_report_em"
    }
    print(f"东方财富接口输入报文参数:")
    print(json.dumps(request_params, ensure_ascii=False, indent=2))

    # 尝试东方财富接口
    try:
        print(f"\n尝试东方财富利润表接口: {stock_code}")
        print(f"调用: ak.stock_profit_sheet_by_report_em('{stock_code}')")

        df = ak.stock_profit_sheet_by_report_em(stock_code)
        print(f"接口调用完成，返回类型: {type(df)}")

        if df is None:
            print("ERROR: 东方财富利润表接口返回None")
        elif hasattr(df, 'empty') and df.empty:
            print("ERROR: 东方财富利润表接口返回空DataFrame")
        else:
            print(f"SUCCESS: 东方财富利润表接口成功: {len(df)} 条记录")

    except Exception as e:
        print(f"ERROR: 东方财富利润表接口调用异常: {type(e).__name__}: {e}")

        # 尝试新浪接口
        try:
            print(f"\n尝试新浪利润表接口: {stock_code}")
            print(f"调用: ak.stock_financial_report_sina('{stock_code}', symbol='利润表')")

            # 打印新浪接口的输入报文
            sina_request_params = {
                "stock_code": stock_code,
                "symbol": "利润表",
                "period": period,
                "target_year": "2025",
                "api_name": "ak.stock_financial_report_sina"
            }
            print(f"新浪接口输入报文参数:")
            print(json.dumps(sina_request_params, ensure_ascii=False, indent=2))

            df = ak.stock_financial_report_sina(stock_code, symbol="利润表")
            print(f"新浪接口调用完成，返回类型: {type(df)}")

            if df is None:
                print("ERROR: 新浪利润表接口返回None")
            elif hasattr(df, 'empty') and df.empty:
                print("ERROR: 新浪利润表接口返回空DataFrame")
            else:
                print(f"SUCCESS: 新浪利润表接口成功: {len(df)} 条记录")
                if hasattr(df, 'columns'):
                    print(f"DataFrame列名数量: {len(list(df.columns))}")
                if hasattr(df, 'shape'):
                    print(f"DataFrame形状: {df.shape}")

        except Exception as e2:
            print(f"ERROR: 新浪利润表接口调用异常: {type(e2).__name__}: {e2}")

    print(f"\n{'='*100}")
    print("调试日志测试完成")
    print(f"{'='*100}")

if __name__ == "__main__":
    test_debug_logging()