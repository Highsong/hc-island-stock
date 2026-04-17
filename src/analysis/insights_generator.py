# src/analysis/insights_generator.py
from typing import Dict, List, Any
import numpy as np

class InsightsGenerator:
    """智能评语生成器"""

    def __init__(self):
        self.insights_templates = {
            'profitability': {
                'excellent': "盈利能力表现优秀，净利润率达到{:.1%}，远超行业平均水平。",
                'good': "盈利能力良好，净利润率为{:.1%}，保持稳定盈利水平。",
                'concern': "盈利能力需要关注，净利润率仅为{:.1%}，建议关注成本控制和收入增长。"
            },
            'growth': {
                'strong': "增长势头强劲，营业收入同比增长{:.1%}，展现出良好的市场竞争力。",
                'moderate': "增长表现稳健，营业收入同比增长{:.1%}，维持稳定发展态势。",
                'weak': "增长动力不足，营业收入同比仅增长{:.1%}，需要关注市场策略调整。"
            },
            'liquidity': {
                'healthy': "流动性状况健康，流动比率为{:.2f}，短期偿债能力充足。",
                'adequate': "流动性状况良好，流动比率为{:.2f}，能够满足短期债务需求。",
                'risky': "流动性存在风险，流动比率仅为{:.2f}，建议关注现金流管理。"
            }
        }

    def generate_profitability_insights(self, ratios: Dict[str, List[float]]) -> List[str]:
        """生成盈利能力分析评语"""
        insights = []

        if '净利润率' in ratios and ratios['净利润率']:
            latest_ratio = ratios['净利润率'][-1]

            if latest_ratio > 0.25:
                insights.append(self.insights_templates['profitability']['excellent'].format(latest_ratio))
            elif latest_ratio > 0.15:
                insights.append(self.insights_templates['profitability']['good'].format(latest_ratio))
            else:
                insights.append(self.insights_templates['profitability']['concern'].format(latest_ratio))

        return insights

    def generate_growth_insights(self, growth_rates: Dict[str, List[float]]) -> List[str]:
        """生成增长分析评语"""
        insights = []

        if '营业收入增长率' in growth_rates and growth_rates['营业收入增长率']:
            latest_growth = growth_rates['营业收入增长率'][-1]

            if latest_growth > 0.2:
                insights.append(self.insights_templates['growth']['strong'].format(latest_growth))
            elif latest_growth > 0.05:
                insights.append(self.insights_templates['growth']['moderate'].format(latest_growth))
            else:
                insights.append(self.insights_templates['growth']['weak'].format(latest_growth))

        return insights

    def generate_liquidity_insights(self, liquidity_ratios: Dict[str, List[float]]) -> List[str]:
        """生成流动性分析评语"""
        insights = []

        if '流动比率' in liquidity_ratios and liquidity_ratios['流动比率']:
            latest_ratio = liquidity_ratios['流动比率'][-1]

            if latest_ratio > 2.0:
                insights.append(self.insights_templates['liquidity']['healthy'].format(latest_ratio))
            elif latest_ratio > 1.0:
                insights.append(self.insights_templates['liquidity']['adequate'].format(latest_ratio))
            else:
                insights.append(self.insights_templates['liquidity']['risky'].format(latest_ratio))

        return insights

    def generate_comprehensive_report(self, all_metrics: Dict[str, Any]) -> Dict[str, List[str]]:
        """生成综合分析报告"""
        report = {
            'profitability': [],
            'growth': [],
            'liquidity': [],
            'risk': [],
            'overall': []
        }

        # 盈利能力分析
        if 'profitability_ratios' in all_metrics:
            report['profitability'] = self.generate_profitability_insights(all_metrics['profitability_ratios'])

        # 增长分析
        if 'growth_rates' in all_metrics:
            report['growth'] = self.generate_growth_insights(all_metrics['growth_rates'])

        # 流动性分析
        if 'liquidity_ratios' in all_metrics:
            report['liquidity'] = self.generate_liquidity_insights(all_metrics['liquidity_ratios'])

        # 综合评估
        report['overall'] = self._generate_overall_assessment(all_metrics)

        return report

    def _generate_overall_assessment(self, metrics: Dict[str, Any]) -> List[str]:
        """生成整体评估"""
        assessment = []

        # 基于多个指标进行综合评估
        profit_score = 0
        growth_score = 0
        liquidity_score = 0

        # 评估盈利能力
        if 'profitability_ratios' in metrics and '净利润率' in metrics['profitability_ratios']:
            latest_profit_margin = metrics['profitability_ratios']['净利润率'][-1]
            if latest_profit_margin > 0.25:
                profit_score = 3
            elif latest_profit_margin > 0.15:
                profit_score = 2
            else:
                profit_score = 1

        # 评估增长性
        if 'growth_rates' in metrics and '营业收入增长率' in metrics['growth_rates']:
            latest_growth = metrics['growth_rates']['营业收入增长率'][-1]
            if latest_growth > 0.2:
                growth_score = 3
            elif latest_growth > 0.05:
                growth_score = 2
            else:
                growth_score = 1

        # 评估流动性
        if 'liquidity_ratios' in metrics and '流动比率' in metrics['liquidity_ratios']:
            latest_liquidity = metrics['liquidity_ratios']['流动比率'][-1]
            if latest_liquidity > 2.0:
                liquidity_score = 3
            elif latest_liquidity > 1.0:
                liquidity_score = 2
            else:
                liquidity_score = 1

        total_score = profit_score + growth_score + liquidity_score

        # 生成具体评语
        if total_score >= 8:
            assessment.append(f"综合评分：{total_score}/9分")
            assessment.append("财务表现卓越：净利润率超过25%显示强劲盈利能力，营收增长超过20%表明市场竞争力强，流动比率高于2.0说明资金充裕。茅台作为白酒龙头，基本面扎实，值得长期持有。")
        elif total_score >= 6:
            assessment.append(f"综合评分：{total_score}/9分")
            assessment.append("财务表现稳健：核心指标处于健康水平，盈利能力维持在15%以上，增长稳定，流动性充足。作为消费白马股，具备稳定的分红能力和抗风险能力。")
        elif total_score >= 4:
            assessment.append(f"综合评分：{total_score}/9分")
            assessment.append("需关注改善：盈利能力或增长速度有待提升，建议关注成本控制和市场拓展策略。虽然品牌优势明显，但需警惕行业竞争加剧对利润率的影响。")
        else:
            assessment.append(f"综合评分：{total_score}/9分")
            assessment.append("风险提示：多项财务指标低于健康水平，可能存在经营压力或行业周期影响。建议密切关注后续季度表现和政策环境变化。")

        return assessment