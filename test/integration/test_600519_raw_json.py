#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试600519股票利润表原始报文JSON打印功能"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_600519_raw_json():
    """测试600519股票利润表原始报文JSON打印"""
    print("测试600519股票利润表原始报文JSON打印功能")
    print("=" * 80)

    try:
        # 直接导入需要的模块来避免缓存管理器问题
        import json
        from datetime import datetime
        import pandas as pd

        # 创建一个简化版本的测试
        import akshare as ak

        stock_code = "600519"
        period = "year"

        print(f"测试目标: 股票{stock_code} 利润表数据")
        print(f"测试时间: {datetime.now().isoformat()}")
        print("=" * 80)

        # 测试新浪利润表接口并打印原始JSON
        print("\n测试新浪利润表接口:")
        print(f"调用: ak.stock_financial_report_sina('{stock_code}', symbol='利润表')")

        # 打印输入报文
        sina_request_params = {
            "stock_code": stock_code,
            "symbol": "利润表",
            "period": period,
            "target_year": "2025",
            "api_name": "ak.stock_financial_report_sina"
        }
        print(f"新浪接口输入报文参数:")
        print(json.dumps(sina_request_params, ensure_ascii=False, indent=2))

        try:
            df = ak.stock_financial_report_sina(stock_code, symbol="利润表")
            print(f"\n新浪接口调用完成，返回类型: {type(df)}")

            if df is None:
                print("ERROR: 新浪利润表接口返回None")
            elif hasattr(df, 'empty') and df.empty:
                print("ERROR: 新浪利润表接口返回空DataFrame")
            else:
                print(f"SUCCESS: 新浪利润表接口成功: {len(df)} 条记录")
                print(f"DataFrame形状: {df.shape}")

                # 打印原始报文的JSON格式
                print(f"\n{'='*80}")
                print(f"新浪利润表接口原始报文(JSON格式):")
                print(f"{'='*80}")
                try:
                    # 将DataFrame转换为JSON格式并打印
                    json_data = df.to_json(orient='records', force_ascii=False, indent=2)
                    print(json_data[:5000])  # 限制输出长度，避免日志过大
                    if len(json_data) > 5000:
                        print(f"\n... (原始报文共 {len(json_data)} 字符，已截断显示前5000字符)")
                    print(f"{'='*80}\n")

                    # 同时也保存到文件以便分析
                    with open("sina_raw_data.json", "w", encoding="utf-8") as f:
                        f.write(json_data)
                    print(f"完整原始报文已保存到: sina_raw_data.json")

                except Exception as json_error:
                    print(f"转换JSON格式失败: {json_error}")
                    # 如果JSON转换失败，打印DataFrame的基本信息
                    print(f"DataFrame基本信息:")
                    print(f"  行数: {len(df)}")
                    print(f"  列数: {len(df.columns) if hasattr(df, 'columns') else 'Unknown'}")
                    print(f"  列名: {list(df.columns) if hasattr(df, 'columns') else 'Unknown'}")
                    print(f"  前5行数据: {df.head().to_dict() if hasattr(df, 'head') else 'No head'}")

        except Exception as e:
            print(f"ERROR: 新浪利润表接口调用异常: {type(e).__name__}: {e}")

    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*80}")
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_600519_raw_json()