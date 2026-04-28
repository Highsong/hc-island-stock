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

            if latest_ratio is not None and latest_ratio > 0.25:
                insights.append(self.insights_templates['profitability']['excellent'].format(latest_ratio))
            elif latest_ratio is not None and latest_ratio > 0.15:
                insights.append(self.insights_templates['profitability']['good'].format(latest_ratio))
            else:
                insights.append(self.insights_templates['profitability']['concern'].format(latest_ratio))

        return insights

    def generate_growth_insights(self, growth_rates: Dict[str, List[float]]) -> List[str]:
        """生成增长分析评语"""
        insights = []

        if '营业收入增长率' in growth_rates and growth_rates['营业收入增长率']:
            latest_growth = growth_rates['营业收入增长率'][-1]

            if latest_growth is not None and latest_growth > 0.2:
                insights.append(self.insights_templates['growth']['strong'].format(latest_growth))
            elif latest_growth is not None and latest_growth > 0.05:
                insights.append(self.insights_templates['growth']['moderate'].format(latest_growth))
            else:
                if latest_growth is not None:
                    insights.append(self.insights_templates['growth']['weak'].format(latest_growth))
                else:
                    insights.append("增长数据暂不可用，需要更多历史数据进行分析。")

        return insights

    def generate_liquidity_insights(self, liquidity_ratios: Dict[str, List[float]]) -> List[str]:
        """生成流动性分析评语"""
        insights = []

        if '流动比率' in liquidity_ratios and liquidity_ratios['流动比率']:
            latest_ratio = liquidity_ratios['流动比率'][-1]

            if latest_ratio is not None and latest_ratio > 2.0:
                insights.append(self.insights_templates['liquidity']['healthy'].format(latest_ratio))
            elif latest_ratio is not None and latest_ratio > 1.0:
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

        # 风险分析
        if 'leverage_ratios' in all_metrics:
            report['risk'] = self.generate_risk_insights(all_metrics['leverage_ratios'])

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
            if latest_profit_margin is not None and latest_profit_margin > 0.25:
                profit_score = 3
            elif latest_profit_margin > 0.15:
                profit_score = 2
            else:
                profit_score = 1

        # 评估增长性
        if 'growth_rates' in metrics and '营业收入增长率' in metrics['growth_rates']:
            latest_growth = metrics['growth_rates']['营业收入增长率'][-1]
            if latest_growth is not None and latest_growth > 0.2:
                growth_score = 3
            elif latest_growth is not None and latest_growth > 0.05:
                growth_score = 2
            else:
                growth_score = 1

        # 评估流动性
        if 'liquidity_ratios' in metrics and '流动比率' in metrics['liquidity_ratios']:
            latest_liquidity = metrics['liquidity_ratios']['流动比率'][-1]
            if latest_liquidity is not None and latest_liquidity > 2.0:
                liquidity_score = 3
            elif latest_liquidity > 1.0:
                liquidity_score = 2
            else:
                liquidity_score = 1

        total_score = profit_score + growth_score + liquidity_score

        # 生成具体评语
        if total_score >= 8:
            assessment.append(f"综合评分：{total_score}/9分")
            assessment.append("🏆 财务表现卓越：净利润率超过25%显示强劲盈利能力，营收增长超过20%表明市场竞争力强，流动比率高于2.0说明资金充裕。该公司基本面扎实，具备行业龙头地位，值得长期持有。建议关注品牌护城河和市场份额变化。")
        elif total_score >= 6:
            assessment.append(f"综合评分：{total_score}/9分")
            assessment.append("✅ 财务表现稳健：核心指标处于健康水平，盈利能力维持在15%以上，增长稳定，流动性充足。作为消费白马股，具备稳定的分红能力和抗风险能力。建议关注行业周期变化和成本控制能力。")
        elif total_score >= 4:
            assessment.append(f"综合评分：{total_score}/9分")
            assessment.append("⚠️ 需关注改善：盈利能力或增长速度有待提升，建议关注成本控制和市场拓展策略。虽然品牌优势明显，但需警惕行业竞争加剧对利润率的影响。建议密切关注管理层战略执行情况。")
        else:
            assessment.append(f"综合评分：{total_score}/9分")
            assessment.append("🔴 风险提示：多项财务指标低于健康水平，可能存在经营压力或行业周期影响。建议密切关注后续季度表现和政策环境变化，谨慎评估投资风险。")

        # 添加投资建议
        if total_score >= 7:
            assessment.append("💡 投资建议：综合评分较高，具备良好的长期投资价值。建议采用价值投资策略，关注估值水平，在合理价位逐步建仓。")
        elif total_score >= 5:
            assessment.append("💡 投资建议：综合表现中等，适合稳健型投资者。建议采用定投策略，分散投资时点，降低波动风险。")
        else:
            assessment.append("💡 投资建议：当前财务表现有待改善，建议观望为主。如要投资，应严格控制仓位，密切关注公司基本面变化。")

        return assessment

    def generate_executive_summary(self, all_metrics: Dict[str, Any],
                                   raw_data: Dict[str, Any] = None,
                                   stock_info: Dict[str, Any] = None) -> List[str]:
        """生成执行摘要（丰富版）

        Args:
            all_metrics: 指标字典，含 profitability_ratios / growth_rates / liquidity_ratios / leverage_ratios
            raw_data: 原始财务数据 {period: {income_statement, balance_sheet, cash_flow}}，用于计算同比
            stock_info: 股票基本信息 {name, industry, market}
        """
        summary = []

        # ── 提取最新一期数据 ──
        profit_ratios = all_metrics.get('profitability_ratios', {})
        growth_rates = all_metrics.get('growth_rates', {})
        liquidity_ratios = all_metrics.get('liquidity_ratios', {})
        leverage_ratios = all_metrics.get('leverage_ratios', {})

        def _last_valid(key, src):
            vals = src.get(key, [])
            valid = [v for v in vals if v is not None]
            return valid[-1] if valid else 0

        pm = _last_valid('净利润率', profit_ratios)          # 净利率
        gm = _last_valid('毛利率', profit_ratios)             # 毛利率
        rev_growth = _last_valid('营业收入增长率', growth_rates)
        cr = _last_valid('流动比率', liquidity_ratios)
        dr = _last_valid('资产负债率', leverage_ratios)
        em = _last_valid('权益乘数', leverage_ratios)

        # 从 raw_data 获取最新一期绝对值（兼容新旧字段名）
        rev_yoy = profit_yoy = ocf_yoy = None
        rev_val = profit_val = ocf_val = roe_val = None
        if raw_data:
            periods = sorted(raw_data.keys())
            if periods:
                latest = periods[-1]
                inc = raw_data[latest].get('income_statement', {})
                bs = raw_data[latest].get('balance_sheet', {})
                cf = raw_data[latest].get('cash_flow', {})

                rev_val = (inc.get('营业收入', [0, 0])[0] or inc.get('营业总收入', [0, 0])[0])
                rev_yoy = (inc.get('营业收入', [0, 0])[1] or inc.get('营业总收入', [0, 0])[1])
                profit_val = inc.get('归母净利润', [0, 0])[0]
                profit_yoy = inc.get('归母净利润', [0, 0])[1]
                ocf_val = (cf.get('经营活动产生的现金流量净额', [0, 0])[0]
                           or cf.get('经营活动现金流净额', [0, 0])[0])
                ocf_yoy = (cf.get('经营活动产生的现金流量净额', [0, 0])[1]
                           or cf.get('经营活动现金流净额', [0, 0])[1])

                total_assets = (bs.get('资产总计', [0])[0] or bs.get('总资产', [0])[0])
                equity = bs.get('所有者权益合计', [0])[0]
                roe_val = (profit_val / equity) if equity else None

                # 上年同比（用于趋势判断）
                if len(periods) >= 2:
                    prev = periods[-2]
                    prev_inc = raw_data[prev].get('income_statement', {})
                    prev_rev = (prev_inc.get('营业收入', [0, 0])[0] or prev_inc.get('营业总收入', [0, 0])[0])
                    prev_profit = prev_inc.get('归母净利润', [0, 0])[0]
                    prev_pm = (prev_profit / prev_rev) if prev_rev else None
                else:
                    prev_pm = None
            else:
                prev_pm = None
        else:
            prev_pm = None

        # ── 第1行：公司概况 ──
        _si = stock_info or {}
        name = _si.get('name') or ''
        industry = _si.get('industry') or ''
        # 构建标题：有公司名时显示"🏢 公司名（行业）"，否则显示"📊 财务分析报告"
        if name:
            title = f"🏢 **{name}**" + (f"（{industry}）" if industry else '') + f" · 分析期间："
        else:
            title = f"📊 **财务分析报告** · 分析期间："
        if raw_data:
            periods = sorted(raw_data.keys())
            period_range = f"{periods[0]}–{periods[-1]}" if len(periods) > 1 else periods[0] if periods else '—'
        else:
            period_range = '—'
        summary.append(f"{title}{period_range}")

        # ── 第2行：核心指标（带同比）──
        def _yoy_str(v):
            if v is None or v == 0:
                return ""
            pct = v * 100 if abs(v) < 1 else v
            return f"（{pct:+.1f}%）"

        rev_str = f"{rev_val/1e8:.1f}亿" if rev_val else "—"
        profit_str = f"{profit_val/1e8:.1f}亿" if profit_val else "—"
        ocf_str = f"{ocf_val/1e8:.1f}亿" if ocf_val else "—"
        roe_str = f"{roe_val:.1%}" if roe_val else "—"

        summary.append(
            f"📊 营收 **{rev_str}**{_yoy_str(rev_yoy)}　"
            f"归母净利润 **{profit_str}**{_yoy_str(profit_yoy)}　"
            f"经营现金流 **{ocf_str}**{_yoy_str(ocf_yoy)}"
        )
        summary.append(
            f"💰 毛利率 **{gm:.1%}**　净利率 **{pm:.1%}**　"
            f"ROE **{roe_str}**　资产负债率 **{dr:.1%}**　流动比率 **{cr:.2f}**"
        )

        # ── 第3行：趋势判断 ──
        trends = []
        if rev_growth is not None:
            if rev_growth > 0.15:
                trends.append("营收高增长")
            elif rev_growth > 0:
                trends.append("营收正增长")
            else:
                trends.append("营收下滑")
        if prev_pm is not None and pm is not None:
            if pm > prev_pm + 0.01:
                trends.append("利润率提升")
            elif pm < prev_pm - 0.01:
                trends.append("利润率收窄")
            else:
                trends.append("利润率稳定")
        if ocf_yoy is not None and ocf_yoy > 0:
            trends.append("现金流改善")
        elif ocf_yoy is not None and ocf_yoy < 0:
            trends.append("现金流承压")
        trend_str = "、".join(trends) if trends else "各项指标平稳"
        summary.append(f"📈 趋势：{trend_str}")

        # ── 第4行：综合评级 ──
        score = 0
        if pm > 0.25: score += 3
        elif pm > 0.15: score += 2
        else: score += 1
        if rev_growth is not None and rev_growth > 0.2: score += 3
        elif rev_growth is not None and rev_growth > 0.05: score += 2
        elif rev_growth is not None: score += 1
        if cr > 2.0: score += 3
        elif cr > 1.0: score += 2
        else: score += 1

        if score >= 8:
            grade, desc = "A", "财务基本面卓越，盈利能力强、成长性高、流动性充裕，具备行业龙头地位"
        elif score >= 6:
            grade, desc = "B", "财务基本面稳健，核心指标健康，具备较好的抗风险能力和持续经营能力"
        elif score >= 4:
            grade, desc = "C", "财务表现一般，部分指标有改善空间，需关注经营效率和成本控制"
        else:
            grade, desc = "D", "多项财务指标偏弱，存在一定经营压力，建议谨慎评估投资风险"
        summary.append(f"🏅 综合评级：**{grade}级**（{score}/9分）— {desc}")

        return summary

    def generate_risk_factors(self, all_metrics: Dict[str, Any]) -> List[str]:
        """生成风险因素分析"""
        risks = []

        profit_ratios = all_metrics.get('profitability_ratios', {})
        growth_rates = all_metrics.get('growth_rates', {})
        liquidity_ratios = all_metrics.get('liquidity_ratios', {})
        leverage_ratios = all_metrics.get('leverage_ratios', {})

        # 利润率风险
        if profit_ratios.get('净利润率'):
            profit_margins = profit_ratios['净利润率']
            if len(profit_margins) > 1 and profit_margins[-1] < profit_margins[-2]:
                risks.append("📉 利润率呈下降趋势，需关注成本上升或价格竞争压力")

        # 增长风险
        if growth_rates.get('营业收入增长率'):
            growth_rates_list = growth_rates['营业收入增长率']
            if growth_rates_list and growth_rates_list[-1] and growth_rates_list[-1] < 0.05:
                risks.append("🐌 营收增长放缓，可能面临市场饱和或竞争加剧")

        # 流动性风险
        if liquidity_ratios.get('流动比率'):
            current_ratio = liquidity_ratios['流动比率'][-1]
            if current_ratio < 1.0:
                risks.append("💧 流动比率偏低，短期偿债能力存在一定压力")

        # 杠杆风险
        if leverage_ratios.get('资产负债率'):
            debt_ratio = leverage_ratios['资产负债率'][-1]
            if debt_ratio > 0.7:
                risks.append("🏦 资产负债率较高，需关注利息负担和债务偿还能力")

        # 行业风险
        risks.append("🏭 行业周期性风险：白酒行业受宏观经济和政策影响较大")
        risks.append("📱 消费趋势变化：年轻消费群体偏好变化可能影响传统白酒市场")
        risks.append("🏛️ 政策监管风险：消费税、环保等政策变化可能影响经营成本")

        return risks

    def generate_risk_insights(self, leverage_ratios: Dict[str, List[float]]) -> List[str]:
        """生成风险分析评语"""
        insights = []

        if '资产负债率' in leverage_ratios and leverage_ratios['资产负债率']:
            latest_ratio = leverage_ratios['资产负债率'][-1]

            if latest_ratio is not None and latest_ratio < 0.3:
                insights.append(f"财务风险极低，资产负债率仅为{latest_ratio:.1%}，资本结构非常稳健，财务杠杆使用保守。")
            elif latest_ratio is not None and latest_ratio < 0.6:
                insights.append(f"财务风险可控，资产负债率为{latest_ratio:.1%}，资本结构合理，具备适度财务杠杆。")
            else:
                insights.append(f"财务杠杆偏高，资产负债率达到{latest_ratio:.1%}，需要关注债务偿还压力和利息负担。")

        if '权益乘数' in leverage_ratios and leverage_ratios['权益乘数']:
            latest_multiplier = leverage_ratios['权益乘数'][-1]

            if latest_multiplier is not None and latest_multiplier < 1.5:
                insights.append(f"权益乘数较低({latest_multiplier:.2f})，表明公司主要依靠自有资本运营，财务风险较小。")
            elif latest_multiplier is not None and latest_multiplier < 2.5:
                insights.append(f"权益乘数适中({latest_multiplier:.2f})，财务杠杆使用合理，能够提升股东回报率。")
            else:
                insights.append(f"权益乘数较高({latest_multiplier:.2f})，财务杠杆使用较多，在经济下行期可能面临较大压力。")

        return insights