#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix data structure issues in the stock analysis system"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from data_extraction.stock_data_source import StockDataSource

def fix_data_structure_issues():
    """Fix the data structure handling issues"""
    print("=" * 80)
    print("FIXING DATA STRUCTURE ISSUES")
    print("=" * 80)

    # 问题分析：
    print("\n1. PROBLEM ANALYSIS:")
    print("- Data is returned as quarterly data even when period='year'")
    print("- Expected structure: {'income_statement': {...}, 'balance_sheet': {...}}")
    print("- Actual structure: {'Q1': {...}, 'Q2': {...}, 'Q3': {...}, 'Q4': {...}}")
    print("- Code tries to access period_data['income_statement'] but finds quarterly keys instead")

    # 解决方案：
    print("\n2. SOLUTION:")
    print("- Modify _normalize_data_structure to handle quarterly data when period='year'")
    print("- Aggregate quarterly data to annual when needed")
    print("- Ensure proper data structure for analysis")

    print("\n3. IMPLEMENTATION:")

    # 读取原始文件
    source_file = 'src/data_extraction/stock_data_source.py'
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 备份原始文件
    backup_file = source_file + '.backup'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_file}")

    # 修复_normalize_data_structure方法
    old_method = '''    def _normalize_data_structure(self, data: Dict, period: str) -> Dict:
        """标准化数据结构"""
        normalized = {}

        for year, year_data in data.items():
            if isinstance(year_data, dict):
                if period == 'quarter':
                    # 季度数据，保持原有的季度结构
                    normalized[year] = {}
                    for quarter, quarter_data in year_data.items():
                        if isinstance(quarter_data, dict):
                            # 合并所有数据源
                            combined_data = {}

                            # 添加利润表数据
                            for key, value in quarter_data.items():
                                if key not in ['balance_sheet', 'cash_flow']:
                                    combined_data[key] = value

                            # 添加资产负债表数据
                            if 'balance_sheet' in quarter_data:
                                combined_data['balance_sheet'] = quarter_data['balance_sheet']

                            # 添加现金流量表数据
                            if 'cash_flow' in quarter_data:
                                combined_data['cash_flow'] = quarter_data['cash_flow']

                            normalized[year][quarter] = combined_data
                        else:
                            normalized[year][quarter] = quarter_data
                else:
                    # 年度数据，转换为数组格式
                    if any(key in year_data for key in ['营业收入', '净利润']):
                        # 这是利润表格式的数据
                        normalized[year] = {
                            'income_statement': {k: [v] for k, v in year_data.items() if k not in ['balance_sheet', 'cash_flow']}
                        }
                        if 'balance_sheet' in year_data:
                            normalized[year]['balance_sheet'] = {k: [v] for k, v in year_data['balance_sheet'].items()}
                        if 'cash_flow' in year_data:
                            normalized[year]['cash_flow'] = {k: [v] for k, v in year_data['cash_flow'].items()}
                    else:
                        # 已经是正确格式的数据
                        normalized[year] = year_data
            else:
                normalized[year] = year_data

        return normalized'''

    new_method = '''    def _normalize_data_structure(self, data: Dict, period: str) -> Dict:
        """标准化数据结构"""
        normalized = {}

        for year, year_data in data.items():
            if isinstance(year_data, dict):
                if period == 'quarter':
                    # 季度数据，保持原有的季度结构
                    normalized[year] = {}
                    for quarter, quarter_data in year_data.items():
                        if isinstance(quarter_data, dict):
                            # 合并所有数据源
                            combined_data = {}

                            # 添加利润表数据
                            for key, value in quarter_data.items():
                                if key not in ['balance_sheet', 'cash_flow']:
                                    combined_data[key] = value

                            # 添加资产负债表数据
                            if 'balance_sheet' in quarter_data:
                                combined_data['balance_sheet'] = quarter_data['balance_sheet']

                            # 添加现金流量表数据
                            if 'cash_flow' in quarter_data:
                                combined_data['cash_flow'] = quarter_data['cash_flow']

                            normalized[year][quarter] = combined_data
                        else:
                            normalized[year][quarter] = quarter_data
                else:
                    # 年度数据，检查是否包含季度数据
                    if any(key.startswith('Q') for key in year_data.keys()):
                        # 包含季度数据，需要聚合为年度数据
                        annual_data = self._aggregate_quarterly_to_annual(year_data)
                        normalized[year] = annual_data
                    elif any(key in year_data for key in ['营业收入', '净利润']):
                        # 这是利润表格式的数据
                        normalized[year] = {
                            'income_statement': {k: [v] for k, v in year_data.items() if k not in ['balance_sheet', 'cash_flow']}
                        }
                        if 'balance_sheet' in year_data:
                            normalized[year]['balance_sheet'] = {k: [v] for k, v in year_data['balance_sheet'].items()}
                        if 'cash_flow' in year_data:
                            normalized[year]['cash_flow'] = {k: [v] for k, v in year_data['cash_flow'].items()}
                    else:
                        # 已经是正确格式的数据
                        normalized[year] = year_data
            else:
                normalized[year] = year_data

        return normalized

    def _aggregate_quarterly_to_annual(self, quarterly_data: Dict) -> Dict:
        """将季度数据聚合为年度数据"""
        annual_data = {
            'income_statement': {
                '营业收入': [0],
                '净利润': [0],
                '营业成本': [0],
                '销售费用': [0],
                '管理费用': [0],
                '财务费用': [0]
            },
            'balance_sheet': {
                '总资产': [0],
                '总负债': [0],
                '所有者权益': [0],
                '流动资产': [0],
                '流动负债': [0],
                '存货': [0],
                '货币资金': [0]
            },
            'cash_flow': {
                '经营活动现金流': [0],
                '投资活动现金流': [0],
                '筹资活动现金流': [0],
                '现金净增加额': [0]
            }
        }

        # 聚合利润表和现金流量表数据（相加）
        flow_items = ['营业收入', '净利润', '营业成本', '销售费用', '管理费用', '财务费用',
                     '经营活动现金流', '投资活动现金流', '筹资活动现金流', '现金净增加额']

        for quarter, quarter_data in quarterly_data.items():
            if not isinstance(quarter_data, dict):
                continue

            # 聚合利润表数据
            for item in ['营业收入', '净利润', '营业成本', '销售费用', '管理费用', '财务费用']:
                if item in quarter_data:
                    annual_data['income_statement'][item][0] += quarter_data[item]

            # 聚合现金流量表数据
            if 'cash_flow' in quarter_data and isinstance(quarter_data['cash_flow'], dict):
                for item in ['经营活动现金流', '投资活动现金流', '筹资活动现金流', '现金净增加额']:
                    if item in quarter_data['cash_flow']:
                        annual_data['cash_flow'][item][0] += quarter_data['cash_flow'][item]

        # 使用Q4的资产负债表数据作为年度数据
        if 'Q4' in quarterly_data and isinstance(quarterly_data['Q4'], dict):
            q4_data = quarterly_data['Q4']
            if 'balance_sheet' in q4_data and isinstance(q4_data['balance_sheet'], dict):
                for item in ['总资产', '总负债', '所有者权益', '流动资产', '流动负债', '存货', '货币资金']:
                    if item in q4_data['balance_sheet']:
                        annual_data['balance_sheet'][item][0] = q4_data['balance_sheet'][item]
            else:
                # 如果没有balance_sheet包装层，直接从Q4数据中提取
                for item in ['总资产', '总负债', '所有者权益', '流动资产', '流动负债', '存货', '货币资金']:
                    if item in q4_data:
                        annual_data['balance_sheet'][item][0] = q4_data[item]

        return annual_data'''

    # 替换方法
    if old_method in content:
        content = content.replace(old_method, new_method)
        print("✓ Updated _normalize_data_structure method")
    else:
        print("✗ Could not find the exact method to replace")
        return False

    # 写入修复后的文件
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✓ Applied fixes to data structure handling")
    print("\n4. SUMMARY:")
    print("- Added _aggregate_quarterly_to_annual method to handle quarterly data")
    print("- Modified _normalize_data_structure to detect and handle quarterly data when period='year'")
    print("- Ensured proper data structure for financial analysis")

    return True

if __name__ == "__main__":
    success = fix_data_structure_issues()
    if success:
        print("\n✅ FIX APPLIED SUCCESSFULLY")
    else:
        print("\n❌ FIX FAILED")