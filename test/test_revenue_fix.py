#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试营业收入字段修复"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_revenue_fix():
    """测试营业收入字段修复"""
    print("测试营业收入字段修复")
    print("=" * 80)

    try:
        import akshare as ak
        import pandas as pd

        stock_code = "600519"

        print(f"测试目标: 股票{stock_code} 2025年营业收入数据")
        print(f"测试时间: {datetime.now().isoformat()}")
        print("=" * 80)

        # 直接调用新浪接口获取数据
        print("\n1. 调用新浪利润表接口:")
        print(f"调用: ak.stock_financial_report_sina('{stock_code}', symbol='利润表')")

        df = ak.stock_financial_report_sina(stock_code, symbol="利润表")
        print(f"接口调用完成，返回类型: {type(df)}")
        print(f"DataFrame形状: {df.shape}")

        if df is not None and not df.empty:
            print(f"\n2. 数据字段检查:")
            columns = list(df.columns)
            print(f"可用字段: {columns}")

            # 检查关键字段
            revenue_fields = ['营业总收入', '营业收入', '净利润']
            for field in revenue_fields:
                if field in columns:
                    print(f"  [OK] 字段 '{field}' 存在")
                else:
                    print(f"  [FAIL] 字段 '{field}' 不存在")

            # 检查2025年数据
            if '报告日' in columns:
                print(f"\n3. 2025年数据检查:")
                df_2025 = df[df['报告日'].astype(str).str.startswith('2025')]
                print(f"2025年数据条数: {len(df_2025)}")

                if len(df_2025) > 0:
                    first_row = df_2025.iloc[0]
                    print(f"\n4. 2025年第一条数据详情:")
                    print(f"报告日: {first_row.get('报告日', 'N/A')}")

                    # 检查不同字段名的值
                    total_revenue = first_row.get('营业总收入', 0)
                    revenue = first_row.get('营业收入', 0)
                    net_profit = first_row.get('净利润', 0)

                    print(f"营业总收入: {total_revenue:,.2f} ({total_revenue/1e8:.2f}亿)")
                    print(f"营业收入: {revenue:,.2f} ({revenue/1e8:.2f}亿)")
                    print(f"净利润: {net_profit:,.2f} ({net_profit/1e8:.2f}亿)")

                    # 验证哪个是正确的
                    print(f"\n5. 数据验证:")
                    expected_revenue = 1688.38 * 1e8  # 1688.38亿
                    tolerance = 0.01 * 1e8  # 1%容差

                    if abs(total_revenue - expected_revenue) < tolerance:
                        print(f"  [OK] 营业总收入匹配预期值1688.38亿")
                    else:
                        print(f"  [FAIL] 营业总收入不匹配预期值1688.38亿")

                    if abs(revenue - expected_revenue) < tolerance:
                        print(f"  [OK] 营业收入匹配预期值1688.38亿")
                    else:
                        print(f"  [FAIL] 营业收入不匹配预期值1688.38亿")

                    # 测试修复后的处理逻辑
                    print(f"\n6. 测试修复后的处理逻辑:")
                    def test_fixed_processing(row):
                        # 修复后的逻辑：优先使用营业总收入，如果没有则使用营业收入
                        final_revenue = row.get('营业总收入', 0) or row.get('营业收入', 0)
                        return final_revenue

                    fixed_revenue = test_fixed_processing(first_row)
                    print(f"修复后获取的营业收入: {fixed_revenue:,.2f} ({fixed_revenue/1e8:.2f}亿)")

                    if abs(fixed_revenue - expected_revenue) < tolerance:
                        print(f"  [SUCCESS] 修复后的处理逻辑正确！")
                    else:
                        print(f"  [FAIL] 修复后的处理逻辑仍有问题")

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
    test_revenue_fix()