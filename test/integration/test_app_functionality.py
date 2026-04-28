#!/usr/bin/env python3
"""
测试应用程序核心功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

# 全局导入所有必要的模块
try:
    from app_new import DataProcessor, main, display_stock_info
    from data_extraction.stock_data_source import StockDataSource
    from analysis.financial_metrics import FinancialMetrics
    from analysis.insights_generator import InsightsGenerator
    from visualization.chart_generator import ChartGenerator
    from utils.cache_manager import cache_manager
    print("✅ 所有模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

def test_imports():
    """测试所有必要的导入"""
    print("测试导入...")
    print("✅ 导入已在模块级别完成")
    return True

def test_data_source():
    """测试数据源功能"""
    print("\n测试数据源...")
    try:
        ds = StockDataSource()

        # 测试示例数据生成
        sample_data = ds._generate_sample_data('600519', '2020', '2024')
        assert len(sample_data) == 5, "示例数据年份数量错误"
        assert '2024' in sample_data, "缺少2024年数据"
        assert 'income_statement' in sample_data['2024'], "缺少收入表数据"

        # 测试股票信息获取
        stock_info = ds.get_stock_info('600519')
        assert 'code' in stock_info, "股票信息缺少代码"
        assert 'name' in stock_info, "股票信息缺少名称"

        print("✅ 数据源测试通过")
        return True
    except Exception as e:
        print(f"❌ 数据源测试失败: {e}")
        return False

def test_financial_metrics():
    """测试财务指标计算"""
    print("\n测试财务指标计算...")
    try:
        fm = FinancialMetrics()

        # 测试盈利能力计算
        income_data = {
            '营业收入': [100, 120, 140],
            '净利润': [20, 25, 30],
            '营业成本': [60, 70, 80]
        }

        profit_ratios = fm.calculate_profitability_ratios(income_data)
        assert '净利润率' in profit_ratios, "缺少净利润率"
        assert '毛利率' in profit_ratios, "缺少毛利率"
        assert len(profit_ratios['净利润率']) == 3, "净利润率数据长度错误"

        print("✅ 财务指标计算测试通过")
        return True
    except Exception as e:
        print(f"❌ 财务指标计算测试失败: {e}")
        return False

def test_insights_generation():
    """测试洞察生成"""
    print("\n测试洞察生成...")
    try:
        ig = InsightsGenerator()

        # 测试综合报告生成
        metrics = {
            'profitability_ratios': {
                '净利润率': [0.2, 0.25, 0.3],
                '毛利率': [0.4, 0.45, 0.5]
            },
            'growth_rates': {
                '营业收入增长率': [0.1, 0.15, 0.2]
            },
            'liquidity_ratios': {
                '流动比率': [1.5, 2.0, 2.5]
            },
            'leverage_ratios': {
                '资产负债率': [0.3, 0.35, 0.4]
            }
        }

        report = ig.generate_comprehensive_report(metrics)
        assert 'profitability' in report, "缺少盈利能力分析"
        assert 'growth' in report, "缺少增长分析"
        assert 'overall' in report, "缺少综合评价"

        # 测试执行摘要生成
        summary = ig.generate_executive_summary(metrics)
        assert len(summary) > 0, "执行摘要为空"

        # 测试风险因素生成
        risks = ig.generate_risk_factors(metrics)
        assert len(risks) > 0, "风险因素为空"

        print("✅ 洞察生成测试通过")
        return True
    except Exception as e:
        print(f"❌ 洞察生成测试失败: {e}")
        return False

def test_chart_generation():
    """测试图表生成"""
    print("\n测试图表生成...")
    try:
        cg = ChartGenerator()

        # 测试折线图生成
        data = {
            '年份': ['2020', '2021', '2022'],
            '营业收入': [100, 120, 140]
        }

        fig = cg.create_line_chart(data, '营业收入', '营收趋势')
        assert fig is not None, "折线图生成失败"

        # 测试柱状图生成
        fig = cg.create_bar_chart(data, '营业收入', '营收对比')
        assert fig is not None, "柱状图生成失败"

        print("✅ 图表生成测试通过")
        return True
    except Exception as e:
        print(f"❌ 图表生成测试失败: {e}")
        return False

def test_data_processor():
    """测试数据处理协调器"""
    print("\n测试数据处理协调器...")
    try:
        processor = DataProcessor()

        # 测试数据处理流程
        result = processor.process_stock_data('600519', '2020', '2024', 'year')

        # 检查返回的数据结构
        required_keys = ['charts', 'insights', 'latest_period', 'periods']
        for key in required_keys:
            assert key in result, f"结果中缺少必需的键: {key}"

        assert isinstance(result['periods'], list), "periods应该是列表"
        assert len(result['periods']) > 0, "periods不能为空"

        if result['latest_period']:
            assert 'key_metrics' in result['latest_period'], "latest_period缺少key_metrics"

        print("✅ 数据处理协调器测试通过")
        return True
    except Exception as e:
        print(f"❌ 数据处理协调器测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试股票分析系统...")
    print("=" * 60)

    tests = [
        test_imports,
        test_data_source,
        test_financial_metrics,
        test_insights_generation,
        test_chart_generation,
        test_data_processor
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 60)
    print(f"测试完成: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！应用程序功能正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)