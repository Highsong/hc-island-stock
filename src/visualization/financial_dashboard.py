"""
专业财务分析仪表板组件
提供综合性的财务数据展示和分析界面
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

class FinancialDashboard:
    """专业财务分析仪表板"""

    def __init__(self):
        self.color_scheme = {
            'primary': '#E74C3C',    # 主色调红
            'secondary': '#F39C12',  # 辅助色金
            'accent': '#3498DB',     # 强调色蓝
            'neutral': '#95A5A6',    # 中性色灰
            'success': '#27AE60',    # 成功色绿
            'warning': '#F1C40F',    # 警告色黄
            'danger': '#C0392B'      # 危险色深红
        }

    def _format_currency(self, amount: float) -> str:
        """格式化货币金额，自动选择合适的单位

        Args:
            amount: 金额数值

        Returns:
            格式化后的字符串，如 "1,234.56万" 或 "12.34亿"
        """
        if amount >= 100000000:  # >= 1亿
            return f"{amount / 100000000:.2f}亿"
        elif amount >= 10000:  # >= 1万
            return f"{amount / 10000:.2f}万"
        else:
            return f"{amount:.2f}"

    def create_executive_summary(self, data: Dict[str, Any]) -> None:
        """创建高管摘要面板"""
        if not data or 'latest_year' not in data:
            st.info("暂无数据用于生成高管摘要")
            return

        latest_metrics = data['latest_year']['key_metrics']

        st.markdown("### 📊 高管财务摘要")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            revenue = latest_metrics.get('revenue', 0)
            revenue_growth = latest_metrics.get('revenue_growth', 0)
            st.metric(
                "营业收入",
                self._format_currency(revenue),
                f"{revenue_growth:.1%}" if abs(revenue_growth) > 0.001 else "稳定"
            )

        with col2:
            profit_margin = latest_metrics.get('profit_margin', 0)
            st.metric(
                "净利润率",
                f"{profit_margin:.1%}",
                "盈利能力" if profit_margin > 0.15 else "需改善"
            )

        with col3:
            roe = latest_metrics.get('roe', 0)
            st.metric(
                "净资产收益率",
                f"{roe:.1%}",
                "优秀" if roe > 0.15 else "良好" if roe > 0.1 else "一般"
            )

        with col4:
            if 'seasonal_patterns' in data:
                strongest_q = data['seasonal_patterns'].get('strongest_quarter', 'N/A')
                st.metric("最强季度", strongest_q)

    def create_risk_indicator_panel(self, risk_data: Dict[str, Any]) -> None:
        """创建风险指标面板"""
        if not risk_data:
            return

        st.markdown("### 🛡️ 风险监控指标")

        risk_level = risk_data.get('overall_risk_level', 'medium')

        # 风险等级指示器
        risk_colors = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
        risk_labels = {'low': '低风险', 'medium': '中风险', 'high': '高风险'}
        indicator_color = risk_colors.get(risk_level, '⚪')
        indicator_label = risk_labels.get(risk_level, '未知')

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("总体风险等级", f"{indicator_color} {indicator_label}")

        with col2:
            seasonal_count = len(risk_data.get('seasonal_risks', []))
            st.metric("季节性风险", seasonal_count)

        with col3:
            operational_count = len(risk_data.get('operational_risks', []))
            st.metric("运营风险", operational_count)

        # 详细风险列表
        if any([seasonal_count, operational_count]):
            with st.expander("详细风险评估"):
                for risk_type, risks in [('seasonal_risks', seasonal_count),
                                       ('operational_risks', operational_count),
                                       ('financial_risks', len(risk_data.get('financial_risks', [])))]:
                    if risks > 0 and risk_type in risk_data:
                        risk_list = risk_data[risk_type]
                        if risk_list:
                            st.write(f"**{risk_type.replace('_', ' ').title()}:**")
                            for risk in risk_list:
                                st.write(f"• {risk}")
                            st.write("---")

    def create_performance_comparison(self, quarterly_data: Dict[str, Any],
                                    title: str = "季度业绩对比") -> None:
        """创建业绩对比图表"""
        if not quarterly_data:
            st.info("暂无季度数据进行业绩对比")
            return

        try:
            # 准备对比数据
            quarters = []
            revenues = []
            profits = []

            years = sorted(quarterly_data.keys())
            for year in years:
                if 'revenue' in quarterly_data[year]:
                    q_revenues = quarterly_data[year]['revenue']
                    for i, q_rev in enumerate(q_revenues):
                        quarters.append(f"{year}Q{i+1}")
                        revenues.append(q_rev)

                        # 计算季度利润（简化处理）
                        profit = q_rev * 0.15
                        profits.append(profit)

            if len(quarters) < 4:
                st.info("需要更多季度数据进行对比分析")
                return

            # 创建组合图
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # 柱状图 - 收入
            fig.add_trace(
                go.Bar(x=quarters, y=revenues, name="营业收入",
                      marker_color=self.color_scheme['primary']),
                secondary_y=False
            )

            # 折线图 - 利润率
            profit_margins = [p / r if r > 0 else 0 for p, r in zip(profits, revenues)]
            fig.add_trace(
                go.Scatter(x=quarters, y=profit_margins, name="利润率",
                          mode='lines+markers', line=dict(color=self.color_scheme['success'])),
                secondary_y=True
            )

            fig.update_layout(
                title=dict(text=title, x=0.5, xanchor='center', font=dict(size=18)),
                template='plotly',
                plot_bgcolor='rgba(248,249,250,1)',
                paper_bgcolor='rgba(255,255,255,1)',
                font=dict(color='black'),
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            fig.update_yaxes(title_text="营业收入 (亿元)", secondary_y=False, showgrid=True, gridcolor='lightgray')
            fig.update_yaxes(title_text="利润率 (%)", secondary_y=True, showgrid=True, gridcolor='lightgray')

            st.plotly_chart(fig, width='stretch')

        except Exception as e:
            st.error(f"创建业绩对比图时出错: {e}")

    def create_seasonality_analysis(self, seasonal_data: Dict[str, Any],
                                  title: str = "季节性模式分析") -> None:
        """创建季节性分析可视化"""
        if not seasonal_data or 'base_patterns' not in seasonal_data:
            st.info("暂无季节性分析数据")
            return

        patterns = seasonal_data['base_patterns']

        try:
            # 准备季节性数据
            quarters = ['Q1', 'Q2', 'Q3', 'Q4']
            values = []

            if 'quarterly_averages' in patterns:
                for q in quarters:
                    values.append(patterns['quarterly_averages'].get(q, 0))

            if not any(values):
                values = [25, 25, 25, 25]  # 默认等分布

            # 创建雷达图显示季节性
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=quarters,
                fill='toself',
                name='季度表现',
                line=dict(color=self.color_scheme['accent'], width=3),
                marker=dict(size=10, color=self.color_scheme['accent'])
            ))

            fig.update_layout(
                title=dict(text=f"{title}", x=0.5, xanchor='center', font=dict(size=16)),
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[min(values)*0.8, max(values)*1.2],
                        tickfont=dict(color='black'),
                        gridcolor='lightgray'
                    ),
                    angularaxis=dict(tickfont=dict(color='black'))
                ),
                showlegend=True,
                template='plotly',
                plot_bgcolor='rgba(248,249,250,1)',
                paper_bgcolor='rgba(255,255,255,1)',
                font=dict(color='black')
            )

            st.plotly_chart(fig, width='stretch')

            # 显示关键指标
            col1, col2, col3 = st.columns(3)
            with col1:
                strongest = patterns.get('strongest_quarter', 'N/A')
                st.metric("最强季度", strongest)
            with col2:
                weakest = patterns.get('weakest_quarter', 'N/A')
                st.metric("最弱季度", weakest)
            with col3:
                season_idx = patterns.get('seasonality_index', 1.0)
                st.metric("季节强度", f"{season_idx:.2f}x")

        except Exception as e:
            st.error(f"创建季节性分析图时出错: {e}")

    def create_business_cycle_visualization(self, cycle_data: Dict[str, Any],
                                         title: str = "业务周期分析") -> None:
        """创建业务周期可视化"""
        if not cycle_data or 'current_phase' not in cycle_data:
            st.info("暂无业务周期分析数据")
            return

        try:
            phase = cycle_data['current_phase']
            confidence = cycle_data.get('confidence', 0.7)
            characteristics = cycle_data.get('characteristics', [])

            # 创建阶段指示器
            phase_colors = {
                '扩张期': self.color_scheme['success'],
                '稳定期': self.color_scheme['secondary'],
                '调整期': self.color_scheme['warning'],
                '衰退期': self.color_scheme['danger']
            }

            color = phase_colors.get(phase, self.color_scheme['neutral'])

            fig = go.Figure()

            # 使用环形图显示阶段和信心度
            fig.add_trace(go.Pie(
                values=[confidence, 1-confidence],
                labels=['当前阶段', '其他阶段'],
                hole=0.6,
                marker=dict(colors=[color, 'lightgray']),
                textinfo='percent',
                textposition='inside'
            ))

            fig.update_layout(
                title=dict(text=f"{title} - {phase}", x=0.5, xanchor='center', font=dict(size=16)),
                showlegend=False,
                template='plotly',
                plot_bgcolor='rgba(248,249,250,1)',
                paper_bgcolor='rgba(255,255,255,1)',
                font=dict(color='black')
            )

            st.plotly_chart(fig, width='stretch')

            # 显示特征
            if characteristics:
                st.write("**当前阶段特征:**")
                for char in characteristics:
                    st.write(f"• {char}")

        except Exception as e:
            st.error(f"创建业务周期图时出错: {e}")

    def create_insights_dashboard(self, insights: List[str], title: str = "智能洞察") -> None:
        """创建洞察仪表板"""
        if not insights:
            st.info("暂无业务洞察数据")
            return

        st.markdown(f"### {title}")

        # 按重要性分组洞察
        strategic_insights = [i for i in insights if any(keyword in i for keyword in ['建议', '策略', '机会', '增长'])]
        warning_insights = [i for i in insights if any(keyword in i for keyword in ['风险', '警告', '问题', '挑战'])]
        operational_insights = [i for i in insights if i not in strategic_insights + warning_insights]

        insight_categories = [
            ("🚀 战略建议", strategic_insights, self.color_scheme['success']),
            ("⚠️ 风险预警", warning_insights, self.color_scheme['warning']),
            ("📈 运营优化", operational_insights, self.color_scheme['accent'])
        ]

        for category_title, category_insights, category_color in insight_categories:
            if category_insights:
                st.markdown(f"#### {category_title}")
                for insight in category_insights[:5]:  # 最多显示5条
                    st.markdown(f"<span style='color: {category_color};'>• {insight}</span>", unsafe_allow_html=True)


# 全局仪表板实例
financial_dashboard = FinancialDashboard()