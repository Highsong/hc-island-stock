# src/visualization/chart_generator.py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class ChartGenerator:
    """图表生成器"""

    # 四套不同的图表背景配色（用于趋势分析四个图各不相同）
    CHART_BG_PRESETS = [
        {   # 0: 蓝灰调（增长率图）
            'paper_bgcolor': 'rgba(244,247,252,1)',
            'plot_bgcolor': 'rgba(236,240,249,1)',
            'gridcolor': 'rgba(200,210,230,1)',
            'zerolinecolor': 'rgba(160,175,200,1)',
        },
        {   # 1: 暖橙调（成本费用图）
            'paper_bgcolor': 'rgba(252,247,242,1)',
            'plot_bgcolor': 'rgba(249,242,235,1)',
            'gridcolor': 'rgba(230,215,195,1)',
            'zerolinecolor': 'rgba(200,180,160,1)',
        },
        {   # 2: 淡绿调（应收/负债图）
            'paper_bgcolor': 'rgba(242,250,245,1)',
            'plot_bgcolor': 'rgba(235,247,238,1)',
            'gridcolor': 'rgba(195,225,205,1)',
            'zerolinecolor': 'rgba(160,200,175,1)',
        },
        {   # 3: 淡紫调（合同负债图）
            'paper_bgcolor': 'rgba(248,244,252,1)',
            'plot_bgcolor': 'rgba(242,236,250,1)',
            'gridcolor': 'rgba(215,200,235,1)',
            'zerolinecolor': 'rgba(185,170,210,1)',
        },
    ]

    def __init__(self):
        self.color_scheme = {
            'primary': '#E74C3C',    # 主色调红
            'secondary': '#F39C12',  # 辅助色金
            'accent': '#3498DB',     # 强调色蓝
            'neutral': '#95A5A6',    # 中性色灰
            'success': '#27AE60',    # 成功色绿
            'warning': '#F1C40F'     # 警告色黄
        }
        # 默认图表背景配色（浅色系，兼容 dark 模式会用 _apply_common_style 覆盖）
        self.chart_bg = self.CHART_BG_PRESETS[0].copy()

    def _apply_common_style(self, fig: go.Figure, is_growth_rate: bool = False,
                            bg_preset: int = None):
        """应用通用美化样式

        Args:
            bg_preset: 使用 CHART_BG_PRESETS 中的哪一套（0-3），None 用默认
        """
        if bg_preset is not None:
            bg = self.CHART_BG_PRESETS[bg_preset % len(self.CHART_BG_PRESETS)]
        else:
            bg = self.chart_bg
        fig.update_layout(
            paper_bgcolor=bg['paper_bgcolor'],
            plot_bgcolor=bg['plot_bgcolor'],
            font=dict(color='#333', family='Arial, sans-serif'),
            xaxis=dict(
                showgrid=True, gridcolor=bg['gridcolor'],
                zerolinecolor=bg['zerolinecolor'],
                tickfont=dict(color='#555', size=11),
                linecolor='#ccc',
            ),
            yaxis=dict(
                showgrid=True, gridcolor=bg['gridcolor'],
                zerolinecolor=bg['zerolinecolor'],
                tickfont=dict(color='#555', size=11),
                linecolor='#ccc',
                ticksuffix='%' if is_growth_rate else '',
                tickformat='.1f' if is_growth_rate else ',.2f',
            ),
            legend=dict(
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#ddd',
                borderwidth=1,
                font=dict(size=11, color='#444'),
            ),
            margin=dict(l=60, r=30, t=60, b=50),
        )
        return fig

    def _add_data_labels(self, fig: go.Figure, texttemplate: str = '%{y:.1f}',
                         textposition: str = 'top center', skip_zero: bool = False):
        """为所有 trace 添加数据标签"""
        for trace in fig.data:
            if hasattr(trace, 'texttemplate') and trace.texttemplate:
                continue  # 已有标签
            trace.update(texttemplate=texttemplate, textposition=textposition,
                         textfont=dict(size=10, color='#444'))
        return fig

    def create_line_chart(self, data: Dict[str, List], y_column: str, title: str,
                         show_trend: bool = True, show_labels: bool = True,
                         label_fmt: str = '{:.2f}') -> go.Figure:
        """创建折线图（默认显示数据标签）"""
        if y_column in data:
            data[y_column] = [float(val) if val is not None and str(val).replace('.','').replace('-','').replace('e','').isdigit() else 0.0 for val in data[y_column]]

        df = pd.DataFrame(data)
        is_yi = '亿' in y_column
        fmt = label_fmt + ('亿' if is_yi else '')

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0],
            y=df[y_column],
            mode='lines+markers+text' if show_labels else 'lines+markers',
            name=y_column,
            line=dict(color=self.color_scheme['primary'], width=2.5),
            marker=dict(size=7, symbol='circle', line=dict(width=1, color='white')),
            text=[fmt.format(v) for v in df[y_column]] if show_labels else None,
            textposition='top center',
            textfont=dict(size=10, color='#444'),
            hovertemplate=f'%{{y:.2f}}{"亿" if is_yi else ""}<extra></extra>'
        ))

        if show_trend and len(df) > 2:
            z = np.polyfit(range(len(df)), df[y_column], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0],
                y=p(range(len(df))),
                mode='lines',
                name='趋势线',
                line=dict(color=self.color_scheme['secondary'], dash='dash', width=1.5),
                showlegend=True,
                hoverinfo='skip'
            ))

        self._apply_common_style(fig)
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='#333', size=15, weight=600)),
            xaxis_title=dict(text=df.columns[0], font=dict(color='#666')),
            yaxis_title=dict(text=y_column, font=dict(color='#666')),
            hovermode='x unified',
        )
        return fig

    def create_bar_chart(self, data: Dict[str, List], y_column: str, title: str,
                        horizontal: bool = False, show_labels: bool = True,
                        label_fmt: str = '{:.2f}') -> go.Figure:
        """创建柱状图（默认显示数据标签）"""
        df = pd.DataFrame(data)
        is_yi = '亿' in y_column
        fmt = label_fmt + ('亿' if is_yi else '')
        colors = [self.color_scheme['primary'], self.color_scheme['secondary'],
                  self.color_scheme['accent'], self.color_scheme['success'],
                  self.color_scheme['warning']]

        bar_kwargs = dict(
            marker_line=dict(width=0),
            hovertemplate=f'%{{y:.2f}}{"亿" if is_yi else ""}<extra></extra>',
        )

        if show_labels:
            bar_kwargs['text'] = [fmt.format(v) for v in df[y_column]]
            bar_kwargs['textposition'] = 'outside'
            bar_kwargs['textfont'] = dict(size=10, color='#444')

        if horizontal:
            bar_kwargs.update(y=df.iloc[:, 0], x=df[y_column], orientation='h')
            fig = go.Figure(go.Bar(**bar_kwargs))
        else:
            num_bars = len(df)
            bar_colors = [colors[i % len(colors)] for i in range(num_bars)]
            bar_kwargs.update(x=df.iloc[:, 0], y=df[y_column], marker_color=bar_colors)
            fig = go.Figure(go.Bar(**bar_kwargs))

        self._apply_common_style(fig)
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='#333', size=15, weight=600)),
            showlegend=False,
            margin=dict(l=60, r=30, t=60, b=50),
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
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='black', size=16)),
            template='plotly',
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(255,255,255,1)',
            font=dict(color='black')
        )

        fig.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color='white'))

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
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='black', size=16)),
            template='plotly',
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(255,255,255,1)',
            font=dict(color='black'),
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='black', tickfont=dict(color='black')),
            yaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='black', tickfont=dict(color='black'), tickformat=',.2f')
        )

        return fig

    def create_combined_chart(self, data: Dict[str, List], primary_y: str,
                             secondary_y: str, title: str,
                             is_growth_rate: bool = False,
                             show_labels: bool = True,
                             bg_preset: int = None) -> go.Figure:
        """创建双轴组合图（默认显示数据标签）

        Args:
            is_growth_rate: True 时两条线都是增长率曲线（折线+虚线），y轴单位%；
                            False 时主柱次线（营收/利润金额图）
            show_labels: 是否直接显示数据标签
        """
        df = pd.DataFrame(data)
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        if is_growth_rate:
            # 主轴折线
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0],
                y=df[primary_y],
                name=primary_y,
                mode='lines+markers+text' if show_labels else 'lines+markers',
                line=dict(color=self.color_scheme['primary'], width=2.5),
                marker=dict(size=7, symbol='circle', line=dict(width=1, color='white')),
                text=[f'{v:.1f}%' for v in df[primary_y]] if show_labels else None,
                textposition='top center',
                textfont=dict(size=10, color=self.color_scheme['primary']),
                hovertemplate='%{y:.1f}%<extra></extra>'
            ), secondary_y=False)

            # 次轴折线（虚线）
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0],
                y=df[secondary_y],
                name=secondary_y,
                mode='lines+markers+text' if show_labels else 'lines+markers',
                line=dict(color=self.color_scheme['secondary'], width=2.5, dash='dash'),
                marker=dict(size=7, symbol='diamond', line=dict(width=1, color='white')),
                text=[f'{v:.1f}%' for v in df[secondary_y]] if show_labels else None,
                textposition='bottom center',
                textfont=dict(size=10, color=self.color_scheme['secondary']),
                hovertemplate='%{y:.1f}%<extra></extra>'
            ), secondary_y=False)

            fig.update_yaxes(
                title_text='同比 (%)', secondary_y=False,
                ticksuffix='%', tickformat='.1f',
            )
        else:
            # 主轴柱状图
            fig.add_trace(go.Bar(
                x=df.iloc[:, 0],
                y=df[primary_y],
                name=primary_y,
                marker_color=self.color_scheme['primary'],
                marker_line=dict(width=0),
                text=[f'{v:.2f}' for v in df[primary_y]] if show_labels else None,
                textposition='outside',
                textfont=dict(size=10, color='#444'),
                hovertemplate='%{y:.2f}亿<extra></extra>'
            ), secondary_y=False)

            # 次轴折线
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0],
                y=df[secondary_y],
                name=secondary_y,
                mode='lines+markers+text' if show_labels else 'lines+markers',
                line=dict(color=self.color_scheme['secondary'], width=2.5),
                marker=dict(size=7, line=dict(width=1, color='white')),
                text=[f'{v:.2f}' for v in df[secondary_y]] if show_labels else None,
                textposition='top center',
                textfont=dict(size=10, color=self.color_scheme['secondary']),
                hovertemplate='%{y:.2f}亿<extra></extra>'
            ), secondary_y=True)

            fig.update_yaxes(title_text=f'{primary_y}', secondary_y=False)
            fig.update_yaxes(title_text=f'{secondary_y}', secondary_y=True)

        self._apply_common_style(fig, is_growth_rate=is_growth_rate, bg_preset=bg_preset)
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='#333', size=15, weight=600)),
            barmode='group',
            hovermode='x unified',
        )
        return fig

    def create_bar_line_chart(self, data: Dict[str, List], bar_column: str,
                              line_column: str, title: str,
                              bar_name: str = None, line_name: str = None,
                              show_labels: bool = True,
                              label_fmt: str = '{:.2f}',
                              bg_preset: int = None) -> go.Figure:
        """创建柱状图+折线图双轴组合（用于合同负债等场景）"""
        df = pd.DataFrame(data)
        bar_name = bar_name or bar_column
        line_name = line_name or line_column

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        colors = [self.color_scheme['primary'], self.color_scheme['secondary'],
                  self.color_scheme['accent'], self.color_scheme['success']]

        # 柱状图（主轴）
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0],
            y=df[bar_column],
            name=bar_name,
            marker_color=[colors[i % len(colors)] for i in range(len(df))],
            marker_line=dict(width=0),
            text=[label_fmt.format(v) for v in df[bar_column]] if show_labels else None,
            textposition='outside',
            textfont=dict(size=10, color='#444'),
            hovertemplate=f'%{{y:{label_fmt}}}<extra></extra>'
        ), secondary_y=False)

        # 折线图（次轴）
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0],
            y=df[line_column],
            name=line_name,
            mode='lines+markers+text' if show_labels else 'lines+markers',
            line=dict(color='#e65100', width=2.5),
            marker=dict(size=8, symbol='diamond', line=dict(width=1, color='white')),
            text=[f'{v:.1f}%' for v in df[line_column]] if show_labels else None,
            textposition='top center',
            textfont=dict(size=11, color='#1a1a1a', family='Arial Black, sans-serif'),
            hovertemplate='%{y:.1f}%<extra></extra>'
        ), secondary_y=True)

        self._apply_common_style(fig, bg_preset=bg_preset)
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='#333', size=15, weight=600)),
            barmode='group',
            hovermode='x unified',
            margin=dict(l=60, r=60, t=60, b=50),
        )
        fig.update_yaxes(title_text=bar_name, secondary_y=False)
        fig.update_yaxes(title_text=line_name, ticksuffix='%', secondary_y=True)
        return fig

    def create_heatmap_chart(self, data: Dict[str, List], title: str,
                           x_labels: List[str] = None, y_labels: List[str] = None) -> go.Figure:
        """创建热力图（用于相关性分析）"""
        df = pd.DataFrame(data)

        fig = go.Figure(data=go.Heatmap(
            z=df.values,
            x=x_labels or df.columns,
            y=y_labels or [f"指标{i+1}" for i in range(len(df.index))],
            colorscale='RdBu_r',
            reversescale=True,
            colorbar=dict(title="相关性"),
            hoverongaps=False
        ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='black', size=16)),
            template='plotly',
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(255,255,255,1)',
            font=dict(color='black'),
            xaxis=dict(tickfont=dict(color='black')),
            yaxis=dict(tickfont=dict(color='black'))
        )

        return fig

    def create_candlestick_chart(self, data: Dict[str, List], title: str) -> go.Figure:
        """创建蜡烛图（模拟股价走势）"""
        df = pd.DataFrame(data)

        # 生成模拟的OHLC数据
        dates = pd.date_range(start='2023-01-01', periods=len(df), freq='Q')

        fig = go.Figure(data=go.Candlestick(
            x=dates,
            open=[row.get('open', 0) for _, row in df.iterrows()],
            high=[row.get('high', 0) for _, row in df.iterrows()],
            low=[row.get('low', 0) for _, row in df.iterrows()],
            close=[row.get('close', 0) for _, row in df.iterrows()],
            increasing_line_color=self.color_scheme['success'],
            decreasing_line_color=self.color_scheme['primary']
        ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='black', size=16)),
            xaxis_title='时间',
            yaxis_title='价格',
            template='plotly',
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(255,255,255,1)',
            font=dict(color='black'),
            xaxis=dict(rangeslider=dict(visible=True), type="date", tickfont=dict(color='black')),
            yaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='black', tickfont=dict(color='black'), tickformat=',.2f')
        )

        return fig

    def create_radar_chart(self, data: Dict[str, float], title: str) -> go.Figure:
        """创建雷达图（多维度评估）"""
        categories = list(data.keys())
        values = list(data.values())

        # 闭合雷达图
        categories.append(categories[0])
        values.append(values[0])

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='综合评分',
            line=dict(color=self.color_scheme['accent'], width=3),
            marker=dict(size=8, color=self.color_scheme['accent'])
        ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='black', size=16)),
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2],
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

        return fig

    def create_scatter_plot(self, data: Dict[str, List], x_column: str,
                          y_column: str, title: str, trendline: bool = True) -> go.Figure:
        """创建散点图（相关性分析）"""
        df = pd.DataFrame(data)

        fig = go.Figure()

        # 主散点
        fig.add_trace(go.Scatter(
            x=df[x_column],
            y=df[y_column],
            mode='markers',
            marker=dict(
                size=12,
                color=self.color_scheme['primary'],
                opacity=0.7,
                line=dict(width=2, color='white')
            ),
            text=[f"{x}: {y:.2f}" for x, y in zip(df[x_column], df[y_column])],
            hovertemplate="<b>%{text}</b><extra></extra>"
        ))

        # 趋势线
        if trendline and len(df) > 1:
            try:
                z = np.polyfit(df[x_column], df[y_column], 1)
                p = np.poly1d(z)

                fig.add_trace(go.Scatter(
                    x=df[x_column],
                    y=p(df[x_column]),
                    mode='lines',
                    name='回归线',
                    line=dict(color=self.color_scheme['secondary'], width=2, dash='dot'),
                    showlegend=True
                ))

                # 显示相关系数
                corr_coef = np.corrcoef(df[x_column], df[y_column])[0, 1]
                trend_text = f"相关系数: {corr_coef:.3f}"

                fig.add_annotation(
                    x=0.05, y=0.95,
                    xref="paper", yref="paper",
                    text=trend_text,
                    showarrow=False,
                    font=dict(size=12, color='black'),
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='lightgray',
                    borderwidth=1
                )

            except Exception as e:
                print(f"计算趋势线时出错: {e}")

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='black', size=16)),
            xaxis_title=x_column,
            yaxis_title=y_column,
            template='plotly',
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(255,255,255,1)',
            font=dict(color='black'),
            hovermode='closest',
            showlegend=True,
            xaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='black', tickfont=dict(color='black')),
            yaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='black', tickfont=dict(color='black'), tickformat=',.2f')
        )

        return fig

    def create_multi_line_chart(self, data: Dict[str, List], title: str,
                              value_columns: List[str] = None) -> go.Figure:
        """创建多线图（对比分析）"""
        df = pd.DataFrame(data)

        if value_columns is None:
            # 自动检测数值列
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_columns = numeric_cols[:5]  # 最多显示5条线

        fig = go.Figure()

        colors = [
            self.color_scheme['primary'],
            self.color_scheme['secondary'],
            self.color_scheme['accent'],
            self.color_scheme['success'],
            self.color_scheme['warning']
        ]

        for i, col in enumerate(value_columns):
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.iloc[:, 0],  # 假设第一列为时间/类别
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6, symbol='circle' if i % 2 == 0 else 'diamond')
                ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(color='black', size=16)),
            xaxis_title=df.columns[0],
            yaxis_title='数值',
            template='plotly',
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(255,255,255,1)',
            font=dict(color='black'),
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='black')),
            xaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='black', tickfont=dict(color='black')),
            yaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='black', tickfont=dict(color='black'), tickformat=',.2f')
        )

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
                metrics_data['profit_data'], '归母净利润', '归母净利润年度对比'
            )

        # 财务比率组合图
        if 'ratios_data' in metrics_data:
            charts['ratios_combo'] = self.create_combined_chart(
                metrics_data['ratios_data'], '净利润率', '营业收入增长率', '盈利能力与增长性分析'
            )

        return charts