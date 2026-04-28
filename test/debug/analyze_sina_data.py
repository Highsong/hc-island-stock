#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze Sina interface data quality"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def analyze_sina_data():
    """Analyze the actual data returned by Sina interface"""
    print("=" * 80)
    print("SINA INTERFACE DATA ANALYSIS")
    print("=" * 80)

    try:
        import akshare as ak
        import pandas as pd
        import numpy as np

        stock_code = "600519"
        print(f"分析股票: {stock_code}")
        print()

        # 调用新浪接口
        print("调用新浪利润表接口...")
        df = ak.stock_financial_report_sina(stock_code, symbol="利润表")

        print(f"返回数据类型: {type(df)}")
        print(f"DataFrame形状: {df.shape}")
        print(f"是否为空: {df.empty}")
        print()

        if df is not None and not df.empty:
            # 1. 基本统计
            print("=== 基本统计 ===")
            print(f"总行数: {len(df)}")
            print(f"总列数: {len(df.columns)}")
            print(f"总数据点数: {df.size}")

            # 2. NaN值分析
            print("\n=== NaN值分析 ===")
            total_nan = df.isnull().sum().sum()
            total_cells = df.size
            nan_percentage = (total_nan / total_cells) * 100

            print(f"NaN值总数: {total_nan}")
            print(f"总数据点数: {total_cells}")
            print(f"NaN值比例: {nan_percentage:.2f}%")

            # 3. 每列的NaN分析
            print("\n=== 列分析 (NaN值最多的10列) ===")
            nan_by_column = df.isnull().sum()
            nan_by_column = nan_by_column.sort_values(ascending=False)

            for col, nan_count in nan_by_column.head(10).items():
                col_total = len(df)
                nan_pct = (nan_count / col_total) * 100
                print(f"{col}: {nan_count}/{col_total} ({nan_pct:.1f}% NaN)")

            # 4. 有数据的列
            print("\n=== 有数据的列 (NaN最少的10列) ===")
            valid_columns = nan_by_column.sort_values(ascending=True)

            for col, nan_count in valid_columns.head(10).items():
                if nan_count < len(df):  # 有实际数据
                    col_total = len(df)
                    valid_pct = ((col_total - nan_count) / col_total) * 100
                    print(f"{col}: {col_total - nan_count}/{col_total} ({valid_pct:.1f}% 有效)")

            # 5. 数据示例
            print("\n=== 数据示例 ===")
            # 找一些有数据的列来展示
            data_columns = [col for col in df.columns if df[col].notna().any()]

            if data_columns:
                print("有数据的前5列示例:")
                sample_cols = data_columns[:5]
                for col in sample_cols:
                    non_nan_values = df[col].dropna()
                    if len(non_nan_values) > 0:
                        print(f"\n列 '{col}':")
                        print(f"  数据类型: {df[col].dtype}")
                        print(f"  非NaN值数量: {len(non_nan_values)}")
                        print(f"  示例值: {non_nan_values.iloc[0]}")
                        if len(non_nan_values) > 1:
                            print(f"  其他值: {list(non_nan_values.iloc[1:3])}")

            # 6. 时间序列分析
            print("\n=== 时间序列分析 ===")
            date_columns = [col for col in df.columns if '日期' in col or '时间' in col or '期' in col]
            if date_columns:
                for date_col in date_columns:
                    non_nan_dates = df[date_col].dropna()
                    if len(non_nan_dates) > 0:
                        print(f"时间列 '{date_col}': {len(non_nan_dates)} 个有效日期")
                        print(f"  示例: {list(non_nan_dates.iloc[:3])}")

            # 7. 数值列分析
            print("\n=== 数值列分析 ===")
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            print(f"数值列数量: {len(numeric_columns)}")

            if numeric_columns:
                print("前5个数值列的统计:")
                for col in numeric_columns[:5]:
                    non_nan_numeric = df[col].dropna()
                    if len(non_nan_numeric) > 0:
                        print(f"  {col}:")
                        print(f"    非零值数量: {len(non_nan_numeric)}")
                        print(f"    平均值: {non_nan_numeric.mean():.2f}")
                        print(f"    最大值: {non_nan_numeric.max():.2f}")
                        print(f"    最小值: {non_nan_numeric.min():.2f}")

            # 8. 数据质量评估
            print("\n=== 数据质量评估 ===")
            valid_data_points = total_cells - total_nan
            data_quality_score = (valid_data_points / total_cells) * 100

            print(f"数据质量评分: {data_quality_score:.1f}%")

            if data_quality_score > 70:
                print("[良好] 数据质量较好，可以用于分析")
            elif data_quality_score > 40:
                print("[一般] 数据质量一般，需要数据清洗")
            else:
                print("[较差] 数据质量较差，建议寻找其他数据源")

            # 9. 建议
            print("\n=== 建议 ===")
            if data_quality_score > 50:
                print("1. 新浪接口数据质量可接受")
                print("2. 建议进行数据清洗，处理NaN值")
                print("3. 可以继续使用新浪接口")
            else:
                print("1. 新浪接口数据质量较差")
                print("2. 建议寻找其他数据源")
                print("3. 或者使用示例数据进行演示")

        else:
            print("❌ 没有获取到数据")

    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)

if __name__ == "__main__":
    analyze_sina_data()