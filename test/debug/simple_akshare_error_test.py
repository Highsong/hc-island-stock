#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple test to demonstrate AKShare error logging"""

import os
import json
import sys
from datetime import datetime

def test_akshare_error_logging():
    """Test AKShare error logging functionality"""
    print("=== Testing AKShare Error Logging ===")

    # Create a simple error logger
    def log_akshare_error(api_name, stock_code, error, additional_info=""):
        error_details = {
            "timestamp": datetime.now().isoformat(),
            "api_name": api_name,
            "stock_code": stock_code,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "additional_info": additional_info
        }

        print(f"\n{'='*60}")
        print(f"AKSHARE接口失败详情:")
        print(f"时间: {error_details['timestamp']}")
        print(f"API: {api_name}")
        print(f"股票代码: {stock_code}")
        print(f"错误类型: {error_details['error_type']}")
        print(f"错误信息: {error_details['error_message']}")
        if additional_info:
            print(f"附加信息: {additional_info}")
        print(f"{'='*60}\n")

        # Save to error log file
        try:
            os.makedirs("data/cache", exist_ok=True)
            error_log_path = os.path.join("data", "cache", "akshare_errors.log")
            with open(error_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(error_details, ensure_ascii=False) + "\n")
            print(f"错误日志已保存到: {error_log_path}")
        except Exception as log_error:
            print(f"写入错误日志失败: {log_error}")

    # Test AKShare availability first
    try:
        import akshare as ak
        print("AKShare imported successfully")
    except ImportError as e:
        log_akshare_error("AKShare导入", "N/A", e, "AKShare未安装")
        return

    # Test various AKShare calls that are likely to fail
    test_cases = [
        {
            "api": "stock_profit_sheet_by_report_em",
            "stock": "600519",
            "call": lambda: ak.stock_profit_sheet_by_report_em("600519")
        },
        {
            "api": "stock_balance_sheet_by_report_em",
            "stock": "600519",
            "call": lambda: ak.stock_balance_sheet_by_report_em("600519")
        },
        {
            "api": "stock_cash_flow_sheet_by_report_em",
            "stock": "600519",
            "call": lambda: ak.stock_cash_flow_sheet_by_report_em("600519")
        },
        {
            "api": "stock_financial_report_sina",
            "stock": "600519",
            "call": lambda: ak.stock_financial_report_sina("600519", symbol="利润表")
        },
        {
            "api": "stock_info_search_code",
            "stock": "茅台",
            "call": lambda: ak.stock_info_search_code(symbol="茅台")
        }
    ]

    for test_case in test_cases:
        print(f"\n测试API: {test_case['api']} (股票: {test_case['stock']})")
        try:
            result = test_case['call']()
            if result is None:
                log_akshare_error(test_case['api'], test_case['stock'], Exception("API返回None"), "接口返回空结果")
            else:
                print(f"API调用成功，返回数据类型: {type(result)}")
                if hasattr(result, 'shape'):
                    print(f"数据形状: {result.shape}")
                elif hasattr(result, '__len__'):
                    print(f"数据长度: {len(result)}")
        except Exception as e:
            log_akshare_error(test_case['api'], test_case['stock'], e, f"API调用失败")

    # Test with different stocks
    test_stocks = ["000858", "000001", "601318"]
    for stock in test_stocks:
        print(f"\n测试股票: {stock}")
        try:
            result = ak.stock_profit_sheet_by_report_em(stock)
            if result is None:
                log_akshare_error("stock_profit_sheet_by_report_em", stock, Exception("API返回None"), f"股票{stock}利润表接口返回空")
            else:
                print(f"股票{stock}利润表数据获取成功")
        except Exception as e:
            log_akshare_error("stock_profit_sheet_by_report_em", stock, e, f"股票{stock}利润表接口调用失败")

    print(f"\n=== 错误日志汇总 ===")
    error_log_path = os.path.join("data", "cache", "akshare_errors.log")
    if os.path.exists(error_log_path):
        try:
            with open(error_log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                print(f"总共记录了 {len(lines)} 个错误")
                print("\n错误统计:")
                error_stats = {}
                for line in lines:
                    try:
                        error_entry = json.loads(line.strip())
                        api_name = error_entry.get('api_name', 'Unknown')
                        error_stats[api_name] = error_stats.get(api_name, 0) + 1
                    except:
                        pass

                for api_name, count in error_stats.items():
                    print(f"  {api_name}: {count} 次失败")

        except Exception as e:
            print(f"读取错误日志失败: {e}")
    else:
        print("未找到错误日志文件")

if __name__ == "__main__":
    test_akshare_error_logging()