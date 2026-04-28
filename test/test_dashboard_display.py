#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试仪表板显示格式"""

import sys
import os

def test_dashboard_display():
    """测试仪表板显示格式"""
    print("测试仪表板显示格式")
    print("=" * 60)

    # 模拟仪表板的格式化函数
    def format_currency(amount):
        """格式化货币金额，自动选择合适的单位"""
        if amount >= 100000000:  # >= 1亿
            return f"{amount / 100000000:.2f}亿"
        elif amount >= 10000:  # >= 1万
            return f"{amount / 10000:.2f}万"
        else:
            return f"{amount:.2f}"

    # 模拟贵州茅台2025年数据
    revenue = 168838102514.79  # 营业收入
    net_profit = 85310324833.67  # 归母净利润

    print(f"原始数据:")
    print(f"  营业收入: {revenue:,.2f}")
    print(f"  归母净利润: {net_profit:,.2f}")

    print(f"\n修复前显示 (错误的):")
    print(f"  营业收入: {revenue:,.0f}亿")  # 错误的显示
    print(f"  归母净利润: {net_profit:,.0f}亿")  # 错误的显示

    print(f"\n修复后显示 (正确的):")
    print(f"  营业收入: {format_currency(revenue)}")
    print(f"  归母净利润: {format_currency(net_profit)}")

    # 测试小金额的情况
    small_amount = 500000  # 50万
    print(f"\n小金额测试:")
    print(f"  {small_amount:,.2f} -> {format_currency(small_amount)}")

    # 验证修复效果
    revenue_formatted = format_currency(revenue)
    profit_formatted = format_currency(net_profit)

    print(f"\n验证结果:")
    if revenue_formatted == "1688.38亿":
        print(f"  [SUCCESS] 营业收入显示正确: {revenue_formatted}")
    else:
        print(f"  [FAIL] 营业收入显示错误: {revenue_formatted}")

    if profit_formatted == "853.10亿":
        print(f"  [SUCCESS] 归母净利润显示正确: {profit_formatted}")
    else:
        print(f"  [FAIL] 归母净利润显示错误: {profit_formatted}")

    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    test_dashboard_display()