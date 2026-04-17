# tests/test_financial_analysis.py
def test_calculate_profitability_ratios():
    from src.analysis.financial_metrics import FinancialMetrics

    # 模拟财务数据
    income_data = {
        '营业收入': [1000, 1200],
        '净利润': [200, 240],
        '营业成本': [600, 720]
    }

    metrics = FinancialMetrics()
    ratios = metrics.calculate_profitability_ratios(income_data)

    assert '净利润率' in ratios
    assert '毛利率' in ratios
    assert ratios['净利润率'][0] == 0.2  # 200/1000

def test_calculate_growth_rates():
    from src.analysis.financial_metrics import FinancialMetrics

    data = {
        '营业收入': [1000, 1200, 1440],
        '净利润': [200, 240, 288]
    }

    metrics = FinancialMetrics()
    growth_rates = metrics.calculate_growth_rates(data)

    assert '营业收入增长率' in growth_rates
    assert '净利润增长率' in growth_rates
    assert abs(growth_rates['营业收入增长率'][1] - 0.2) < 0.01  # (1200-1000)/1000