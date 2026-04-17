# src/visualization/chart_generator.py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class ChartGenerator:
    """图表生成器"""

    def __init__(self):
        self.color_scheme = {
            'primary': '#E74C3C',    # 茅台红
            'secondary': '#F39C12',  # 金色
            'accent': '#3498DB',     # 蓝色
            'neutral': '#95A5A6',    # 灰色
            'success': '#27AE60',    # 绿色
            'warning': '#F1C40F'     # 黄色
        }

    def create_line_chart(self, data: Dict[str, List], y_column: str, title: str,
                         show_trend: bool = True) -> go.Figure:
        """创建折线图"""
        df = pd.DataFrame(data)

        fig = go.Figure()

        # 主折线
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0],  # 第一列作为x轴
            y=df[y_column],
            mode='lines+markers',
            name=y_column,
            line=dict(color=self.color_scheme['primary'], width=3),
            marker=dict(size=8, symbol='circle')
        ))

        # 趋势线
        if show_trend and len(df) > 2:
            z = np.polyfit(range(len(df)), df[y_column], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0],
                y=p(range(len(df))),
                mode='lines',
                name='趋势线',
                line=dict(color=self.color_scheme['secondary'], dash='dash'),
                showlegend=True
            ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            xaxis_title=df.columns[0],
            yaxis_title=y_column,
            template='plotly_white',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig

    def create_bar_chart(self, data: Dict[str, List], y_column: str, title: str,
                        horizontal: bool = False) -> go.Figure:
        """创建柱状图"""
        df = pd.DataFrame(data)

        if horizontal:
            fig = go.Figure(go.Bar(
                y=df.iloc[:, 0],
                x=df[y_column],
                orientation='h',
                marker_color=self.color_scheme['primary']
            ))
            fig.update_layout(
                xaxis_title=y_column,
                yaxis_title=df.columns[0]
            )
        else:
            fig = go.Figure(go.Bar(
                x=df.iloc[:, 0],
                y=df[y_column],
                marker_color=self.color_scheme['primary']
            ))
            fig.update_layout(
                xaxis_title=df.columns[0],
                yaxis_title=y_column
            )

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            template='plotly_white',
            showlegend=False
        )

        return fig

    def create_pie_chart(self, data: Dict[str, List], names_column: str,
                        values_column: str, title: str) -> go.Figure:
        """创建饼图"""
        df = pd.DataFrame(data)

        fig = go.Figure(go.Pie(
            labels=df[names_column],
            values=df[values_column],
            hole=0.4,
            marker_colors=list(self.color_scheme.values())
        ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            template='plotly_white'
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')

        return fig

    def create_waterfall_chart(self, data: Dict[str, List], title: str) -> go.Figure:
        """创建瀑布图（用于利润分析）"""
        df = pd.DataFrame(data)

        # 计算累计值
        measures = ["relative"] * (len(df) - 2) + ["total", "total"]

        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=measures,
            x=df.iloc[:, 0],
            y=df['金额'],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": self.color_scheme['success']}},
            decreasing={"marker": {"color": self.color_scheme['primary']}},
            totals={"marker": {"color": self.color_scheme['secondary']}}
        ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            template='plotly_white',
            showlegend=False
        )

        return fig

    def create_combined_chart(self, data: Dict[str, List], primary_y: str,
                             secondary_y: str, title: str) -> go.Figure:
        """创建双轴组合图"""
        df = pd.DataFrame(data)

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 主轴数据（柱状图）
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0],
            y=df[primary_y],
            name=primary_y,
            marker_color=self.color_scheme['primary']
        ), secondary_y=False)

        # 次轴数据（折线图）
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0],
            y=df[secondary_y],
            name=secondary_y,
            mode='lines+markers',
            line=dict(color=self.color_scheme['secondary'], width=3),
            marker=dict(size=8)
        ), secondary_y=True)

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            template='plotly_white',
            barmode='group'
        )

        fig.update_yaxes(title_text=primary_y, secondary_y=False)
        fig.update_yaxes(title_text=secondary_y, secondary_y=True)

        return fig

    def create_financial_dashboard(self, metrics_data: Dict[str, Any]) -> Dict[str, go.Figure]:
        """创建财务仪表板图表集合"""
        charts = {}

        # 营收趋势图
        if 'revenue_data' in metrics_data:
            charts['revenue_trend'] = self.create_line_chart(
                metrics_data['revenue_data'], '营业收入', '营业收入趋势分析'
            )

        # 利润对比图
        if 'profit_data' in metrics_data:
            charts['profit_comparison'] = self.create_bar_chart(
                metrics_data['profit_data'], '净利润', '净利润年度对比'
            )

        # 财务比率组合图
        if 'ratios_data' in metrics_data:
            charts['ratios_combo'] = self.create_combined_chart(
                metrics_data['ratios_data'], '净利润率', '营业收入增长率', '盈利能力与增长性分析'
            )

        return charts