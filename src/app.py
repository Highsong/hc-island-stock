# src/app.py
import streamlit as st
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.visualization.dashboard_layout import DashboardLayout
from src.visualization.chart_generator import ChartGenerator
from src.analysis.financial_metrics import FinancialMetrics
from src.analysis.trend_analysis import TrendAnalysis
from src.analysis.insights_generator import InsightsGenerator
from src.data_extraction.pdf_parser import PDFParser
from src.data_extraction.data_cleaner import DataCleaner
from src.utils.helpers import *

def main():
    """主应用函数"""
    # 初始化仪表板
    dashboard = DashboardLayout()
    dashboard.setup_page()

    # 页面标题
    st.title('🏮 贵州茅台年报分析系统')
    st.markdown('---')

    # 检测可用数据
    available_years = get_available_years()

    if not available_years:
        st.warning('📂 未检测到年报数据，请将PDF文件放入 data/raw_pdfs/ 目录')
        st.info('💡 支持的PDF文件命名格式：02MT2025年年报.pdf')
        return

    # 创建侧边栏
    filters = dashboard.create_sidebar(available_years)

    # 创建主标签页
    tab1, tab2, tab3, tab4 = dashboard.create_main_tabs()

    # 加载数据和分析
    with st.spinner('正在加载和分析数据...'):
        data_processor = DataProcessor()
        analysis_data = data_processor.process_selected_years(filters['years'])

    # 财务概览标签页
    with tab1:
        display_financial_overview(dashboard, analysis_data, filters)

    # 趋势分析标签页
    with tab2:
        display_trend_analysis(dashboard, analysis_data, filters)

    # 季度分析标签页
    with tab3:
        display_quarterly_analysis(dashboard, analysis_data, filters)

    # 综合报告标签页
    with tab4:
        display_comprehensive_report(dashboard, analysis_data, filters)

def get_available_years() -> List[str]:
    """获取可用的年份列表"""
    pdf_files = detect_new_reports()
    years = [extract_year_from_filename(f) for f in pdf_files]
    return sorted([y for y in years if y != '未知年份'], reverse=True)

def display_financial_overview(dashboard: DashboardLayout, data: Dict, filters: Dict):
    """显示财务概览"""
    st.header('📊 财务概览')

    if not data.get('latest_year'):
        st.info('请选择要分析的年份')
        return

    # 显示关键指标
    latest_metrics = data['latest_year']['key_metrics']
    dashboard.display_key_metrics(latest_metrics)

    # 显示图表
    col1, col2 = st.columns(2)

    with col1:
        if 'revenue_chart' in data['charts']:
            dashboard.display_chart_with_export(
                data['charts']['revenue_chart'],
                '营收趋势',
                filters['export_format']
            )

    with col2:
        if 'profit_chart' in data['charts']:
            dashboard.display_chart_with_export(
                data['charts']['profit_chart'],
                '利润分析',
                filters['export_format']
            )

    # 显示洞察
    if 'insights' in data:
        dashboard.display_insights(data['insights'])

def display_trend_analysis(dashboard: DashboardLayout, data: Dict, filters: Dict):
    """显示趋势分析"""
    st.header('📈 多年趋势分析')

    if len(filters['years']) < 2:
        st.info('趋势分析需要选择至少2个年份')
        return

    # 趋势图表
    if 'trend_charts' in data:
        for chart_name, chart in data['trend_charts'].items():
            dashboard.display_chart_with_export(
                chart,
                chart_name,
                filters['export_format']
            )

    # 趋势分析结果
    if 'trend_analysis' in data:
        st.subheader('📊 趋势分析结果')
        trend_df = pd.DataFrame(data['trend_analysis'])
        st.dataframe(trend_df.style.format({
            '复合增长率': '{:.2%}',
            '年均增长': '{:.2%}'
        }))

def display_quarterly_analysis(dashboard: DashboardLayout, data: Dict, filters: Dict):
    """显示季度分析"""
    st.header('🔍 季度业绩分析')

    if 'quarterly_data' not in data:
        st.info('暂无季度数据')
        return

    # 季度趋势图
    if 'quarterly_chart' in data['charts']:
        dashboard.display_chart_with_export(
            data['charts']['quarterly_chart'],
            '季度趋势',
            filters['export_format']
        )

    # 季节性分析
    if 'seasonal_patterns' in data:
        st.subheader('🎯 季节性模式分析')
        patterns = data['seasonal_patterns']

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('最强季度', patterns.get('最强季度', 'N/A'))
        with col2:
            st.metric('最弱季度', patterns.get('最弱季度', 'N/A'))
        with col3:
            st.metric('季度波动性', f"{patterns.get('季度波动性', 0):.2%}")

def display_comprehensive_report(dashboard: DashboardLayout, data: Dict, filters: Dict):
    """显示综合报告"""
    st.header('📋 综合分析报告')

    # 执行摘要
    st.subheader('📄 执行摘要')
    if 'executive_summary' in data:
        for summary_point in data['executive_summary']:
            st.markdown(f"- {summary_point}")

    # 详细分析
    st.subheader('🔍 详细分析')
    if 'insights' in data:
        dashboard.display_insights(data['insights'])

    # 风险评估
    st.subheader('⚠️ 风险提示')
    if 'risk_factors' in data:
        for risk in data['risk_factors']:
            st.warning(risk)

    # 投资建议
    st.subheader('💡 投资建议')
    if 'investment_recommendation' in data:
        recommendation = data['investment_recommendation']
        st.info(recommendation)

class DataProcessor:
    """数据处理协调器"""

    def __init__(self):
        self.parser = PDFParser()
        self.cleaner = DataCleaner()
        self.metrics_calculator = FinancialMetrics()
        self.trend_analyzer = TrendAnalysis()
        self.insights_generator = InsightsGenerator()
        self.chart_generator = ChartGenerator()

    def process_selected_years(self, selected_years: List[str]) -> Dict[str, Any]:
        """处理选定年份的数据"""
        result = {
            'charts': {},
            'insights': {},
            'latest_year': None,
            'trend_analysis': {},
            'quarterly_data': {},
            'seasonal_patterns': {}
        }

        # 加载和处理数据
        raw_data = self._load_year_data(selected_years)

        if not raw_data:
            return result

        # 计算财务指标
        financial_metrics = self._calculate_all_metrics(raw_data)

        # 生成图表
        charts = self._generate_charts(raw_data, financial_metrics)

        # 生成洞察
        insights = self._generate_insights(financial_metrics)

        # 趋势分析
        if len(selected_years) > 1:
            trend_analysis = self._perform_trend_analysis(raw_data)
            result['trend_analysis'] = trend_analysis

        # 更新结果
        result.update({
            'latest_year': self._get_latest_year_data(raw_data, financial_metrics),
            'charts': charts,
            'insights': insights,
            'raw_data': raw_data,
            'financial_metrics': financial_metrics
        })

        return result

    def _load_year_data(self, years: List[str]) -> Dict[str, Any]:
        """加载年度数据"""
        # 这里应该实现从PDF或已处理的数据文件加载数据
        # 为简化示例，返回模拟数据
        return self._get_sample_data(years)

    def _calculate_all_metrics(self, raw_data: Dict) -> Dict[str, Any]:
        """计算所有财务指标"""
        # 实现指标计算逻辑
        return {}

    def _generate_charts(self, raw_data: Dict, metrics: Dict) -> Dict[str, Any]:
        """生成图表"""
        # 实现图表生成逻辑
        return {}

    def _generate_insights(self, metrics: Dict) -> Dict[str, List[str]]:
        """生成分析洞察"""
        # 实现洞察生成逻辑
        return {}

    def _perform_trend_analysis(self, raw_data: Dict) -> Dict[str, Any]:
        """执行趋势分析"""
        # 实现趋势分析逻辑
        return {}

    def _get_latest_year_data(self, raw_data: Dict, metrics: Dict) -> Dict[str, Any]:
        """获取最新年度数据"""
        # 实现最新年度数据提取逻辑
        return {}

    def _get_sample_data(self, years: List[str]) -> Dict[str, Any]:
        """获取示例数据（用于演示）"""
        # 这里提供示例数据，实际应用中应该从PDF提取
        return {
            'sample': {
                'revenue': [1000, 1200, 1400, 1600, 1800],
                'profit': [200, 240, 280, 320, 360]
            }
        }

if __name__ == '__main__':
    main()