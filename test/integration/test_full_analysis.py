#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the full analysis pipeline"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from app_new import DataProcessor

def test_full_analysis():
    """Test the complete analysis pipeline"""
    print("=" * 80)
    print("TESTING FULL ANALYSIS PIPELINE")
    print("=" * 80)

    try:
        processor = DataProcessor()

        print("\n1. Testing yearly analysis...")
        yearly_result = processor.process_stock_data('600519', '2021', '2023', 'year')

        print(f"Yearly analysis result keys: {list(yearly_result.keys())}")

        if yearly_result.get('periods'):
            print(f"Periods: {yearly_result['periods']}")
            print(f"Number of periods: {len(yearly_result['periods'])}")

        if yearly_result.get('latest_period'):
            print("✓ Latest period data available")
            latest = yearly_result['latest_period']
            if 'key_metrics' in latest:
                metrics = latest['key_metrics']
                print(f"  Revenue: {metrics.get('revenue', 0)}")
                print(f"  Net Profit: {metrics.get('net_profit', 0)}")
                print(f"  Revenue Growth: {metrics.get('revenue_growth', 0):.2%}")
                print(f"  Profit Margin: {metrics.get('profit_margin', 0):.2%}")

        if yearly_result.get('charts'):
            print(f"✓ Charts generated: {list(yearly_result['charts'].keys())}")

        print("\n2. Testing quarterly analysis...")
        quarterly_result = processor.process_stock_data('600519', '2023', '2023', 'quarter')

        print(f"Quarterly analysis result keys: {list(quarterly_result.keys())}")

        if quarterly_result.get('period_data'):
            print("✓ Quarterly period data available")
            period_data = quarterly_result['period_data']
            print(f"  Period data keys: {list(period_data.keys())}")

        print("\n3. Testing financial metrics calculation...")
        if yearly_result.get('periods'):
            # Test the metrics calculation directly
            from analysis.financial_metrics import FinancialMetrics
            metrics_calculator = FinancialMetrics()

            # Get some sample data
            raw_data = processor._load_stock_data('600519', '2021', '2023', 'year')
            if raw_data:
                all_metrics = metrics_calculator.calculate_all_metrics(raw_data)
                print(f"✓ Financial metrics calculated: {list(all_metrics.keys())}")

                if 'profitability_ratios' in all_metrics:
                    profit_ratios = all_metrics['profitability_ratios']
                    print(f"  Profitability ratios: {list(profit_ratios.keys())}")

                if 'growth_rates' in all_metrics:
                    growth_rates = all_metrics['growth_rates']
                    print(f"  Growth rates: {list(growth_rates.keys())}")

        print("\n✅ FULL ANALYSIS PIPELINE TEST PASSED!")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("FULL ANALYSIS TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_full_analysis()