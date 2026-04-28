#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix growth rates handling in insights generator"""

import sys
import os

def fix_growth_rates_handling():
    """Fix the insights generator to properly handle None values in growth rates"""
    print("=" * 80)
    print("FIXING GROWTH RATES HANDLING")
    print("=" * 80)

    file_path = 'src/analysis/insights_generator.py'

    # 读取原始文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 备份原始文件
    backup_file = file_path + '.backup2'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_file}")

    # 修复增长率处理逻辑
    old_section = '''        # 获取最新指标
        profit_ratios = metrics.get('profitability_ratios', {})
        growth_rates = metrics.get('growth_rates', {})
        liquidity_ratios = metrics.get('liquidity_ratios', {})
        leverage_ratios = metrics.get('leverage_ratios', {})

        latest_profit_margin = profit_ratios.get('净利润率', [0])[-1] if profit_ratios.get('净利润率') else 0
        latest_revenue_growth = growth_rates.get('营业收入增长率', [0])[-1] if growth_rates.get('营业收入增长率') else 0
        latest_current_ratio = liquidity_ratios.get('流动比率', [0])[-1] if liquidity_ratios.get('流动比率') else 0
        latest_debt_ratio = leverage_ratios.get('资产负债率', [0])[-1] if leverage_ratios.get('资产负债率') else 0'''

    new_section = '''        # 获取最新指标
        profit_ratios = metrics.get('profitability_ratios', {})
        growth_rates = metrics.get('growth_rates', {})
        liquidity_ratios = metrics.get('liquidity_ratios', {})
        leverage_ratios = metrics.get('leverage_ratios', {})

        latest_profit_margin = profit_ratios.get('净利润率', [0])[-1] if profit_ratios.get('净利润率') else 0

        # 处理增长率，过滤掉None值
        revenue_growth_list = growth_rates.get('营业收入增长率', [0])
        latest_revenue_growth = 0
        if revenue_growth_list and len(revenue_growth_list) > 0:
            # 过滤掉None值，取最后一个有效值
            valid_growth_rates = [x for x in revenue_growth_list if x is not None]
            if valid_growth_rates:
                latest_revenue_growth = valid_growth_rates[-1]

        latest_current_ratio = liquidity_ratios.get('流动比率', [0])[-1] if liquidity_ratios.get('流动比率') else 0
        latest_debt_ratio = leverage_ratios.get('资产负债率', [0])[-1] if leverage_ratios.get('资产负债率') else 0'''

    if old_section in content:
        content = content.replace(old_section, new_section)
        print("✓ Fixed growth rates handling")
    else:
        print("✗ Could not find the exact section to replace")
        print("Trying alternative approach...")

        # 尝试更简单的替换
        old_line = '        latest_revenue_growth = growth_rates.get("营业收入增长率", [0])[-1] if growth_rates.get("营业收入增长率") else 0'
        new_lines = '''        # 处理增长率，过滤掉None值
        revenue_growth_list = growth_rates.get("营业收入增长率", [0])
        latest_revenue_growth = 0
        if revenue_growth_list and len(revenue_growth_list) > 0:
            # 过滤掉None值，取最后一个有效值
            valid_growth_rates = [x for x in revenue_growth_list if x is not None]
            if valid_growth_rates:
                latest_revenue_growth = valid_growth_rates[-1]'''

        if old_line in content:
            content = content.replace(old_line, new_lines)
            print("✓ Applied alternative fix for growth rates")
        else:
            print("✗ Could not apply alternative fix")
            return False

    # 写入修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✓ Applied fixes to insights generator")
    return True

if __name__ == "__main__":
    success = fix_growth_rates_handling()
    if success:
        print("\n✅ GROWTH RATES FIX APPLIED")
    else:
        print("\n❌ FIX FAILED")