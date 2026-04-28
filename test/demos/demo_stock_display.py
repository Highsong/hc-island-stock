#!/usr/bin/env python3
"""Demo stock name and year data display"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def demo_stock_display():
    """Demonstrate stock name and year display functionality"""
    print("Demonstrating stock name and year data display...")

    try:
        # Test the modified financial overview function components
        from data_extraction.stock_data_source import StockDataSource
        from app_new import DataProcessor

        # Test 1: Default stock code (Example: Moutai)
        print("\nTest 1: Default stock code (Example: Moutai)")
        ds = StockDataSource()
        stock_info = ds.get_stock_info('600519')  # 示例：贵州茅台
        print(f"Stock info: {stock_info}")

        # Test 2: Sample data processing with periods
        print("\nTest 2: Sample data processing")
        dp = DataProcessor()

        # Create sample data to simulate what would be returned by process_stock_data
        sample_data = {
            'latest_period': {
                'period': '2023',
                'key_metrics': {
                    'revenue': 1322.5,
                    'net_profit': 198.4,
                    'revenue_growth': 0.15,
                    'profit_growth': 0.12,
                    'profit_margin': 0.15,
                    'roe': 0.18,
                    'roe_change': 0.01,
                    'margin_change': 0.005
                }
            },
            'periods': ['2021', '2022', '2023'],
            'charts': {'revenue_chart': 'figure_object', 'profit_chart': 'figure_object'},
            'insights': {'profitability': ['Insight 1'], 'growth': ['Insight 2']}
        }

        filters = {
            'stock_code': '600519',  # 示例：贵州茅台
            'start_year': '2021',
            'end_year': '2023',
            'period': 'year',
            'export_format': 'PNG'
        }

        # Simulate what the display_financial_overview function would show
        if sample_data.get('latest_period'):
            print("[OK] Latest period data available")
            latest_metrics = sample_data['latest_period']['key_metrics']
            print(f"  Revenue: ¥{latest_metrics.get('revenue', 0):,.1f}亿")
            print(f"  Net Profit: ¥{latest_metrics.get('net_profit', 0):,.1f}亿")
            print(f"  Revenue Growth: {latest_metrics.get('revenue_growth', 0):.1%}")
            print(f"  Profit Margin: {latest_metrics.get('profit_margin', 0):.1%}")

        # Test period information
        periods = sample_data.get('periods', [])
        if periods:
            print(f"\n[OK] Analysis periods: {min(periods)} - {max(periods)}")
            print(f"  Period count: {len(periods)} years")

        # Test stock information display
        stock_code = filters.get('stock_code', '')
        if stock_code:
            print(f"\n[OK] Stock code: {stock_code}")
            try:
                stock_info = ds.get_stock_info(stock_code)
                print(f"  Stock name: {stock_info.get('name', 'Unknown')}")
                print(f"  Market: {stock_info.get('market', 'Unknown')}")
                print(f"  Industry: {stock_info.get('industry', 'Unknown')}")
            except Exception as e:
                print(f"  Stock info error (expected): {e}")

        print("\n🎉 Stock name and year data display demonstration completed!")
        print("\nFeatures demonstrated:")
        print("• Default stock code example: 600519")
        print("• Stock name display in financial overview")
        print("• Analysis period range showing")
        print("• Key metrics with growth rates")
        print("• Professional financial presentation")

        return True

    except Exception as e:
        print(f"Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = demo_stock_display()
    if success:
        print("\nThe enhanced financial overview is ready for use!")
    else:
        print("\nEnhancement demonstration encountered issues.")
    sys.exit(0 if success else 1)