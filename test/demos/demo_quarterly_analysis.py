#!/usr/bin/env python3
"""Demonstrate advanced quarterly and seasonal analysis functionality"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from analysis.advanced_quarterly_analysis import advanced_quarterly_analyzer

def demo_advanced_analysis():
    """Demonstrate advanced quarterly analysis"""
    print("Starting advanced quarterly analysis demo...")

    # Create sample data
    sample_data = {
        '2021': {
            'income_statement': {'营业收入': [1000]},
            'balance_sheet': {'总资产': [2000]}
        },
        '2022': {
            'income_statement': {'营业收入': [1150]},
            'balance_sheet': {'总资产': [2300]}
        },
        '2023': {
            'income_statement': {'营业收入': [1322.5]},
            'balance_sheet': {'总资产': [2645]}
        }
    }

    print("\nSample Data:")
    for year, data in sample_data.items():
        revenue = data['income_statement']['营业收入'][0]
        print(f"  {year}: Revenue {revenue} billion")

    # Execute advanced quarterly analysis
    print("\nPerforming advanced quarterly analysis...")
    try:
        result = advanced_quarterly_analyzer.perform_comprehensive_quarterly_analysis(
            sample_data, {}
        )

        print("Analysis completed!")

        # Display results summary
        if 'quarterly_trends' in result:
            trends = result['quarterly_trends']
            if 'error' not in trends:
                years = list(trends.keys())
                print(f"\nQuarterly Trends:")
                for year in years:
                    if 'revenue' in trends[year]:
                        q_revenues = trends[year]['revenue']
                        total_q_rev = sum(q_revenues)
                        print(f"  {year}: Q1={q_revenues[0]:.1f}, Q2={q_revenues[1]:.1f}, "
                              f"Q3={q_revenues[2]:.1f}, Q4={q_revenues[3]:.1f}")
            else:
                print(f"  Error: {trends['error']}")

        if 'seasonal_analysis' in result:
            seasonal = result['seasonal_analysis']
            if 'base_patterns' in seasonal:
                patterns = seasonal['base_patterns']
                print(f"\nSeasonal Patterns:")
                print(f"  Strongest Quarter: {patterns.get('strongest_quarter', 'N/A')}")
                print(f"  Weakest Quarter: {patterns.get('weakest_quarter', 'N/A')}")
                print(f"  Seasonality Index: {patterns.get('seasonality_index', 1.0):.2f}x")

        if 'business_cycle_analysis' in result:
            cycle = result['business_cycle_analysis']
            phase = cycle.get('current_phase', 'unknown')
            confidence = cycle.get('confidence', 0.0)
            print(f"\nBusiness Cycle:")
            print(f"  Current Phase: {phase} (Confidence: {confidence:.0%})")
            characteristics = cycle.get('characteristics', [])
            if characteristics:
                print(f"  Features: {', '.join(characteristics)}")

        if 'risk_indicators' in result:
            risks = result['risk_indicators']
            overall_risk = risks.get('overall_risk_level', 'medium')
            print(f"\nRisk Analysis:")
            print(f"  Overall Risk Level: {overall_risk.upper()}")

        if 'insights' in result:
            insights = result['insights']
            print(f"\nBusiness Insights:")
            for insight in insights[:3]:  # Show first 3 insights
                print(f"  - {insight}")

    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()

    print("\nAdvanced quarterly analysis demo completed!")

if __name__ == '__main__':
    demo_advanced_analysis()