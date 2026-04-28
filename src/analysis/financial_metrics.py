# src/analysis/financial_metrics.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class FinancialMetrics:
    """财务指标计算器 - 支持多数据类型"""

    def __init__(self):
        self.metrics = {}

    def calculate_profitability_ratios(self, income_data: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """计算盈利能力指标"""
        # Handle empty input data
        if not income_data or '营业收入' not in income_data:
            return {}

        ratios = {}

        years = len(income_data['营业收入'])

        # Check if required keys exist and have valid data
        if years == 0:
            return {'净利润率': [], '毛利率': []}

        # 净利润率
        try:
            ratios['净利润率'] = [
                income_data['净利润'][i] / income_data['营业收入'][i] if income_data['营业收入'][i] != 0 else 0
                for i in range(years)
            ]
        except (KeyError, IndexError):
            ratios['净利润率'] = [0] * years

        # 毛利率
        try:
            ratios['毛利率'] = [
                (income_data['营业收入'][i] - income_data.get('营业成本', [0]*years)[i]) / income_data['营业收入'][i]
                if income_data['营业收入'][i] != 0 else 0
                for i in range(years)
            ]
        except (KeyError, IndexError):
            ratios['毛利率'] = [0] * years

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

    def calculate_all_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算所有财务指标（支持多数据类型）"""
        if not raw_data:
            return {}

        # 提取数据
        periods = sorted(raw_data.keys())

        # 收入数据
        income_data = {
            '营业收入': [],
            '净利润': [],
            '营业成本': [],
            '销售费用': [],
            '管理费用': [],
            '财务费用': []
        }

        # 资产负债数据
        balance_data = {
            '总资产': [],
            '总负债': [],
            '所有者权益': [],
            '流动资产': [],
            '流动负债': [],
            '存货': [],
            '货币资金': []
        }

        # 现金流数据
        cash_flow_data = {
            '经营活动现金流': [],
            '投资活动现金流': [],
            '筹资活动现金流': [],
            '现金净增加额': []
        }

        for period in periods:
            period_data = raw_data[period]

            # 提取收入数据
            income_stmt = period_data.get('income_statement', {})
            for key in income_data.keys():
                income_data[key].append(income_stmt.get(key, [0])[0])

            # 提取资产负债数据
            balance_sheet = period_data.get('balance_sheet', {})
            for key in balance_data.keys():
                balance_data[key].append(balance_sheet.get(key, [0])[0])

            # 提取现金流数据
            cash_flow = period_data.get('cash_flow', {})
            for key in cash_flow_data.keys():
                cash_flow_data[key].append(cash_flow.get(key, [0])[0])

        # 计算各类指标（避免存储冗余的原始数据）
        result = {
            'periods': periods,
            'profitability_ratios': self.calculate_profitability_ratios(income_data),
            'growth_rates': self.calculate_growth_rates(income_data),
            'liquidity_ratios': self.calculate_liquidity_ratios(balance_data),
            'leverage_ratios': self.calculate_leverage_ratios(balance_data),
            'cash_flow_ratios': self.calculate_cash_flow_ratios(cash_flow_data, income_data)
        }

        return result

    def calculate_cash_flow_ratios(self,
                                 cash_flow_data: Dict[str, List[float]],
                                 income_data: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """计算现金流相关指标"""
        ratios = {}
        years = len(cash_flow_data['经营活动现金流'])

        # 经营现金流与净利润比率
        ratios['经营现金流净利润比'] = [
            cash_flow_data['经营活动现金流'][i] / income_data['净利润'][i]
            if income_data['净利润'][i] != 0 else 0
            for i in range(years)
        ]

        # 经营现金流与营业收入比率
        ratios['经营现金流营收比'] = [
            cash_flow_data['经营活动现金流'][i] / income_data['营业收入'][i]
            if income_data['营业收入'][i] != 0 else 0
            for i in range(years)
        ]

        return ratios

    def get_key_metrics_summary(self, all_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """获取关键指标摘要"""
        if not all_metrics or 'periods' not in all_metrics:
            return {}

        periods = all_metrics['periods']
        if not periods:
            return {}

        latest_period = periods[-1]
        period_idx = len(periods) - 1

        # 盈利能力指标
        profit_ratios = all_metrics.get('profitability_ratios', {})
        latest_profit_margin = profit_ratios.get('净利润率', [0])[period_idx] if period_idx < len(profit_ratios.get('净利润率', [])) else 0
        latest_gross_margin = profit_ratios.get('毛利率', [0])[period_idx] if period_idx < len(profit_ratios.get('毛利率', [])) else 0

        # 成长性指标
        growth_rates = all_metrics.get('growth_rates', {})
        latest_revenue_growth = growth_rates.get('营业收入增长率', [0])[period_idx] if period_idx < len(growth_rates.get('营业收入增长率', [])) else 0
        latest_profit_growth = growth_rates.get('净利润增长率', [0])[period_idx] if period_idx < len(growth_rates.get('净利润增长率', [])) else 0

        # 流动性指标
        liquidity_ratios = all_metrics.get('liquidity_ratios', {})
        latest_current_ratio = liquidity_ratios.get('流动比率', [0])[period_idx] if period_idx < len(liquidity_ratios.get('流动比率', [])) else 0
        latest_quick_ratio = liquidity_ratios.get('速动比率', [0])[period_idx] if period_idx < len(liquidity_ratios.get('速动比率', [])) else 0

        # 杠杆指标
        leverage_ratios = all_metrics.get('leverage_ratios', {})
        latest_debt_ratio = leverage_ratios.get('资产负债率', [0])[period_idx] if period_idx < len(leverage_ratios.get('资产负债率', [])) else 0
        latest_equity_multiplier = leverage_ratios.get('权益乘数', [0])[period_idx] if period_idx < len(leverage_ratios.get('权益乘数', [])) else 0

        return {
            'period': latest_period,
            'profitability': {
                '净利润率': latest_profit_margin,
                '毛利率': latest_gross_margin
            },
            'growth': {
                '营收增长率': latest_revenue_growth,
                '利润增长率': latest_profit_growth
            },
            'liquidity': {
                '流动比率': latest_current_ratio,
                '速动比率': latest_quick_ratio
            },
            'leverage': {
                '资产负债率': latest_debt_ratio,
                '权益乘数': latest_equity_multiplier
            }
        }