#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试关键指标数据流"""

def test_metrics_flow():
    """测试关键指标数据流"""
    print("测试关键指标数据流")
    print("=" * 60)

    # 模拟从数据源获取的数据
    revenue = 168838102514.79
    profit = 85310324833.67

    # 模拟 app_new.py 中的计算
    profit_margin = profit / revenue if revenue > 0 else 0

    # 模拟 key_metrics 数据结构
    key_metrics = {
        'revenue': revenue,
        'net_profit': profit,
        'revenue_growth': 0.05,  # 假设5%增长
        'profit_growth': 0.03,   # 假设3%增长
        'profit_margin': profit_margin,
        'roe': 0.15,
        'roe_change': 0.01,
        'margin_change': 0.005
    }

    print(f"key_metrics 数据:")
    for key, value in key_metrics.items():
        if key in ['revenue', 'net_profit']:
            print(f"  {key}: {value:,.2f}")
        else:
            print(f"  {key}: {value}")

    # 模拟 DashboardLayout 中的显示逻辑
    print(f"\nDashboardLayout 显示逻辑:")
    dashboard_revenue = key_metrics.get('revenue', 0) / 100000000
    dashboard_profit = key_metrics.get('net_profit', 0) / 100000000
    dashboard_margin = key_metrics.get('profit_margin', 0)

    print(f"  营业收入: {dashboard_revenue:.2f}亿")
    print(f"  归母净利润: {dashboard_profit:.2f}亿")
    print(f"  净利润率: {dashboard_margin:.1%}")

    # 模拟 FinancialDashboard 中的显示逻辑
    print(f"\nFinancialDashboard 显示逻辑:")
    def format_currency(amount):
        if amount >= 100000000:
            return f"{amount / 100000000:.2f}亿"
        elif amount >= 10000:
            return f"{amount / 10000:.2f}万"
        else:
            return f"{amount:.2f}"

    financial_revenue = format_currency(key_metrics.get('revenue', 0))
    financial_margin = key_metrics.get('profit_margin', 0)

    print(f"  营业收入: {financial_revenue}")
    print(f"  净利润率: {financial_margin:.1%}")

    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    test_metrics_flow()