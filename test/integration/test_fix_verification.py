#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试修复后的利润表数据处理"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fix_verification():
    """测试修复后的利润表数据处理"""
    print("测试修复后的利润表数据处理")
    print("=" * 80)

    try:
        import akshare as ak
        import pandas as pd
        from datetime import datetime

        stock_code = "600519"
        period = "year"

        print(f"测试目标: 股票{stock_code} 2025年利润表数据")
        print(f"测试时间: {datetime.now().isoformat()}")
        print("=" * 80)

        # 直接调用新浪接口获取数据
        print("\n1. 调用新浪利润表接口:")
        print(f"调用: ak.stock_financial_report_sina('{stock_code}', symbol='利润表')")

        df = ak.stock_financial_report_sina(stock_code, symbol="利润表")
        print(f"接口调用完成，返回类型: {type(df)}")
        print(f"DataFrame形状: {df.shape}")

        if df is not None and not df.empty:
            print(f"\n2. 数据预览:")
            print(f"列名: {list(df.columns)}")
            print(f"前3行数据:")
            print(df.head(3))

            # 检查报告日字段
            if '报告日' in df.columns:
                print(f"\n3. 报告日字段数据:")
                report_dates = df['报告日'].tolist()
                print(f"报告日: {report_dates[:5]}...")

                # 提取2025年的数据
                year_2025_data = [date for date in report_dates if str(date).startswith('2025')]
                print(f"2025年的数据条数: {len(year_2025_data)}")

            # 测试修复后的数据处理逻辑
            print(f"\n4. 测试修复后的数据处理逻辑:")

            def test_process_income_data(df):
                """测试处理利润表数据"""
                result = {}

                try:
                    for _, row in df.iterrows():
                        # 尝试多种可能的字段名来获取报告日期
                        year = str(row.get('报告期', '') or row.get('报告日', ''))
                        if not year or year == 'nan':
                            continue

                        # 从报告日格式（如20251231）中提取年份
                        if len(year) == 8 and year.isdigit():
                            year = year[:4]  # 提取前4位作为年份

                        print(f"处理年份: {year}, 营业收入: {row.get('营业收入', 0)}")

                        result[year] = {
                            '营业收入': [float(row.get('营业收入', 0)) if pd.notna(row.get('营业收入', 0)) else 0],
                            '净利润': [float(row.get('净利润', 0)) if pd.notna(row.get('净利润', 0)) else 0],
                            '营业成本': [float(row.get('营业成本', 0)) if pd.notna(row.get('营业成本', 0)) else 0],
                            '销售费用': [float(row.get('销售费用', 0)) if pd.notna(row.get('销售费用', 0)) else 0],
                            '管理费用': [float(row.get('管理费用', 0)) if pd.notna(row.get('管理费用', 0)) else 0],
                            '财务费用': [float(row.get('财务费用', 0)) if pd.notna(row.get('财务费用', 0)) else 0]
                        }
                except Exception as e:
                    print(f"处理数据时出错: {e}")

                return result

            processed_data = test_process_income_data(df)

            print(f"\n5. 处理结果:")
            print(f"处理后的年份数量: {len(processed_data)}")

            if processed_data:
                print("处理后的数据:")
                for year, data in processed_data.items():
                    print(f"  {year}年: 营业收入={data['营业收入'][0]:,.2f}, 净利润={data['净利润'][0]:,.2f}")

                # 检查2025年数据
                if '2025' in processed_data:
                    print(f"\n6. 2025年数据验证:")
                    data_2025 = processed_data['2025']
                    print(f"2025年营业收入: {data_2025['营业收入'][0]:,.2f}")
                    print(f"2025年净利润: {data_2025['净利润'][0]:,.2f}")
                    print("✅ 2025年数据成功提取！")
                else:
                    print("❌ 2025年数据未找到")
            else:
                print("❌ 未能处理任何数据")

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
    test_fix_verification()