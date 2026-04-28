#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试显示修复 - 验证营业收入单位和归母净利润"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_display_fix():
    """测试显示修复"""
    print("测试显示修复")
    print("=" * 80)

    try:
        import akshare as ak
        import pandas as pd

        stock_code = "600519"

        print(f"测试目标: 股票{stock_code} 显示格式修复")
        print(f"测试时间: {datetime.now().isoformat()}")
        print("=" * 80)

        # 直接调用新浪接口获取数据
        print("\n1. 调用新浪利润表接口:")
        df = ak.stock_financial_report_sina(stock_code, symbol="利润表")

        if df is not None and not df.empty:
            # 获取2025年数据
            df_2025 = df[df['报告日'].astype(str).str.startswith('2025')]

            if len(df_2025) > 0:
                first_row = df_2025.iloc[0]

                # 测试数据提取
                revenue = first_row.get('营业收入', 0)  # 营业收入
                net_profit = first_row.get('归属于母公司股东的净利润', 0) or first_row.get('净利润', 0)  # 归母净利润

                print(f"\n2. 原始数据:")
                print(f"营业收入: {revenue:,.2f} ({revenue/1e8:.2f}亿)")
                print(f"归母净利润: {net_profit:,.2f} ({net_profit/1e8:.2f}亿)")

                # 测试显示格式
                revenue_in_billions = revenue / 100000000  # 转换为亿元
                net_profit_in_billions = net_profit / 100000000  # 转换为亿元

                print(f"\n3. 修复后显示格式:")
                print(f"营业收入显示: {revenue_in_billions:.2f}亿")
                print(f"归母净利润显示: {net_profit_in_billions:.2f}亿")

                # 验证修复效果
                print(f"\n4. 验证结果:")
                if revenue_in_billions == 1688.38:
                    print(f"  [SUCCESS] 营业收入显示正确: ¥{revenue_in_billions:.2f}亿")
                else:
                    print(f"  [FAIL] 营业收入显示错误: {revenue_in_billions:.2f}亿 (期望: 1688.38亿)")

                if abs(net_profit_in_billions - 823.20) < 1.0:  # 允许1亿误差
                    print(f"  [SUCCESS] 归母净利润显示正确: ¥{net_profit_in_billions:.2f}亿")
                else:
                    print(f"  [FAIL] 归母净利润显示错误: {net_profit_in_billions:.2f}亿 (期望: 823.20亿)")

        else:
            print("❌ 未能获取到数据")

    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*80}")
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_display_fix()