#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整演示调试功能 - 针对股票600519的2025年利润表数据"""

import sys
import os
import json
from datetime import datetime

def demo_complete_debug():
    """完整演示调试功能"""
    print("完整演示调试功能")
    print("=" * 80)

    try:
        import akshare as ak
        print(f"AKShare版本: {getattr(ak, '__version__', 'Unknown')}")
    except ImportError as e:
        print(f"AKShare导入失败: {e}")
        return

    stock_code = "600519"  # 贵州茅台
    period = "year"
    target_year = "2025"

    print(f"\n演示目标: 获取股票 {stock_code} {target_year} 年利润表数据")
    print(f"演示时间: {datetime.now().isoformat()}")
    print("=" * 80)

    # 模拟我们修改后的完整调试输出
    print("\n1. 股票财务数据请求详情:")
    print("-" * 60)
    request_details = {
        "股票代码": stock_code,
        "开始年份": target_year,
        "结束年份": target_year,
        "数据周期": period,
        "强制刷新": True,
        "请求时间": datetime.now().isoformat()
    }
    print(json.dumps(request_details, ensure_ascii=False, indent=2))

    print("\n2. 开始获取A股财务数据:")
    print("-" * 60)
    print(f"原始股票代码: {stock_code}")
    print(f"标准化代码: {stock_code}")
    print(f"开始年份: {target_year}")
    print(f"结束年份: {target_year}")
    print(f"数据周期: {period}")

    print("\n3. 开始获取利润表数据:")
    print("-" * 60)

    print("\n4. 准备调用利润表接口:")
    print("-" * 60)
    print(f"股票代码: {stock_code}")
    print(f"数据周期: {period}")
    print(f"目标年份: {target_year}")
    print(f"接口调用时间: {datetime.now().isoformat()}")

    # 东方财富接口
    print("\n5. 东方财富接口输入报文参数:")
    print("-" * 60)
    eastmoney_params = {
        "stock_code": stock_code,
        "period": period,
        "target_year": target_year,
        "api_name": "ak.stock_profit_sheet_by_report_em"
    }
    print(json.dumps(eastmoney_params, ensure_ascii=False, indent=2))

    try:
        print(f"\n6. 尝试东方财富利润表接口: {stock_code}")
        print(f"调用: ak.stock_profit_sheet_by_report_em('{stock_code}')")

        df = ak.stock_profit_sheet_by_report_em(stock_code)
        print(f"接口调用完成，返回类型: {type(df)}")

        if df is None:
            print("结果: 接口返回None")
        elif hasattr(df, 'empty') and df.empty:
            print("结果: 接口返回空DataFrame")
        else:
            print(f"结果: 成功获取 {len(df)} 条记录")

    except Exception as e:
        print(f"结果: 接口调用失败 - {type(e).__name__}: {e}")

        # 新浪接口
        print(f"\n7. 新浪接口输入报文参数:")
        print("-" * 60)
        sina_params = {
            "stock_code": stock_code,
            "symbol": "利润表",
            "period": period,
            "target_year": target_year,
            "api_name": "ak.stock_financial_report_sina"
        }
        print(json.dumps(sina_params, ensure_ascii=False, indent=2))

        try:
            print(f"\n8. 尝试新浪利润表接口: {stock_code}")
            print(f"调用: ak.stock_financial_report_sina('{stock_code}', symbol='利润表')")

            df = ak.stock_financial_report_sina(stock_code, symbol="利润表")
            print(f"接口调用完成，返回类型: {type(df)}")

            if df is None:
                print("结果: 接口返回None")
            elif hasattr(df, 'empty') and df.empty:
                print("结果: 接口返回空DataFrame")
            else:
                print(f"结果: 成功获取 {len(df)} 条记录")
                print(f"数据形状: {df.shape}")

        except Exception as e2:
            print(f"结果: 新浪接口调用失败 - {type(e2).__name__}: {e2}")

    print("\n" + "=" * 80)
    print("调试演示完成")
    print("\n总结: 通过以上调试输出，我们可以清楚地看到:")
    print("1. 完整的请求参数和报文信息")
    print("2. 每个API调用的具体参数")
    print("3. 调用前后的状态信息")
    print("4. 错误发生的具体位置和原因")
    print("\n这有助于快速定位和解决接口调用问题。")
    print("=" * 80)

if __name__ == "__main__":
    demo_complete_debug()