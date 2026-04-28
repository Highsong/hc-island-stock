#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基本功能的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_basic_functionality():
    """测试基本功能"""
    print("开始测试基本功能...")

    try:
        # 导入必要的模块
        from src.data_extraction.stock_data_source import StockDataSource
        from src.utils.cache_manager import cache_manager
        from src.analysis.financial_metrics import FinancialMetrics

        # 测试数据源
        print("1. 测试股票数据源...")
        data_source = StockDataSource()

        # 测试股票信息获取
        try:
            stock_info = data_source.get_stock_info("600519")
            print(f"   [OK] 股票信息获取: {stock_info.get('name', 'Unknown')} ({stock_info.get('market', 'Unknown')})")
        except Exception as e:
            print(f"   [WARN] 股票信息获取失败: {e}")

        # 测试缓存
        print("2. 测试缓存功能...")
        try:
            test_data = {"test": "data", "timestamp": "2024-01-01"}
            cache_manager.set(test_data, "test", "basic_test")
            cached_data = cache_manager.get("test", "basic_test")
            if cached_data == test_data:
                print("   [OK] 缓存功能正常")
            else:
                print("   [FAIL] 缓存数据不匹配")
        except Exception as e:
            print(f"   [FAIL] 缓存测试失败: {e}")

        # 测试财务指标计算
        print("3. 测试财务指标计算...")
        try:
            metrics = FinancialMetrics()

            # 测试盈利能力比率计算
            test_income_data = {
                '营业收入': [1000, 1200, 1400],
                '净利润': [100, 150, 200],
                '营业成本': [600, 700, 800]
            }

            profitability = metrics.calculate_profitability_ratios(test_income_data)
            print(f"   [OK] 盈利能力指标计算: {profitability}")

            # 测试增长率计算
            growth_rates = metrics.calculate_growth_rates(test_income_data)
            print(f"   [OK] 增长率计算: {growth_rates}")

        except Exception as e:
            print(f"   [FAIL] 财务指标计算失败: {e}")
            import traceback
            traceback.print_exc()

        # 测试图表生成
        print("4. 测试图表生成...")
        try:
            from src.visualization.chart_generator import ChartGenerator
            chart_gen = ChartGenerator()

            # 创建测试数据
            test_data = {
                '周期': ['2020', '2021', '2022'],
                '营业收入': [1000.0, 1200.0, 1400.0]
            }

            chart = chart_gen.create_line_chart(test_data, '营业收入', '测试营收趋势')
            if chart is not None:
                print("   [OK] 图表生成成功")
            else:
                print("   [FAIL] 图表生成失败")

        except Exception as e:
            print(f"   [FAIL] 图表生成测试失败: {e}")

        print("\n[OK] 基本功能测试完成!")
        return True

    except Exception as e:
        print(f"\n[FAIL] 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)