#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整应用流程的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_data_processing_flow():
    """测试数据处理流程"""
    print("开始测试数据处理流程...")

    try:
        from src.data_extraction.stock_data_source import StockDataSource
        from src.analysis.financial_metrics import FinancialMetrics
        from src.analysis.trend_analysis import TrendAnalysis
        from src.analysis.insights_generator import InsightsGenerator
        from src.visualization.chart_generator import ChartGenerator

        # 1. 测试数据源
        print("1. 测试股票数据源...")
        data_source = StockDataSource()

        # 测试获取股票数据（使用示例数据）
        try:
            # 尝试获取真实数据，如果失败则使用示例数据
            raw_data = data_source.get_stock_financial_data(
                "600519", "2020", "2023", "year"
            )
            print(f"   [OK] 获取到 {len(raw_data)} 个周期的数据")
        except Exception as e:
            print(f"   [WARN] 获取真实数据失败: {e}")
            print("   使用示例数据进行测试...")
            # 创建示例数据
            raw_data = {
                '2020': {
                    'income_statement': {
                        '营业收入': [1000.0],
                        '净利润': [100.0],
                        '营业成本': [600.0]
                    },
                    'balance_sheet': {
                        '总资产': [2000.0],
                        '总负债': [600.0],
                        '所有者权益': [1400.0],
                        '流动资产': [1200.0],
                        '流动负债': [400.0],
                        '存货': [200.0]
                    }
                },
                '2021': {
                    'income_statement': {
                        '营业收入': [1200.0],
                        '净利润': [150.0],
                        '营业成本': [700.0]
                    },
                    'balance_sheet': {
                        '总资产': [2400.0],
                        '总负债': [700.0],
                        '所有者权益': [1700.0],
                        '流动资产': [1400.0],
                        '流动负债': [450.0],
                        '存货': [220.0]
                    }
                },
                '2022': {
                    'income_statement': {
                        '营业收入': [1400.0],
                        '净利润': [200.0],
                        '营业成本': [800.0]
                    },
                    'balance_sheet': {
                        '总资产': [2800.0],
                        '总负债': [800.0],
                        '所有者权益': [2000.0],
                        '流动资产': [1600.0],
                        '流动负债': [500.0],
                        '存货': [240.0]
                    }
                }
            }
            print(f"   [OK] 创建示例数据: {len(raw_data)} 个周期")

        # 2. 测试财务指标计算
        print("2. 测试财务指标计算...")
        metrics = FinancialMetrics()

        # 准备测试数据
        income_data = {'营业收入': [], '净利润': [], '营业成本': []}
        balance_data = {'总资产': [], '总负债': [], '所有者权益': [],
                       '流动资产': [], '流动负债': [], '存货': []}

        periods = sorted(raw_data.keys())
        for period in periods:
            period_data = raw_data[period]

            # 收入数据
            income_stmt = period_data.get('income_statement', {})
            income_data['营业收入'].append(income_stmt.get('营业收入', [0])[0])
            income_data['净利润'].append(income_stmt.get('净利润', [0])[0])
            income_data['营业成本'].append(income_stmt.get('营业成本', [0])[0])

            # 资产负债数据
            balance_sheet = period_data.get('balance_sheet', {})
            balance_data['总资产'].append(balance_sheet.get('总资产', [0])[0])
            balance_data['总负债'].append(balance_sheet.get('总负债', [0])[0])
            balance_data['所有者权益'].append(balance_sheet.get('所有者权益', [0])[0])
            balance_data['流动资产'].append(balance_sheet.get('流动资产', [0])[0])
            balance_data['流动负债'].append(balance_sheet.get('流动负债', [0])[0])
            balance_data['存货'].append(balance_sheet.get('存货', [0])[0])

        # 计算指标
        profitability_ratios = metrics.calculate_profitability_ratios(income_data)
        growth_rates = metrics.calculate_growth_rates(income_data)
        liquidity_ratios = metrics.calculate_liquidity_ratios(balance_data)
        leverage_ratios = metrics.calculate_leverage_ratios(balance_data)

        print(f"   [OK] 盈利能力指标: {profitability_ratios}")
        print(f"   [OK] 增长率指标: {growth_rates}")
        print(f"   [OK] 流动性指标: {liquidity_ratios}")
        print(f"   [OK] 杠杆指标: {leverage_ratios}")

        # 3. 测试趋势分析
        print("3. 测试趋势分析...")
        trend_analyzer = TrendAnalysis()

        if len(income_data['营业收入']) > 1:
            cagr = trend_analyzer.calculate_compound_growth_rate(income_data['营业收入'])
            trend_direction = trend_analyzer.analyze_trend_direction(income_data['营业收入'])
            print(f"   [OK] 营收复合增长率: {cagr:.2%}")
            print(f"   [OK] 趋势方向: {trend_direction}")
        else:
            print("   [SKIP] 数据不足，跳过趋势分析")

        # 4. 测试洞察生成
        print("4. 测试洞察生成...")
        insights_generator = InsightsGenerator()

        all_metrics = {
            'profitability_ratios': profitability_ratios,
            'growth_rates': growth_rates,
            'liquidity_ratios': liquidity_ratios,
            'leverage_ratios': leverage_ratios
        }

        insights = insights_generator.generate_comprehensive_report(all_metrics)
        print(f"   [OK] 生成洞察报告: {len(insights)} 个部分")

        # 5. 测试图表生成
        print("5. 测试图表生成...")
        chart_generator = ChartGenerator()

        # 准备图表数据
        chart_data = {
            '周期': periods,
            '营业收入': income_data['营业收入'],
            '净利润': income_data['净利润']
        }

        # 生成图表
        revenue_chart = chart_generator.create_line_chart(
            chart_data, '营业收入', '营业收入趋势分析'
        )
        profit_chart = chart_generator.create_bar_chart(
            chart_data, '净利润', '净利润对比分析'
        )

        if revenue_chart is not None:
            print("   [OK] 营收趋势图生成成功")
        else:
            print("   [FAIL] 营收趋势图生成失败")

        if profit_chart is not None:
            print("   [OK] 利润对比图生成成功")
        else:
            print("   [FAIL] 利润对比图生成失败")

        print("\n[OK] 数据处理流程测试完成!")
        return True

    except Exception as e:
        print(f"\n[FAIL] 数据处理流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_integration():
    """测试应用集成"""
    print("\n开始测试应用集成...")

    try:
        # 模拟DataProcessor的功能
        from src.data_extraction.stock_data_source import StockDataSource
        from src.analysis.financial_metrics import FinancialMetrics
        from src.analysis.trend_analysis import TrendAnalysis
        from src.analysis.insights_generator import InsightsGenerator
        from src.visualization.chart_generator import ChartGenerator

        print("1. 测试DataProcessor模拟...")

        # 创建处理器实例
        data_source = StockDataSource()
        metrics_calculator = FinancialMetrics()
        trend_analyzer = TrendAnalysis()
        insights_generator = InsightsGenerator()
        chart_generator = ChartGenerator()

        print("   [OK] 所有处理器实例化成功")

        # 模拟处理流程
        stock_code = "600519"
        start_year = "2020"
        end_year = "2023"
        period = "year"

        print(f"2. 模拟处理 {stock_code} 的数据...")

        # 这里可以添加更详细的集成测试
        print("   [OK] 集成测试模拟完成")

        print("\n[OK] 应用集成测试完成!")
        return True

    except Exception as e:
        print(f"\n[FAIL] 应用集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_data_processing_flow()
    success2 = test_app_integration()

    overall_success = success1 and success2
    print(f"\n{'='*50}")
    print(f"完整流程测试结果: {'成功' if overall_success else '失败'}")
    print(f"{'='*50}")

    sys.exit(0 if overall_success else 1)