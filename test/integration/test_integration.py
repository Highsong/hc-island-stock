#!/usr/bin/env python3
"""
集成测试 - 测试完整的应用流程
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def test_complete_analysis_flow():
    """测试完整的分析流程"""
    print("测试完整分析流程...")

    try:
        from app_new import DataProcessor

        # 创建处理器
        processor = DataProcessor()

        # 测试不同股票和时间范围
        test_cases = [
            ('600519', '2020', '2024', 'year'),
            ('000858', '2021', '2023', 'year'),
            ('600519', '2022', '2024', 'quarter')
        ]

        for stock_code, start_year, end_year, period in test_cases:
            print(f"  测试 {stock_code} ({start_year}-{end_year}, {period})...")

            result = processor.process_stock_data(stock_code, start_year, end_year, period)

            # 验证结果结构
            assert 'periods' in result, f"缺少periods字段"
            assert 'latest_period' in result, f"缺少latest_period字段"
            assert 'insights' in result, f"缺少insights字段"

            # 验证数据不为空
            assert len(result['periods']) > 0, f"periods为空"

            print(f"    ✅ 成功处理 {len(result['periods'])} 个周期的数据")

        print("✅ 完整分析流程测试通过")
        return True

    except Exception as e:
        print(f"❌ 完整分析流程测试失败: {e}")
        return False

def test_chart_generation():
    """测试图表生成功能"""
    print("测试图表生成...")

    try:
        from visualization.chart_generator import ChartGenerator

        cg = ChartGenerator()

        # 测试数据
        test_data = {
            '年份': ['2020', '2021', '2022', '2023', '2024'],
            '营业收入': [100, 120, 140, 160, 180],
            '净利润': [20, 25, 30, 35, 40],
            '增长率': [0.1, 0.15, 0.2, 0.25, 0.3]
        }

        # 测试各种图表类型
        charts = [
            cg.create_line_chart(test_data, '营业收入', '营收趋势'),
            cg.create_bar_chart(test_data, '净利润', '利润对比'),
            cg.create_combined_chart(test_data, '营业收入', '增长率', '营收与增长'),
            cg.create_pie_chart({'项目': ['A', 'B', 'C'], '金额': [30, 40, 30]}, '项目', '金额', '占比分析')
        ]

        for i, chart in enumerate(charts):
            assert chart is not None, f"图表 {i} 生成失败"

        print("✅ 图表生成测试通过")
        return True

    except Exception as e:
        print(f"❌ 图表生成测试失败: {e}")
        return False

def test_insights_quality():
    """测试洞察质量"""
    print("测试洞察质量...")

    try:
        from analysis.insights_generator import InsightsGenerator

        ig = InsightsGenerator()

        # 测试高质量数据
        good_metrics = {
            'profitability_ratios': {
                '净利润率': [0.25, 0.28, 0.30],
                '毛利率': [0.45, 0.48, 0.50]
            },
            'growth_rates': {
                '营业收入增长率': [0.15, 0.20, 0.25]
            },
            'liquidity_ratios': {
                '流动比率': [2.0, 2.2, 2.5]
            },
            'leverage_ratios': {
                '资产负债率': [0.2, 0.25, 0.3]
            }
        }

        report = ig.generate_comprehensive_report(good_metrics)
        summary = ig.generate_executive_summary(good_metrics)
        risks = ig.generate_risk_factors(good_metrics)

        # 验证洞察质量
        assert len(report['overall']) > 0, "缺少综合评价"
        assert any('优秀' in insight or '卓越' in insight for insight in report['overall']), "高质量数据应该有正面评价"

        assert len(summary) > 0, "缺少执行摘要"
        assert len(risks) > 0, "缺少风险因素"

        print("✅ 洞察质量测试通过")
        return True

    except Exception as e:
        print(f"❌ 洞察质量测试失败: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("测试错误处理...")

    try:
        from data_extraction.stock_data_source import StockDataSource

        ds = StockDataSource()

        # 测试无效股票代码
        invalid_result = ds.get_stock_financial_data('INVALID', '2020', '2024', 'year')
        # 应该返回示例数据而不是失败
        assert isinstance(invalid_result, dict), "应该返回字典格式的数据"

        # 测试无效年份范围
        empty_result = ds.get_stock_financial_data('600519', '2030', '2040', 'year')
        # 应该处理无效年份范围
        assert isinstance(empty_result, dict), "应该返回字典格式的数据"

        print("✅ 错误处理测试通过")
        return True

    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False

def main():
    """运行集成测试"""
    print("开始集成测试...")
    print("=" * 60)

    tests = [
        test_complete_analysis_flow,
        test_chart_generation,
        test_insights_quality,
        test_error_handling
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 60)
    print(f"集成测试完成: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有集成测试通过！应用程序可以正常运行。")
        return True
    else:
        print("⚠️  部分集成测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)