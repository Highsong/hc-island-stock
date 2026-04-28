#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix insights generator to handle None values"""

import sys
import os

def fix_insights_generator():
    """Fix the insights generator to handle None values in growth rates"""
    print("=" * 80)
    print("FIXING INSIGHTS GENERATOR")
    print("=" * 80)

    file_path = 'src/analysis/insights_generator.py'

    # 读取原始文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 备份原始文件
    backup_file = file_path + '.backup'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_file}")

    # 修复None值处理
    old_lines = [
        '        latest_profit_margin = profit_ratios.get("净利润率", [0])[-1] if profit_ratios.get("净利润率") else 0',
        '        latest_revenue_growth = growth_rates.get("营业收入增长率", [0])[-1] if growth_rates.get("营业收入增长率") else 0',
        '        latest_current_ratio = liquidity_ratios.get("流动比率", [0])[-1] if liquidity_ratios.get("流动比率") else 0',
        '        latest_debt_ratio = leverage_ratios.get("资产负债率", [0])[-1] if leverage_ratios.get("资产负债率") else 0'
    ]

    new_lines = [
        '        latest_profit_margin = profit_ratios.get("净利润率", [0])[-1] if profit_ratios.get("净利润率") else 0',
        '        latest_revenue_growth = growth_rates.get("营业收入增长率", [0])[-1] if growth_rates.get("营业收入增长率") else 0',
        '        latest_current_ratio = liquidity_ratios.get("流动比率", [0])[-1] if liquidity_ratios.get("流动比率") else 0',
        '        latest_debt_ratio = leverage_ratios.get("资产负债率", [0])[-1] if leverage_ratios.get("资产负债率") else 0'
    ]

    # 修复格式化问题 - 处理None值
    old_format_line = '        summary.append(f"📊 核心财务指标：净利润率 {latest_profit_margin:.1%}，营收增长率 {latest_revenue_growth:.1%}，流动比率 {latest_current_ratio:.2f}，资产负债率 {latest_debt_ratio:.1%}")'
    new_format_line = '        summary.append(f"📊 核心财务指标：净利润率 {latest_profit_margin:.1%}，营收增长率 {latest_revenue_growth:.1% if latest_revenue_growth is not None else 0:.1%}，流动比率 {latest_current_ratio:.2f}，资产负债率 {latest_debt_ratio:.1%}")'

    if old_format_line in content:
        content = content.replace(old_format_line, new_format_line)
        print("✓ Fixed format string to handle None values")
    else:
        print("✗ Could not find the exact format line to replace")

    # 写入修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✓ Applied fixes to insights generator")
    return True

if __name__ == "__main__":
    success = fix_insights_generator()
    if success:
        print("\n✅ INSIGHTS GENERATOR FIX APPLIED")
    else:
        print("\n❌ FIX FAILED")