#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试货币格式化功能"""

def test_currency_formatting():
    """测试货币格式化"""
    print("测试货币格式化功能")
    print("=" * 60)

    # 模拟格式化函数
    def format_currency(amount):
        """格式化货币金额，自动选择合适的单位"""
        if amount >= 100000000:  # >= 1亿
            return f"{amount / 100000000:.2f}亿"
        elif amount >= 10000:  # >= 1万
            return f"{amount / 10000:.2f}万"
        else:
            return f"{amount:.2f}"

    # 测试用例
    test_cases = [
        (168838102514.79, "1688.38亿"),  # 贵州茅台2025年营收
        (85310324833.67, "853.10亿"),   # 贵州茅台2025年归母净利润
        (50000000, "5000.00万"),        # 5000万
        (1000000, "100.00万"),          # 100万
        (50000, "5.00万"),              # 5万
        (1000, "1000.00"),              # 1000
    ]

    print("测试用例:")
    all_passed = True

    for amount, expected in test_cases:
        result = format_currency(amount)
        passed = result == expected
        status = "PASS" if passed else "FAIL"

        print(f"  {status} {amount:,.2f} -> {result} (期望: {expected})")
        if not passed:
            all_passed = False

    print(f"\n总体结果: {'全部通过' if all_passed else '有失败用例'}")

    # 特别测试贵州茅台的数据
    print(f"\n贵州茅台2025年数据:")
    revenue = 168838102514.79
    net_profit = 85310324833.67

    print(f"  营业收入: {revenue:,.2f} -> {format_currency(revenue)}")
    print(f"  归母净利润: {net_profit:,.2f} -> {format_currency(net_profit)}")

    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    test_currency_formatting()