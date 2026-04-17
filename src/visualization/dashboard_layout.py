# src/visualization/dashboard_layout.py
import streamlit as st
from typing import Dict, List, Any
import plotly.graph_objects as go

class DashboardLayout:
    """仪表板布局管理器"""

    def __init__(self):
        self.page_config = {
            'page_title': '茅台年报分析系统',
            'page_icon': '🏮',
            'layout': 'wide',
            'initial_sidebar_state': 'expanded'
        }

    def setup_page(self):
        """设置页面配置"""
        st.set_page_config(**self.page_config)

        # 自定义CSS样式
        st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 0.5rem solid #e74c3c;
        }
        .insight-box {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
        }
        .chart-container {
            background-color: white;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

    def create_sidebar(self, available_years: List[str]) -> Dict[str, Any]:
        """创建侧边栏"""
        st.sidebar.title('🏮 茅台分析系统')

        # 年份选择
        selected_years = st.sidebar.multiselect(
            '选择年份',
            available_years,
            default=available_years[-3:]  # 默认选择最近3年
        )

        # 分析类型选择
        analysis_type = st.sidebar.radio(
            '分析类型',
            ['单年分析', '多年趋势', '季度分析', '综合报告']
        )

        # 指标筛选
        metrics_options = [
            '盈利能力', '成长性', '流动性', '杠杆水平', '现金流量'
        ]
        selected_metrics = st.sidebar.multiselect(
            '关注指标',
            metrics_options,
            default=metrics_options
        )

        # 导出选项
        st.sidebar.markdown('---')
        st.sidebar.subheader('导出选项')
        export_format = st.sidebar.radio('导出格式', ['PNG', 'PDF', 'Excel'])

        return {
            'years': selected_years,
            'analysis_type': analysis_type,
            'metrics': selected_metrics,
            'export_format': export_format
        }

    def create_main_tabs(self):
        """创建主标签页"""
        return st.tabs([
            '📊 财务概览',
            '📈 趋势分析',
            '🔍 季度分析',
            '📋 综合报告'
        ])

    def display_key_metrics(self, metrics_data: Dict[str, float]):
        """显示关键指标卡片"""
        st.subheader('🔑 关键财务指标')

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label='营业收入',
                value=f"¥{metrics_data.get('revenue', 0):,.0f}亿",
                delta=f"{metrics_data.get('revenue_growth', 0):+.1f}%"
            )

        with col2:
            st.metric(
                label='净利润',
                value=f"¥{metrics_data.get('net_profit', 0):,.0f}亿",
                delta=f"{metrics_data.get('profit_growth', 0):+.1f}%"
            )

        with col3:
            st.metric(
                label='净利润率',
                value=f"{metrics_data.get('profit_margin', 0):.1%}",
                delta=f"{metrics_data.get('margin_change', 0):+.1f}pp"
            )

        with col4:
            st.metric(
                label='ROE',
                value=f"{metrics_data.get('roe', 0):.1%}",
                delta=f"{metrics_data.get('roe_change', 0):+.1f}pp"
            )

    def display_insights(self, insights: Dict[str, List[str]]):
        """显示分析洞察"""
        st.subheader('💡 智能分析洞察')

        for category, insight_list in insights.items():
            if insight_list:
                with st.expander(f"{self._get_category_icon(category)} {self._get_category_name(category)}",
                               expanded=True):
                    for insight in insight_list:
                        st.markdown(f'<div class="insight-box">{insight}</div>',
                                  unsafe_allow_html=True)

    def display_chart_with_export(self, fig: go.Figure, chart_title: str,
                                 export_format: str = 'PNG'):
        """显示图表并提供导出功能"""
        st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

        # 导出按钮
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button(f'导出 {export_format}', key=f'export_{chart_title}'):
                self._export_chart(fig, chart_title, export_format)

        st.markdown('</div>', unsafe_allow_html=True)

    def _get_category_icon(self, category: str) -> str:
        """获取分类图标"""
        icons = {
            'profitability': '💰',
            'growth': '📈',
            'liquidity': '💧',
            'risk': '⚠️',
            'overall': '🎯'
        }
        return icons.get(category, '📊')

    def _get_category_name(self, category: str) -> str:
        """获取分类名称"""
        names = {
            'profitability': '盈利能力分析',
            'growth': '成长性分析',
            'liquidity': '流动性分析',
            'risk': '风险分析',
            'overall': '综合评价'
        }
        return names.get(category, category)

    def _export_chart(self, fig: go.Figure, title: str, format_type: str):
        """导出图表"""
        filename = f"茅台分析_{title.replace(' ', '_')}.{format_type.lower()}"

        try:
            if format_type == 'PNG':
                fig.write_image(filename, scale=2)
            elif format_type == 'PDF':
                fig.write_image(filename)

            st.success(f'图表已导出为 {filename}')
        except Exception as e:
            st.error(f'导出失败: {e}')