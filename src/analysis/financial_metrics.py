# src/analysis/financial_metrics.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class FinancialMetrics:
    """财务指标计算器"""

    def __init__(self):
        self.metrics = {}

    def calculate_profitability_ratios(self, income_data: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """计算盈利能力指标"""
        ratios = {}

        years = len(income_data['营业收入'])

        # 净利润率
        ratios['净利润率'] = [
            income_data['净利润'][i] / income_data['营业收入'][i] if income_data['营业收入'][i] != 0 else 0
            for i in range(years)
        ]

        # 毛利率
        ratios['毛利率'] = [
            (income_data['营业收入'][i] - income_data['营业成本'][i]) / income_data['营业收入'][i]
            if income_data['营业收入'][i] != 0 else 0
            for i in range(years)
        ]

        return ratios

    def calculate_growth_rates(self, data: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """计算增长率"""
        growth_rates = {}

        for key, values in data.items():
            rates = [None]  # 第一年无增长率
            for i in range(1, len(values)):
                if values[i-1] != 0:
                    rate = (values[i] - values[i-1]) / values[i-1]
                else:
                    rate = 0
                rates.append(rate)
            growth_rates[f'{key}增长率'] = rates

        return growth_rates

    def calculate_liquidity_ratios(self, balance_data: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """计算流动性指标"""
        ratios = {}
        years = len(balance_data['流动资产'])

        # 流动比率
        ratios['流动比率'] = [
            balance_data['流动资产'][i] / balance_data['流动负债'][i]
            if balance_data['流动负债'][i] != 0 else 0
            for i in range(years)
        ]

        # 速动比率（简化计算）
        ratios['速动比率'] = [
            (balance_data['流动资产'][i] - balance_data.get('存货', [0]*years)[i]) / balance_data['流动负债'][i]
            if balance_data['流动负债'][i] != 0 else 0
            for i in range(years)
        ]

        return ratios

    def calculate_leverage_ratios(self, balance_data: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """计算杠杆指标"""
        ratios = {}
        years = len(balance_data['总资产'])

        # 资产负债率
        ratios['资产负债率'] = [
            balance_data['总负债'][i] / balance_data['总资产'][i]
            if balance_data['总资产'][i] != 0 else 0
            for i in range(years)
        ]

        # 权益乘数
        ratios['权益乘数'] = [
            balance_data['总资产'][i] / balance_data['所有者权益'][i]
            if balance_data['所有者权益'][i] != 0 else 0
            for i in range(years)
        ]

        return ratios