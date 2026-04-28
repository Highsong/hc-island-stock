# src/app_new.py
"""
通用股票财务分析系统
支持A股和港股，多数据源（雪球 > AKShare > 示例数据）
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from visualization.dashboard_layout import DashboardLayout
from visualization.chart_generator import ChartGenerator
from analysis.financial_metrics import FinancialMetrics
from analysis.trend_analysis import TrendAnalysis
from analysis.insights_generator import InsightsGenerator
from analysis.dupont_analysis import calculate_dupont_with_comparison
from analysis.porter_five_forces import analyze_porter_five_forces
from data_extraction.stock_data_source import StockDataSource
from data_extraction.xueqiu_data_source import XueqiuDataSource
from data_extraction.sample_data_source import SampleDataSource
from data_extraction.data_source_manager import DataSourceManager
from utils.helpers import *
from utils.cache_manager import cache_manager
from portfolio_view import render_portfolio_page

# ──────────────────────────────────────────────
# 全局数据源管理器（按优先级注册）
# ──────────────────────────────────────────────
_data_source_manager: DataSourceManager = None


def get_data_source_manager() -> DataSourceManager:
    """获取全局数据源管理器（懒加载单例）"""
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
        # 优先级：雪球 > AKShare > 示例数据
        _data_source_manager.register(XueqiuDataSource())
        _data_source_manager.register(StockDataSource())
        _data_source_manager.register(SampleDataSource())
    return _data_source_manager

def main():
    """主应用函数"""
    # 初始化仪表板
    dashboard = DashboardLayout()
    dashboard.setup_page()

    # 初始化页面模式
    if "_page_mode" not in st.session_state:
        st.session_state["_page_mode"] = "analysis"

    # 页面标题
    st.title('📊 通用股票财务分析系统')
    st.markdown('---')

    # 股票选择区域
    st.sidebar.header('🎯 股票选择')

    # 股票代码输入
    stock_code = st.sidebar.text_input(
        '股票代码',
        value='600519',
        help='输入股票代码，如：000858(五粮液), 600519(贵州茅台), 0700.HK(腾讯)'
    ).strip()

    # 数据周期选择
    period_options = {
        '年度': 'year',
        '半年度': 'year_half',
        '三季度': 'Q3',
        '一季度': 'Q1',
    }
    selected_period_label = st.sidebar.selectbox(
        '数据周期',
        options=list(period_options.keys()),
        index=0,
        help='选择财务数据的报告周期'
    )
    period = period_options[selected_period_label]

    # 获取可用年份范围
    current_year = datetime.now().year
    available_years = [str(year) for year in range(1990, current_year + 1)]

    # 年份范围选择（在开始分析按钮上面）
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_year = st.selectbox('开始年份', options=available_years, index=len(available_years) - 5)
    with col2:
        end_year = st.selectbox('结束年份', options=available_years, index=len(available_years) - 1)

    # 分析按钮
    analyze_btn = st.sidebar.button('🔍 开始分析', type='primary')

    # ── 我的投资（侧边栏底部）──
    st.sidebar.markdown("---")
    if st.sidebar.button("💼 我的投资", key="btn_my_portfolio"):
        st.session_state["_page_mode"] = "portfolio"
        st.rerun()

    # ── 页面路由 ──
    if st.session_state.get("_page_mode") == "portfolio":
        render_portfolio_page()
        # 返回按钮
        if st.sidebar.button("⬅️ 返回分析", key="btn_back_to_analysis"):
            st.session_state["_page_mode"] = "analysis"
            st.rerun()
        return

    # ── 判断是否需要重新分析 ──
    need_analysis = False
    if analyze_btn:
        # 点击了开始分析按钮
        need_analysis = True
    elif 'cached_analysis_data' in st.session_state and 'cached_filters' in st.session_state:
        # 有缓存数据，直接复用（侧边栏参数变化不触发重新分析）
        need_analysis = False
    else:
        # 首次加载，无缓存，显示欢迎页
        display_welcome_message()
        return

    if not stock_code:
        st.warning('👆 请在左侧输入股票代码')
        return

    # ── 构建过滤器 ──
    filters = {
        'start_year': start_year,
        'end_year': end_year,
        'period': period,
        'export_format': 'PNG'
    }

    if need_analysis:
        # 保存分析状态
        st.session_state.last_analyzed_stock = stock_code
        st.session_state.last_analyzed_period = period

        # 获取股票基本信息
        stock_info = {}
        try:
            dsm = get_data_source_manager()
            stock_info = dsm.get_stock_info(stock_code)
        except Exception as e:
            print(f"获取股票信息失败: {e}")
            st.error(f'获取股票信息失败: {e}')
            return

        # ── 数据源状态检测 ──
        try:
            dsm_check = get_data_source_manager()
            if hasattr(dsm_check, '_sources'):
                for _src in dsm_check._sources:
                    if '雪球' in _src.get_name():
                        _avail = _src.is_available()
                        if not _avail:
                            st.warning(
                                "⚠️ **雪球 Cookie 已过期**，当前使用 AKShare/示例数据源，数据可能不完整。\n\n"
                                "**更新方法：** 打开 https://xueqiu.com → F12 Network → 随便点一个请求 → "
                                "复制 Cookie 中的 `xq_a_token` → 更新 `config/XueQiuCookie.txt` → 刷新页面"
                            )
                        break
        except Exception:
            pass

        # 加载数据和分析
        try:
            with st.spinner(f'正在获取和分析 {stock_code} 的财务数据...'):
                data_processor = DataProcessor()
                analysis_data = data_processor.process_stock_data(
                    stock_code,
                    filters['start_year'],
                    filters['end_year'],
                    period,
                    selected_period_label,
                    stock_info=stock_info,
                )

            if not analysis_data or not analysis_data.get('periods'):
                st.error(f'❌ 无法获取股票 {stock_code} 的数据')
                st.info('💡 可能的原因：\n- 股票代码格式不正确\n- 网络连接问题\n- 数据源暂时不可用')
                st.markdown("**支持的股票代码格式：**\n- A股：000858(五粮液), 600519(贵州茅台)\n- 港股：0700.HK(腾讯), 0941.HK(中国移动)")
                return

            # 缓存分析结果 + 图表 key（用于判断是否需要重新创建图表）
            st.session_state.cached_analysis_data = analysis_data
            st.session_state.cached_filters = filters
            st.session_state.cached_stock_info = stock_info
            st.session_state._chart_data_key = f"{stock_code}_{start_year}_{end_year}_{period}"

        except Exception as e:
            st.error(f'X: data error: {str(e)}')
            st.info('check connection')
            return

    # ── 从缓存读取数据用于展示 ──
    analysis_data = st.session_state.get('cached_analysis_data', {})
    filters = st.session_state.get('cached_filters', filters)

    if not analysis_data or not analysis_data.get('periods'):
        display_welcome_message()
        return

    # ── 创建主标签页并展示 ──
    tab1, tab2, tab3, tab4 = dashboard.create_main_tabs()

    with tab1:
        display_financial_overview(dashboard, analysis_data, filters)

    with tab2:
        display_trend_analysis(dashboard, analysis_data, filters)

    with tab3:
        display_period_analysis(dashboard, analysis_data, filters)

    with tab4:
        display_comprehensive_report(dashboard, analysis_data, filters)

def display_welcome_message():
    """显示欢迎信息"""
    st.markdown("""
    ## 👋 欢迎使用通用股票财务分析系统

    ### 📋 功能特性
    - **📈 多股票支持**: 支持A股和港股财务数据分析
    - **📊 多周期分析**: 支持年度、半年度、三季度、一季度数据分析
    - **🔄 实时数据**: 基于AKshare API获取最新财务数据
    - **💾 智能缓存**: 自动缓存数据，提高访问速度
    - **📋 专业分析**: 财务指标计算、趋势分析、风险评估

    ### 🎯 使用说明
    1. 在左侧边栏输入股票代码
    2. 选择数据周期（年度/半年度/三季度/一季度）
    3. 设置分析年份范围
    4. 点击"开始分析"按钮

    ### 💡 支持的股票代码格式
    - **A股**: 000858(五粮液), 600519(贵州茅台), 000001(平安银行)
    - **港股**: 0700.HK(腾讯), 0941.HK(中国移动), 0005.HK(汇丰控股)

    **开始您的股票分析之旅吧！** 🚀
    """)

def display_stock_info(stock_code: str):
    """显示股票基本信息（兼容旧调用，实际已改为内联副标题）"""
    # 此函数保留以兼容旧调用，但新的显示逻辑已改为 _stock_inline_subtitle()
    pass


def _stock_inline_subtitle(stock_code: str) -> str:
    """生成股票信息小字副标题文本，用于追加到各 tab 标题下方"""
    try:
        dsm = get_data_source_manager()
        info = dsm.get_stock_info(stock_code)
        name = info.get("name", f"股票 {stock_code}")
        market = info.get("market", "—")
        industry = info.get("industry", "—")
        return f"{name} · {stock_code} · {market} · {industry}"
    except Exception:
        return f"股票 {stock_code}"

def display_financial_overview(dashboard: DashboardLayout, data: Dict, filters: Dict):
    """显示财务概览"""
    stock_code = filters.get('stock_code', '') or st.session_state.get('last_analyzed_stock', '')
    subtitle = _stock_inline_subtitle(stock_code)
    st.markdown(
        f"<div style='display:flex;align-items:baseline;gap:1rem;'>"
        f"<h2 style='margin:0;'>📊 财务概览</h2>"
        f"<span style='color:#888;font-size:0.75em;'>{subtitle}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if not data.get('latest_period'):
        st.info('暂无数据')
        return

    periods = data.get('periods', [])

    if stock_code and periods:
        try:
            dsm = get_data_source_manager()
            period_label = get_period_display_name(filters.get('period', ''))
            st.markdown(
                f"<span style='color:#888;font-size:0.8em;'>"
                f"分析期间：{min(periods)}–{max(periods)}　"
                f"数据周期：{period_label}　"
                f"数据来源：{dsm.active_source_name}"
                f"</span>",
                unsafe_allow_html=True,
            )
        except Exception as e:
            print(f"显示股票信息时出错: {e}")

    # ── 从 raw_data 直接取最新一期同比（接口返回的 [value, yoy]）──
    raw_data = data.get('_raw_data', {})
    periods = data.get('periods', [])
    rev_yoy = None
    profit_yoy = None
    if raw_data and periods:
        latest_p = periods[-1]
        inc = raw_data.get(latest_p, {}).get('income_statement', {})
        rev_entry = inc.get('营业收入', [0]) or inc.get('营业总收入', [0])
        profit_entry = inc.get('归母净利润', [0])
        if len(rev_entry) >= 2:
            rev_yoy = rev_entry[1]
        if len(profit_entry) >= 2:
            profit_yoy = profit_entry[1]

    # 显示关键指标（传入接口同比）
    latest_metrics = data['latest_period']['key_metrics']
    # 覆盖为接口返回的同比
    if rev_yoy is not None:
        latest_metrics['revenue_growth'] = rev_yoy * 100 if abs(rev_yoy) < 1 else rev_yoy
    if profit_yoy is not None:
        latest_metrics['profit_growth'] = profit_yoy * 100 if abs(profit_yoy) < 1 else profit_yoy

    latest_year = data['latest_period'].get('period', '')
    period_label = get_period_display_name(filters.get('period', ''))
    dashboard.display_key_metrics(latest_metrics, latest_year, period_label)

    # ── 图表（标题含周期标签）──
    chart_period_label = period_label  # 如 "年度"/"半年度"/"三季度"/"一季度"
    col1, col2 = st.columns(2)

    with col1:
        if 'revenue_chart' in data['charts']:
            dashboard.display_chart_with_export(
                data['charts']['revenue_chart'],
                f'营业收入趋势-{chart_period_label}',
                filters['export_format']
            )

    with col2:
        if 'profit_chart' in data['charts']:
            dashboard.display_chart_with_export(
                data['charts']['profit_chart'],
                f'归母净利润-{chart_period_label}',
                filters['export_format']
            )

    # ── 盈利能力（原"智能分析洞察"改名，表格展示）──
    if 'insights' in data:
        display_profitability_table(data, raw_data, periods)

def _get_raw_val_yoy(raw_data, period, table, field, fallback=None):
    """从 raw_data 取 [value, yoy]，返回 (value, yoy)。
    value 为 None 表示字段不存在（区别于 value=0 的有效零值）。
    当指定 fallback 且主字段为 None 时，尝试 fallback 字段。
    """
    entry = raw_data.get(period, {}).get(table, {}).get(field, None)
    # 主字段不存在时，尝试 fallback（仅在 entry 为 None 时，不把 [0] 当空）
    if entry is None and fallback:
        entry = raw_data.get(period, {}).get(table, {}).get(fallback, None)
    if isinstance(entry, (list, tuple)) and len(entry) >= 2:
        return entry[0], entry[1]
    elif isinstance(entry, (list, tuple)) and len(entry) == 1:
        return entry[0], None
    elif entry is None:
        return None, None
    else:
        return entry, None


def display_profitability_table(data: Dict, raw_data: Dict, periods: List[str]):
    """盈利能力 — 表格展示，同比用红绿色，数字和同比在同一单元格"""
    st.subheader('💰 盈利能力')

    if not raw_data or not periods:
        st.info('暂无数据')
        return

    rev_periods = list(reversed(periods))

    def fmt_yoy(yoy):
        if yoy is None:
            return ""
        pct = yoy * 100 if abs(yoy) < 1 else yoy
        sign = "+" if pct >= 0 else ""
        color = "#43a047" if pct >= 0 else "#e53935"
        return f"<br><span style='color:{color};font-size:0.78em;'>{sign}{pct:.1f}%</span>"

    def fmt_val(v):
        if v is None or v == 0:
            return "—"
        return f"{v/1e8:.2f}亿"

    def pct_val(v):
        if v is None or v == 0:
            return "—"
        return f"{v:.1%}"

    # 预计算各期毛利率/净利率
    gm_by_period = {}
    nm_by_period = {}
    for p in periods:
        rev, _ = _get_raw_val_yoy(raw_data, p, 'income_statement', '营业收入', '营业总收入')
        cost, _ = _get_raw_val_yoy(raw_data, p, 'income_statement', '营业成本')
        profit, _ = _get_raw_val_yoy(raw_data, p, 'income_statement', '归母净利润')
        gm_by_period[p] = (rev - cost) / rev if rev else None
        nm_by_period[p] = profit / rev if rev else None

    # 表格行定义：(标签, 类型, table, field1, field2)
    # 类型: 'val'=金额带同比, 'pct'=百分比带同比差
    rows_def = [
        ('营业收入(亿)', 'val', 'income_statement', '营业收入', '营业总收入'),
        ('归母净利润(亿)', 'val', 'income_statement', '归母净利润', None),
        ('毛利率', 'pct_calc', None, None, None),
        ('净利率', 'pct_calc', None, None, None),
        ('营业成本(亿)', 'val', 'income_statement', '营业成本', None),
        ('销售费用(亿)', 'val', 'income_statement', '销售费用', None),
        ('管理费用(亿)', 'val', 'income_statement', '管理费用', None),
        ('研发费用(亿)', 'val', 'income_statement', '研发费用', None),
        ('财务费用(亿)', 'val', 'income_statement', '财务费用', None),
        ('经营现金流(亿)', 'val', 'cash_flow', '经营活动产生的现金流量净额', '经营活动现金流净额'),
    ]

    # 构建表头
    col_headers = ['<th style="text-align:left;padding:6px 8px;color:#666;font-size:0.8em;">科目</th>']
    for p in rev_periods:
        col_headers.append(f'<th style="text-align:right;padding:6px 8px;color:#666;font-size:0.8em;">{p}</th>')

    # 构建数据行
    data_rows = []
    for label, rtype, table, field, fallback in rows_def:
        cells = [f'<td style="padding:5px 8px;font-weight:600;font-size:0.85em;">{label}</td>']
        for p in rev_periods:
            if rtype == 'pct_calc' and label == '毛利率':
                val = gm_by_period.get(p)
                cells.append(f'<td style="text-align:right;padding:5px 8px;font-size:0.85em;">{pct_val(val)}{fmt_yoy(None)}</td>')
            elif rtype == 'pct_calc' and label == '净利率':
                val = nm_by_period.get(p)
                cells.append(f'<td style="text-align:right;padding:5px 8px;font-size:0.85em;">{pct_val(val)}{fmt_yoy(None)}</td>')
            else:
                val, yoy = _get_raw_val_yoy(raw_data, p, table, field, fallback)
                cells.append(f'<td style="text-align:right;padding:5px 8px;font-size:0.85em;">{fmt_val(val)}{fmt_yoy(yoy)}</td>')
        data_rows.append(
            f'<tr style="border-bottom:1px solid #f0f0f0;">' + ''.join(cells) + '</tr>'
        )

    table_html = (
        '<table style="width:100%;border-collapse:collapse;margin-top:4px;">'
        '<thead><tr style="background:#fafafa;border-bottom:2px solid #e0e0e0;">'
        + ''.join(col_headers) + '</tr></thead>'
        '<tbody>' + ''.join(data_rows) + '</tbody></table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


def display_trend_analysis(dashboard: DashboardLayout, data: Dict, filters: Dict):
    """显示趋势分析（图表缓存版）"""
    stock_code = filters.get('stock_code', '') or st.session_state.get('last_analyzed_stock', '')
    subtitle = _stock_inline_subtitle(stock_code)
    st.markdown(
        f"<div style='display:flex;align-items:baseline;gap:1rem;'>"
        f"<h2 style='margin:0;'>📈 趋势分析</h2>"
        f"<span style='color:#888;font-size:0.75em;'>{subtitle}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if len(data.get('periods', [])) < 2:
        st.info('趋势分析需要至少2个周期的数据')
        return

    periods = data.get('periods', [])
    raw_data = data.get('_raw_data', {})
    period_label = get_period_display_name(filters.get('period', ''))
    chart_gen = ChartGenerator()

    # 图表缓存：数据未变化时复用已有图表 JSON，跳过重新创建
    _data_key = st.session_state.get('_chart_data_key', '')
    _cached_key = '_trend_charts_json'
    _fmt = filters.get('export_format', 'PNG')
    if st.session_state.get('_trend_data_key') == _data_key and _cached_key in st.session_state:
        import json as _json
        for _item in st.session_state[_cached_key]:
            dashboard.display_chart_with_export(
                go.Figure(_json.loads(_item['json'])), _item['name'], _item.get('fmt', _fmt))
        return

    _charts_to_cache = []
    if raw_data and len(periods) >= 2:
        # ── 增长率图：直接使用接口返回的同比数据 ──
        rev_yoys = []
        profit_yoys = []
        chart_periods = []
        for p in periods:
            _, rev_yoy = _get_raw_val_yoy(raw_data, p, 'income_statement', '营业收入', '营业总收入')
            _, profit_yoy = _get_raw_val_yoy(raw_data, p, 'income_statement', '归母净利润')
            if rev_yoy is not None:
                rev_yoys.append(rev_yoy * 100 if abs(rev_yoy) < 1 else rev_yoy)
            else:
                rev_yoys.append(0)
            if profit_yoy is not None:
                profit_yoys.append(profit_yoy * 100 if abs(profit_yoy) < 1 else profit_yoy)
            else:
                profit_yoys.append(0)
            chart_periods.append(p)

        growth_data = {
            '周期': chart_periods,
            '营收同比(%)': rev_yoys,
            '归母净利润同比(%)': profit_yoys,
        }
        growth_chart = chart_gen.create_combined_chart(
            growth_data, '营收同比(%)', '归母净利润同比(%)',
            f'营收与归母净利润同比趋势 ({period_label})',
            is_growth_rate=True, bg_preset=0
        )
        growth_chart.update_traces(
            selector=dict(name='营收同比(%)'),
            texttemplate='%{y:.1f}%', textposition='top center',
            textfont=dict(size=10, color='#e53935'),
        )
        growth_chart.update_traces(
            selector=dict(name='归母净利润同比(%)'),
            texttemplate='%{y:.1f}%', textposition='bottom center',
            textfont=dict(size=10, color='#f0a500'),
        )
        growth_chart.update_layout(
            legend=dict(
                orientation='v', yanchor='top', y=0.98,
                xanchor='right', x=0.98, font=dict(size=10),
                bgcolor='rgba(255,255,255,0.75)', bordercolor='#ddd', borderwidth=1,
            ),
            annotations=[dict(
                text='📌 营收同比 & 归母净利润同比',
                xref='paper', yref='paper', x=0.01, y=-0.12,
                showarrow=False, font=dict(size=10, color='#888'),
                xanchor='left', yanchor='top',
            )],
            margin=dict(l=60, r=30, t=50, b=55),
        )
        dashboard.display_chart_with_export(
            growth_chart,
            '增长率',
            filters['export_format']
        )

        # ── 营业成本与四费占比 ──
        cost_ratios = []
        four_fee_ratios = []
        fee_periods = []
        for p in periods:
            rev, _ = _get_raw_val_yoy(raw_data, p, 'income_statement', '营业收入', '营业总收入')
            if not rev:
                continue
            cost, _ = _get_raw_val_yoy(raw_data, p, 'income_statement', '营业成本')
            sales_fee, _ = _get_raw_val_yoy(raw_data, p, 'income_statement', '销售费用')
            mgmt_fee, _ = _get_raw_val_yoy(raw_data, p, 'income_statement', '管理费用')
            rd_fee, _ = _get_raw_val_yoy(raw_data, p, 'income_statement', '研发费用')
            fin_fee, _ = _get_raw_val_yoy(raw_data, p, 'income_statement', '财务费用')
            cost_ratios.append(cost / rev * 100)
            four_fee_ratios.append((sales_fee + mgmt_fee + rd_fee + fin_fee) / rev * 100)
            fee_periods.append(p)

        if fee_periods:
            fee_data = {
                '周期': fee_periods,
                '营业成本占营收(%)': [round(v, 1) for v in cost_ratios],
                '四费占营收(%)': [round(v, 1) for v in four_fee_ratios],
            }
            fee_chart = chart_gen.create_combined_chart(
                fee_data, '营业成本占营收(%)', '四费占营收(%)',
                f'营业成本与四费占营收比例 ({period_label})',
                is_growth_rate=True, bg_preset=1
            )
            # 主线标签上移，次线标签下移，避免交汇点重叠
            fee_chart.update_traces(
                selector=dict(name='营业成本占营收(%)'),
                texttemplate='%{y:.1f}%', textposition='top center',
                textfont=dict(size=10, color='#e53935'),
            )
            fee_chart.update_traces(
                selector=dict(name='四费占营收(%)'),
                texttemplate='%{y:.1f}%', textposition='bottom center',
                textfont=dict(size=10, color='#f0a500'),
            )
            fee_chart.update_layout(
                legend=dict(
                    orientation='v', yanchor='top', y=0.98,
                    xanchor='right', x=0.98, font=dict(size=10),
                    bgcolor='rgba(255,255,255,0.75)', bordercolor='#ddd', borderwidth=1,
                ),
                annotations=[dict(
                    text='📌 四费 = 销售 + 管理 + 研发 + 财务',
                    xref='paper', yref='paper', x=0.01, y=-0.12,
                    showarrow=False, font=dict(size=10, color='#888'),
                    xanchor='left', yanchor='top',
                )],
                margin=dict(l=60, r=30, t=50, b=55),
            )
            dashboard.display_chart_with_export(
                fee_chart,
                '成本费用占比',
                filters['export_format']
            )

        # ── 应收占比和负债率 ──
        ar_ratios = []
        debt_ratios = []
        ar_periods = []
        for p in periods:
            total_assets, _ = _get_raw_val_yoy(raw_data, p, 'balance_sheet', '资产总计', '总资产')
            if not total_assets:
                continue
            bills_ar, _ = _get_raw_val_yoy(raw_data, p, 'balance_sheet', '应收票据')
            acct_ar, _ = _get_raw_val_yoy(raw_data, p, 'balance_sheet', '应收账款')
            prepay, _ = _get_raw_val_yoy(raw_data, p, 'balance_sheet', '预付款项')
            other_ar, _ = _get_raw_val_yoy(raw_data, p, 'balance_sheet', '其他应收款')
            lt_ar, _ = _get_raw_val_yoy(raw_data, p, 'balance_sheet', '长期应收款')
            total_ar = bills_ar + acct_ar + prepay + other_ar + lt_ar
            total_liab, _ = _get_raw_val_yoy(raw_data, p, 'balance_sheet', '负债合计')
            ar_ratios.append(total_ar / total_assets * 100)
            debt_ratios.append(total_liab / total_assets * 100)
            ar_periods.append(p)

        if ar_periods:
            ar_data = {
                '周期': ar_periods,
                '应收类占总资产(%)': [round(v, 1) for v in ar_ratios],
                '资产负债率(%)': [round(v, 1) for v in debt_ratios],
            }
            ar_chart = chart_gen.create_combined_chart(
                ar_data, '应收类占总资产(%)', '资产负债率(%)',
                f'应收占比与资产负债率 ({period_label})',
                is_growth_rate=True, bg_preset=2
            )
            ar_chart.update_traces(
                selector=dict(name='应收类占总资产(%)'),
                texttemplate='%{y:.1f}%', textposition='top center',
                textfont=dict(size=10, color='#e53935'),
            )
            ar_chart.update_traces(
                selector=dict(name='资产负债率(%)'),
                texttemplate='%{y:.1f}%', textposition='bottom center',
                textfont=dict(size=10, color='#f0a500'),
            )
            ar_chart.update_layout(
                legend=dict(
                    orientation='v', yanchor='top', y=0.98,
                    xanchor='right', x=0.98, font=dict(size=10),
                    bgcolor='rgba(255,255,255,0.75)', bordercolor='#ddd', borderwidth=1,
                ),
                annotations=[dict(
                    text='📌 应收类 = 应收票据+应收账款+预付款项+其他应收款+长期应收款',
                    xref='paper', yref='paper', x=0.01, y=-0.12,
                    showarrow=False, font=dict(size=10, color='#888'),
                    xanchor='left', yanchor='top',
                )],
                margin=dict(l=60, r=30, t=50, b=55),
            )
            dashboard.display_chart_with_export(
                ar_chart,
                '应收与负债率',
                filters['export_format']
            )

        # ── 合同负债/预收款项趋势（白酒行业重要指标）──
        # 2019年后用"合同负债"，之前用"预收款项"（会计准则变更）
        # 策略：哪个字段有值就用哪个字段的同比（不交叉）；有值但同比为 None 时手动衔接
        _pre_fields = ['预收款项', '预收款项(别名)']
        contract_vals = []
        contract_yoys = []
        contract_periods = []
        has_contract = False

        # 收集每年的值和对应字段的同比，同时记录来源字段
        _entries = []  # [(val, yoy, src_field), ...]
        for p in periods:
            val, yoy, src = None, None, None
            # 先尝试合同负债
            val, yoy = _get_raw_val_yoy(raw_data, p, 'balance_sheet', '合同负债')
            if val is not None and val != 0:
                src = '合同负债'
            else:
                # 合同负债无值，尝试预收款项
                for _pf in _pre_fields:
                    val2, yoy2 = _get_raw_val_yoy(raw_data, p, 'balance_sheet', _pf)
                    if val2 is not None and val2 != 0:
                        val, yoy, src = val2, yoy2, _pf
                        break
            _entries.append((val, yoy, src))

        # 同比逻辑：API 返回了 yoy（非 None）直接用；yoy 为 None 时手动衔接
        for i, (val, yoy, src) in enumerate(_entries):
            contract_vals.append(val / 1e8 if val is not None else 0)
            contract_periods.append(periods[i])
            if val is not None:
                has_contract = True

            if val is None:
                contract_yoys.append(None)
            elif yoy is not None:
                # API 返回了同比（小数形式，如 -0.1653 表示 -16.53%），转为百分比
                contract_yoys.append(yoy * 100)
            else:
                # 有值但 API 没返回同比 → 手动衔接：只取上一期值，不往前追溯
                prev_val = _entries[i - 1][0] if i > 0 else None
                if prev_val is not None and prev_val != 0:
                    _yoy = (val - prev_val) / abs(prev_val)
                    contract_yoys.append(_yoy * 100)
                else:
                    contract_yoys.append(None)

        import sys as _sys
        for _dbg_p in periods:
            _dbg_bs = raw_data.get(_dbg_p, {}).get('balance_sheet', {})
            _dbg_cl = _dbg_bs.get('合同负债', 'N/A')
            _dbg_ys = _dbg_bs.get('预收款项', 'N/A')
            print(f"[DBG合同负债] {_dbg_p}: 合同负债={_dbg_cl}, 预收款项={_dbg_ys}", file=_sys.stderr)
        for _dbg_i, (_dbg_v, _dbg_y, _dbg_s) in enumerate(_entries):
            print(f"[DBG合同负债] {periods[_dbg_i]}: val={_dbg_v}, yoy={_dbg_y}, src={_dbg_s}", file=_sys.stderr)
        print(f"[DBG合同负债] contract_yoys={contract_yoys}", file=_sys.stderr)
        #         cl = bs.get('合同负债', 'N/A')
        #         yk = bs.get('预收款项', 'N/A')
        #         st.write(f"{p}: 合同负债={cl}, 预收款项={yk}")
        #     st.write(f"结果: {list(zip(contract_periods, contract_vals))}")

        if has_contract:
            # 柱状图（金额）+ 折线图（同比）双轴合一
            cl_combined_data = {
                '周期': contract_periods,
                '合同负债(亿)': [round(v, 2) for v in contract_vals],
                '同比(%)': [y if y is not None else 0 for y in contract_yoys],
            }
            print(f"[DBG图表] cl_combined_data={cl_combined_data}", file=_sys.stderr)
            cl_combined_chart = chart_gen.create_bar_line_chart(
                cl_combined_data,
                bar_column='合同负债(亿)',
                line_column='同比(%)',
                title=f'合同负债趋势与同比 ({period_label})',
                bar_name='合同负债(亿)',
                line_name='同比(%)',
                bg_preset=3,
            )
            cl_combined_chart.update_layout(
                legend=dict(
                    orientation='v', yanchor='top', y=0.98,
                    xanchor='right', x=0.98, font=dict(size=10),
                    bgcolor='rgba(255,255,255,0.75)', bordercolor='#ddd', borderwidth=1,
                ),
                annotations=[dict(
                    text='📌 2019年前为"预收款项"，2019年起为"合同负债"（会计准则变更）',
                    xref='paper', yref='paper', x=0.01, y=-0.12,
                    showarrow=False, font=dict(size=10, color='#888'),
                    xanchor='left', yanchor='top',
                )],
                margin=dict(l=60, r=30, t=50, b=55),
            )
            dashboard.display_chart_with_export(
                cl_combined_chart,
                '合同负债',
                filters['export_format']
            )
    # 趋势图表
    if 'trend_charts' in data:
        for chart_name, chart in data['trend_charts'].items():
            dashboard.display_chart_with_export(
                chart,
                chart_name,
                filters['export_format']
            )

    # 趋势分析结果
    if 'trend_analysis' in data and data['trend_analysis']:
        st.subheader('📊 趋势分析结果')

        trend_rows = []
        for metric_name, metrics in data['trend_analysis'].items():
            if isinstance(metrics, dict):
                row = {
                    '指标': metric_name,
                    '复合增长率': metrics.get('复合增长率', 0.0),
                    '年均增长': metrics.get('年均增长', 0.0),
                    '趋势方向': metrics.get('趋势方向', '未知')
                }
                trend_rows.append(row)

        if trend_rows:
            trend_df = pd.DataFrame(trend_rows)
            trend_df.set_index('指标', inplace=True)
            st.dataframe(trend_df.style.format({
                '复合增长率': '{:.2%}',
                '年均增长': '{:.2%}'
            }))

def _build_fv_table(raw_data, periods, table_key, field_order,
                    category_headers=None, highlight_fields=None):
    """通用：构建 字段×年份 的数值+同比 HTML 表格，年份倒序（最近在前）

    Args:
        category_headers: list of (field_before, category_label) tuples.
                          在 field_before 之前插入分类标题行 + 空白分隔行。
                          例如 [("货币资金", "流动资产"), ...] 表示在货币资金前插入"流动资产"标题行和空行。
        highlight_fields: set of field names to highlight (合计/总计行用特殊样式)
    """
    import pandas as pd
    rev_periods = list(reversed(periods))  # 倒序：最近年份在前
    category_headers = category_headers or []
    highlight_fields = highlight_fields or set()

    def gv(period, field):
        v = raw_data.get(period, {}).get(table_key, {}).get(field, [0, 0])
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return v[0], v[1]
        elif isinstance(v, (list, tuple)) and len(v) == 1:
            return v[0], 0.0
        return v, 0.0

    def fmt_yoy(yoy):
        if yoy is None or yoy == 0:
            return "—"
        pct = yoy * 100 if abs(yoy) < 1 else yoy
        return f"{pct:+.1f}%"

    def fmt_val(v):
        if v is None:
            return "—"
        return f"{v/1e8:.2f}"

    # 按预定义顺序过滤存在的字段，再追加未预见字段
    latest_data = raw_data.get(periods[-1], {}).get(table_key, {})
    ordered = [f for f in field_order if f in latest_data]
    for f in latest_data:
        if f not in ordered:
            ordered.append(f)

    # ── 构建行列表（含分类标题行和空白行）──
    # category_headers: list of (insert_before_field, label)
    # 转换为 dict 方便查找
    cat_map = {field: label for field, label in category_headers}

    rows = []
    for field in ordered:
        # 在该字段前插入分类标题行（如果需要）
        if field in cat_map:
            rows.append({'__type__': 'category', 'label': cat_map[field]})
            rows.append({'__type__': 'blank'})
        rows.append({'__type__': 'data', 'field': field})

    # ── 生成 HTML ──
    n_year_cols = len(rev_periods) * 2  # 每年：数值 + 同比
    # 表头
    year_header_cells = ''.join(
        f'<th colspan="2" style="text-align:center;border-bottom:2px solid #555;padding:4px 8px;white-space:nowrap;">{p}</th>'
        for p in rev_periods
    )
    sub_header_cells = ''.join(
        f'<th style="text-align:center;padding:3px 6px;font-size:0.8em;color:#888;white-space:nowrap;">数值(亿)</th>'
        f'<th style="text-align:center;padding:3px 6px;font-size:0.8em;color:#888;white-space:nowrap;">同比</th>'
        for _ in rev_periods
    )

    # 分类标题背景色（交替）— light / dark 两套
    cat_colors_light = ['#e8f4fd', '#e8f8f0', '#fdf6e8', '#f8e8f8', '#f0e8fd', '#fde8e8', '#e8fde8', '#e8f0fd']
    cat_colors_dark  = ['#1a2a3a', '#1a2e1a', '#2e2a1a', '#2a1a2e', '#221a3a', '#2e1a1a', '#1a2e1a', '#1a1e3a']

    data_rows_html = ''
    cat_idx = 0
    for row in rows:
        if row['__type__'] == 'category':
            cl = cat_colors_light[cat_idx % len(cat_colors_light)]
            cd = cat_colors_dark[cat_idx % len(cat_colors_dark)]
            cat_idx += 1
            data_rows_html += (
                f'<tr class="fv-cat fv-cat-{cat_idx}" style="background-color:{cl};">'
                f'<td colspan="{1 + n_year_cols}" style="padding:5px 8px;font-weight:700;font-size:0.95em;color:var(--fv-cat-text);border-top:1px solid var(--fv-cat-border);">'
                f'📁 {row["label"]}</td></tr>'
            )
        elif row['__type__'] == 'blank':
            data_rows_html += (
                '<tr style="background:var(--fv-blank-bg);">'
                f'<td colspan="{1 + n_year_cols}" style="height:4px;padding:0;border:none;"></td></tr>'
            )
        else:
            field = row['field']
            is_highlight = field in highlight_fields
            field_style = (
                f'padding:3px 8px;font-weight:700;font-size:0.88em;color:var(--fv-hl-text);border-top:1px solid var(--fv-hl-border);'
                if is_highlight else
                'padding:3px 8px;font-size:0.85em;white-space:nowrap;'
            )
            indent = '' if is_highlight else '&nbsp;&nbsp;&nbsp;&nbsp;'
            field_label = f'{indent}{field}' if not is_highlight else f'<strong>{field}</strong>'

            cells = ''
            for period in rev_periods:
                val, yoy = gv(period, field)
                val_str = fmt_val(val)
                yoy_str = fmt_yoy(yoy)
                if yoy is not None and yoy > 0:
                    yoy_color = 'var(--fv-yoy-pos)'
                elif yoy is not None and yoy < 0:
                    yoy_color = 'var(--fv-yoy-neg)'
                else:
                    yoy_color = 'var(--fv-yoy-neu)'
                cells += (
                    f'<td style="text-align:right;padding:3px 6px;white-space:nowrap;">{val_str}</td>'
                    f'<td style="text-align:right;padding:3px 6px;color:{yoy_color};white-space:nowrap;">{yoy_str}</td>'
                )
            bg_style = 'background-color:var(--fv-hl-bg);' if is_highlight else ''
            data_rows_html += (
                f'<tr style="{bg_style}border-bottom:1px solid var(--fv-row-border);">'
                f'<td style="{field_style}">{field_label}</td>{cells}</tr>'
            )

    # 子表头颜色用 CSS 变量
    sub_header_cells_css = ''.join(
        f'<th style="text-align:center;padding:3px 6px;font-size:0.8em;color:var(--fv-subheader-text);white-space:nowrap;">数值(亿)</th>'
        f'<th style="text-align:center;padding:3px 6px;font-size:0.8em;color:var(--fv-subheader-text);white-space:nowrap;">同比</th>'
        for _ in rev_periods
    )

    # 构建分类行 dark 模式 CSS
    cat_dark_rules = ''
    for i in range(1, cat_idx + 1):
        ci = (i - 1) % len(cat_colors_dark)
        cat_dark_rules += f'  html[data-theme="dark"] .fv-cat-{i} {{ background-color: {cat_colors_dark[ci]} !important; }}\n'

    html = (
        '<div style="overflow-x:auto;max-height:70vh;">'
        '<style>'
        + cat_dark_rules +
        '</style>'
        '<table style="border-collapse:collapse;width:100%;font-family:sans-serif;">'
        '<thead>'
        f'<tr><th style="text-align:left;padding:4px 8px;min-width:180px;border-bottom:2px solid var(--fv-header-border);">科目</th>{year_header_cells}</tr>'
        f'<tr><th style="text-align:left;padding:3px 8px;border-bottom:1px solid var(--fv-subheader-border);"></th>{sub_header_cells_css}</tr>'
        '</thead>'
        f'<tbody>{data_rows_html}</tbody>'
        '</table></div>'
    )
    return html


def display_period_analysis(dashboard: DashboardLayout, data: Dict, filters: Dict):
    """财务数据 — Tab切换：关键指标 / 利润表 / 资产负债表 / 现金流量表"""
    import pandas as pd

    period_label = get_period_display_name(filters.get('period', ''))

    # ── 标题 + 副标题同行（副标题在右侧小字）──
    stock_code = filters.get('stock_code', '') or st.session_state.get('last_analyzed_stock', '')
    subtitle = _stock_inline_subtitle(stock_code)
    st.markdown(
        f"<div style='display:flex;align-items:baseline;gap:1rem;'>"
        f"<h2 style='margin:0;'>📊 财务数据 ({period_label})</h2>"
        f"<span style='color:#888;font-size:0.75em;'>{subtitle}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    raw_data = data.get('_raw_data', {})
    periods = sorted(data.get('periods', []))  # 正序，用于计算

    if not raw_data or not periods:
        st.info('暂无数据')
        return

    # ── 工具函数（KPI tab 用）──
    def gv_raw(period, table, field):
        v = raw_data.get(period, {}).get(table, {}).get(field, [0, 0])
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return v[0], v[1]
        elif isinstance(v, (list, tuple)) and len(v) == 1:
            return v[0], 0.0
        return v, 0.0

    def fmt_yoy(yoy):
        if yoy is None or yoy == 0:
            return "—"
        pct = yoy * 100 if abs(yoy) < 1 else yoy
        return f"{pct:+.1f}%"

    def fmt_val(v):
        if v is None:
            return "—"
        return f"{v/1e8:.2f}"

    rev_periods = list(reversed(periods))  # 倒序

    # ── Tab 切换 ──
    tab_kpi, tab_inc, tab_bal, tab_cf = st.tabs([
        "🔑 关键指标", "📋 利润表", "🏦 资产负债表", "💧 现金流量表"
    ])

    # ════════════════════════════════════════
    # Tab 1: 关键指标摘要表（年份倒序）
    # ════════════════════════════════════════
    with tab_kpi:
        st.markdown(f"**最新：{periods[-1]}** · 同比变化")

        rows = []
        for period in rev_periods:
            rev, rev_yoy = gv_raw(period, 'income_statement', '营业收入')
            if not rev:
                rev, rev_yoy = gv_raw(period, 'income_statement', '营业总收入')
            profit, profit_yoy = gv_raw(period, 'income_statement', '归母净利润')
            total_assets, _ = gv_raw(period, 'balance_sheet', '资产总计')
            total_liab, _ = gv_raw(period, 'balance_sheet', '负债合计')
            equity, _ = gv_raw(period, 'balance_sheet', '所有者权益合计')
            ocf, ocf_yoy = gv_raw(period, 'cash_flow', '经营活动产生的现金流量净额')

            debt_ratio = (total_liab / total_assets * 100) if total_assets else 0
            profit_margin = (profit / rev * 100) if rev else 0
            roe = (profit / equity * 100) if equity else 0

            rows.append({
                '指标': period,
                '营业收入(亿)': fmt_val(rev),
                '营收同比': fmt_yoy(rev_yoy),
                '归母净利润(亿)': fmt_val(profit),
                '净利同比': fmt_yoy(profit_yoy),
                '净利润率': f"{profit_margin:.1f}%",
                'ROE': f"{roe:.1f}%",
                '资产负债率': f"{debt_ratio:.1f}%",
                '经营现金流(亿)': fmt_val(ocf),
                'OCF同比': fmt_yoy(ocf_yoy),
            })

        df = pd.DataFrame(rows).set_index('指标')
        st.dataframe(df, width='stretch', height=min(300, 35 * len(df) + 37))

    # ════════════════════════════════════════
    # Tab 2: 利润表（全量字段，年份倒序）
    # ════════════════════════════════════════
    with tab_inc:
        st.markdown("**利润表** · 单位：亿元")

        _inc_order = [
            # ── 营业收入 ──
            "营业总收入", "营业收入",
            # ── 营业成本与费用 ──
            "营业总成本", "营业成本", "税金及附加",
            "销售费用", "管理费用", "研发费用", "财务费用",
            "利息支出", "利息收入",
            # ── 其他损益 ──
            "其他收益", "投资收益", "对联营企业和合营企业的投资收益",
            "公允价值变动收益", "资产减值损失", "信用减值损失",
            "资产处置收益", "汇兑收益",
            # ── 利润 ──
            "营业利润",
            "营业外收入", "营业外支出",
            "利润总额", "所得税费用",
            "净利润", "归母净利润", "扣非归母净利润",
            "持续经营净利润", "少数股东损益",
            # ── 综合收益 ──
            "综合收益总额",
            "归属于母公司股东的综合收益总额", "归属于少数股东的综合收益总额",
            "其他综合收益",
            "归属于母公司股东的其他综合收益", "归属于少数股东的其他综合收益",
            # ── 每股收益 ──
            "基本每股收益", "稀释每股收益",
        ]
        _inc_cats = [
            ("营业总收入", "营业收入"),
            ("营业总成本", "营业成本与费用"),
            ("其他收益", "其他损益"),
            ("营业利润", "利润"),
            ("综合收益总额", "综合收益"),
            ("基本每股收益", "每股收益"),
        ]
        _inc_highlight = {"营业总收入", "营业利润", "利润总额", "净利润", "归母净利润", "扣非归母净利润", "综合收益总额"}
        html = _build_fv_table(raw_data, periods, 'income_statement', _inc_order,
                               category_headers=_inc_cats, highlight_fields=_inc_highlight)
        st.markdown(html, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # Tab 3: 资产负债表（全量字段，年份倒序）
    # ════════════════════════════════════════
    with tab_bal:
        st.markdown("**资产负债表** · 单位：亿元")

        _bal_order = [
            # ════════════ 资产 ════════════
            # ── 流动资产 ──
            "货币资金", "交易性金融资产",
            "应收票据", "应收账款", "应收票据及应收账款",
            "应收利息", "应收股利", "预付款项", "其他应收款",
            "存货", "合同资产", "一年内到期的非流动资产", "其他流动资产",
            "流动资产合计",
            # ── 非流动资产 ──
            "可供出售金融资产", "持有至到期投资", "其他非流动金融资产",
            "长期应收款", "长期股权投资", "投资性房地产",
            "固定资产", "固定资产合计", "固定资产清理",
            "在建工程", "在建工程合计", "生产性生物资产", "油气资产",
            "无形资产", "开发支出", "商誉",
            "长期待摊费用", "递延所得税资产", "其他非流动资产",
            "非流动资产合计",
            # ── 资产总计 ──
            "资产总计",
            # ════════════ 负债 ════════════
            # ── 流动负债 ──
            "短期借款", "交易性金融负债",
            "应付票据", "应付账款", "应付票据及应付账款",
            "预收款项", "合同负债", "应付职工薪酬",
            "应交税费", "应付利息", "应付股利", "其他应付款",
            "一年内到期的非流动负债", "其他流动负债",
            "流动负债合计",
            # ── 非流动负债 ──
            "长期借款", "应付债券", "永续债",
            "长期应付款", "长期应付款合计",
            "预计负债", "递延所得税负债", "其他非流动负债",
            "非流动负债合计",
            # ── 负债总计 ──
            "负债合计",
            # ════════════ 所有者权益 ════════════
            "实收资本(股本)", "资本公积", "库存股",
            "其他综合收益", "专项储备", "盈余公积", "未分配利润",
            "归属于母公司股东的权益合计", "少数股东权益",
            "所有者权益合计",
            # ── 总计 ──
            "负债和所有者权益总计",
            "资产负债率",
        ]
        _bal_cats = [
            ("货币资金", "流动资产"),
            ("可供出售金融资产", "非流动资产"),
            ("短期借款", "流动负债"),
            ("长期借款", "非流动负债"),
            ("实收资本(股本)", "所有者权益"),
        ]
        _bal_highlight = {
            "流动资产合计", "非流动资产合计", "资产总计",
            "流动负债合计", "非流动负债合计", "负债合计",
            "所有者权益合计", "负债和所有者权益总计",
        }
        html = _build_fv_table(raw_data, periods, 'balance_sheet', _bal_order,
                               category_headers=_bal_cats, highlight_fields=_bal_highlight)
        st.markdown(html, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # Tab 4: 现金流量表（全量字段，年份倒序）
    # ════════════════════════════════════════
    with tab_cf:
        st.markdown("**现金流量表** · 单位：亿元")

        _cf_order = [
            # ════════════ 经营活动 ════════════
            "销售商品、提供劳务收到的现金", "收到的税费返还",
            "收到其他与经营活动有关的现金", "经营活动现金流入小计",
            "购买商品、接受劳务支付的现金", "支付给职工以及为职工支付的现金",
            "支付的各项税费", "支付其他与经营活动有关的现金",
            "经营活动现金流出小计",
            "经营活动产生的现金流量净额",
            # ════════════ 投资活动 ════════════
            "处置固定资产、无形资产和其他长期资产收回的现金净额",
            "处置子公司及其他营业单位收到的现金净额",
            "取得投资收益收到的现金", "收到其他与投资活动有关的现金",
            "投资活动现金流入小计",
            "购建固定资产、无形资产和其他长期资产支付的现金",
            "投资支付的现金", "支付其他与投资活动有关的现金",
            "投资活动现金流出小计",
            "投资活动产生的现金流量净额",
            # ════════════ 筹资活动 ════════════
            "吸收投资收到的现金", "取得借款收到的现金", "发行债券收到的现金",
            "收到其他与筹资活动有关的现金", "筹资活动现金流入小计",
            "偿还债务支付的现金", "分配股利、利润或偿付利息支付的现金",
            "向少数股东支付股利", "支付其他与筹资活动有关的现金",
            "筹资活动现金流出小计",
            "筹资活动产生的现金流量净额",
            # ════════════ 现金净增加 ════════════
            "汇率变动对现金及现金等价物的影响",
            "现金及现金等价物净增加额",
            "期初现金及现金等价物余额", "期末现金及现金等价物余额",
        ]
        _cf_cats = [
            ("销售商品、提供劳务收到的现金", "经营活动"),
            ("处置固定资产、无形资产和其他长期资产收回的现金净额", "投资活动"),
            ("吸收投资收到的现金", "筹资活动"),
            ("汇率变动对现金及现金等价物的影响", "现金净增加"),
        ]
        _cf_highlight = {
            "经营活动现金流入小计", "经营活动现金流出小计", "经营活动产生的现金流量净额",
            "投资活动现金流入小计", "投资活动现金流出小计", "投资活动产生的现金流量净额",
            "筹资活动现金流入小计", "筹资活动现金流出小计", "筹资活动产生的现金流量净额",
            "现金及现金等价物净增加额",
        }
        html = _build_fv_table(raw_data, periods, 'cash_flow', _cf_order,
                               category_headers=_cf_cats, highlight_fields=_cf_highlight)
        st.markdown(html, unsafe_allow_html=True)

    # ── 期间趋势图 ──
    if 'period_chart' in data.get('charts', {}):
        st.markdown("---")
        st.markdown(f"**📈 {period_label}趋势**")
        dashboard.display_chart_with_export(
            data['charts']['period_chart'],
            f'{period_label}趋势',
            filters['export_format']
        )

    # ── 周期性分析 ──
    if data.get('period_patterns'):
        st.markdown("---")
        patterns = data.get('period_patterns')
        st.markdown("**🎯 周期性模式分析**")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("最强周期", patterns.get('最强周期', 'N/A'))
        with c2:
            st.metric("最弱周期", patterns.get('最弱周期', 'N/A'))
        with c3:
            st.metric("周期波动性", f"{patterns.get('周期波动性', 0):.2%}")

def display_comprehensive_report(dashboard: DashboardLayout, data: Dict, filters: Dict):
    """显示综合报告（丰富版）"""
    stock_code = filters.get('stock_code', '') or st.session_state.get('last_analyzed_stock', '')
    subtitle = _stock_inline_subtitle(stock_code)
    st.markdown(
        f"<div style='display:flex;align-items:baseline;gap:1rem;'>"
        f"<h2 style='margin:0;'>📋 综合分析报告</h2>"
        f"<span style='color:#888;font-size:0.75em;'>{subtitle}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    raw_data = data.get('_raw_data', {})
    periods = sorted(data.get('periods', []))

    # ── 年份选择器（弹簧式横向展开） ──
    period_label = get_period_display_name(filters.get('period', ''))
    if len(periods) > 1:
        rev_periods = list(reversed(periods))  # 倒序：最新在前

        # 初始化 session state
        if 'cr_sel_period' not in st.session_state or st.session_state.cr_sel_period not in rev_periods:
            st.session_state.cr_sel_period = rev_periods[0]
        if '_cr_expanded' not in st.session_state:
            st.session_state['_cr_expanded'] = False

        _cur = st.session_state.cr_sel_period
        _expanded = st.session_state['_cr_expanded']

        if _expanded:
            # 展开态：所有年份按钮 + 收缩按钮，横向排列
            _items = list(rev_periods) + ['__collapse__']
            _cols = st.columns(len(_items))
            for _i, _p in enumerate(_items):
                with _cols[_i]:
                    if _p == '__collapse__':
                        if st.button('◀ 收起', key='_cr_collapse', use_container_width=True):
                            st.session_state['_cr_expanded'] = False
                    else:
                        _is_cur = (_p == _cur)
                        _label = f"{'● ' if _is_cur else ''}{_p}{period_label if _is_cur else ''}"
                        if st.button(_label, key=f'_cr_year_{_p}',
                                     type='primary' if _is_cur else 'secondary',
                                     use_container_width=True):
                            st.session_state.cr_sel_period = _p
                            st.session_state['_cr_expanded'] = False
        else:
            # 折叠态：仅一个按钮，包含年份+箭头，点击即展开
            if st.button(
                f"📅 {_cur}{period_label}  ▶",
                key='_cr_expand',
                use_container_width=False,
            ):
                st.session_state['_cr_expanded'] = True

        sel_period = st.session_state.cr_sel_period
    elif len(periods) == 1:
        sel_period = periods[0]
    else:
        st.info('暂无数据')
        return

    # 数据缓存 key（用于杜邦/波特五力等缓存标识）
    _data_key = f"{filters.get('stock_code', '')}_{filters.get('start_year', '')}_{filters.get('end_year', '')}_{filters.get('period', '')}"

    # ════════════════════════════════════════
    # 一、执行摘要（丰富版）
    # ════════════════════════════════════════
    st.subheader('📄 执行摘要')
    if 'executive_summary' in data and data['executive_summary']:
        summary_lines = data['executive_summary']
        company_line = summary_lines[0] if len(summary_lines) > 0 else ''
        cashflow_line = summary_lines[1] if len(summary_lines) > 1 else ''
        ratio_line = summary_lines[2] if len(summary_lines) > 2 else ''
        trend_line = summary_lines[3] if len(summary_lines) > 3 else ''
        grade_line = summary_lines[4] if len(summary_lines) > 4 else ''

        # 解析 company_line → 行1=分析期间范围，行2=公司名 · 报告期
        _clean = company_line.replace('**', '').replace('🏢 ', '').replace('📊 ', '').strip()
        _parts = _clean.split(' · ')
        _company_part = _parts[0].strip() if _parts else ''
        _period_range = ''
        if len(_parts) >= 2:
            _period_raw = _parts[-1].strip()
            for _sep in ['分析期间：', '分析期间:']:
                if _sep in _period_raw:
                    _period_range = _period_raw.split(_sep)[-1].strip()
                    break

        _sel_period_full = f"{sel_period}{period_label}"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f8f9fa,#e8eaf6);border-radius:14px;
                    padding:18px 22px;margin:8px 0 4px;border-left:5px solid #1a237e;">
            <div style="font-size:0.82em;color:#888;margin-bottom:6px;">当前分析期间：{_period_range or '—'}</div>
            <div style="font-size:0.95em;color:#333;margin-bottom:12px;">{_company_part} · 报告期：<strong>{_sel_period_full}</strong></div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
                <div style="flex:1;min-width:200px;background:white;border-radius:8px;padding:10px 14px;
                            box-shadow:0 1px 3px rgba(0,0,0,0.08);">
                    <div style="font-size:0.72em;color:#888;margin-bottom:4px;">💵 经营规模</div>
                    <div style="font-size:0.88em;color:#333;">{cashflow_line}</div>
                </div>
                <div style="flex:1;min-width:200px;background:white;border-radius:8px;padding:10px 14px;
                            box-shadow:0 1px 3px rgba(0,0,0,0.08);">
                    <div style="font-size:0.72em;color:#888;margin-bottom:4px;">📊 盈利 & 财务质量</div>
                    <div style="font-size:0.88em;color:#333;">{ratio_line}</div>
                </div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
                <div style="flex:1;min-width:200px;background:white;border-radius:8px;padding:10px 14px;
                            box-shadow:0 1px 3px rgba(0,0,0,0.08);">
                    <div style="font-size:0.72em;color:#888;margin-bottom:4px;">📈 趋势判断</div>
                    <div style="font-size:0.88em;color:#333;">{trend_line}</div>
                </div>
                <div style="flex:1;min-width:200px;background:white;border-radius:8px;padding:10px 14px;
                            box-shadow:0 1px 3px rgba(0,0,0,0.08);">
                    <div style="font-size:0.72em;color:#888;margin-bottom:4px;">🏅 综合评级</div>
                    <div style="font-size:0.88em;color:#333;">{grade_line}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # 二、智能分析洞察（紧凑网格）
    # ════════════════════════════════════════
    st.subheader('🔍 详细分析')

    # 从 insights 各分类生成评分
    _insights = data.get('insights', {})
    _scores = {}
    for cat, texts in _insights.items():
        if not texts:
            _scores[cat] = 0
            continue
        # 根据文本内容推断评分
        text = ' '.join(texts)
        if any(k in text for k in ('优秀', '卓越', '强劲', '充足', '健康')):
            _scores[cat] = 3
        elif any(k in text for k in ('良好', '稳健', '适中', '合理')):
            _scores[cat] = 2
        elif any(k in text for k in ('关注', '不足', '风险', '偏低', '下滑')):
            _scores[cat] = 1
        else:
            _scores[cat] = 2

    dashboard.display_insights(_insights, scores=_scores)

    # ════════════════════════════════════════
    # 三、杜邦分析
    # ════════════════════════════════════════
    st.markdown("---")
    st.subheader(f'📐 杜邦分析 ({sel_period})')

    if raw_data:
        dupont = calculate_dupont_with_comparison(raw_data, period=sel_period)
        latest = dupont.get('latest', {})
        delta = dupont.get('delta', {})

        if latest:
            def _fmt_pct(v, d=None):
                if v is None:
                    return '—', ''
                s = f"{v:.1%}"
                if d is not None and abs(d) > 0.0001:
                    arrow = '↑' if d > 0 else '↓'
                    s += f" {arrow}{abs(d):.1%}"
                return s, 'color:#43a047' if (d or 0) >= 0 else 'color:#e53935'

            def _fmt_num(v, d=None):
                if v is None:
                    return '—', ''
                s = f"{v:.2f}"
                if d is not None and abs(d) > 0.001:
                    arrow = '↑' if d > 0 else '↓'
                    s += f" {arrow}{abs(d):.2f}"
                return s, 'color:#43a047' if (d or 0) >= 0 else 'color:#e53935'

            roe_s, roe_c = _fmt_pct(latest.get('roe'), delta.get('roe'))
            nm_s, nm_c = _fmt_pct(latest.get('net_margin'), delta.get('net_margin'))
            at_s, at_c = _fmt_num(latest.get('asset_turnover'), delta.get('asset_turnover'))
            em_s, em_c = _fmt_num(latest.get('equity_multiplier'), delta.get('equity_multiplier'))

            # 获取历史趋势数据用于 sparkline（缓存避免重复计算）
            _periods_all = sorted(raw_data.keys())
            _dupont_cache_key = f"_dupont_hist_{_data_key}"
            if st.session_state.get(_dupont_cache_key + '_key') == _data_key:
                _hist = st.session_state[_dupont_cache_key]
                _hist_roe, _hist_nm, _hist_at, _hist_em = _hist['roe'], _hist['nm'], _hist['at'], _hist['em']
            else:
                _hist_roe, _hist_nm, _hist_at, _hist_em = [], [], [], []
                for _p in _periods_all:
                    _d = calculate_dupont_with_comparison(raw_data, period=_p)
                    _l = _d.get('latest', {})
                    _hist_roe.append(_l.get('roe', 0) or 0)
                    _hist_nm.append(_l.get('net_margin', 0) or 0)
                    _hist_at.append(_l.get('asset_turnover', 0) or 0)
                    _hist_em.append(_l.get('equity_multiplier', 0) or 0)
                st.session_state[_dupont_cache_key] = {'roe': _hist_roe, 'nm': _hist_nm, 'at': _hist_at, 'em': _hist_em}
                st.session_state[_dupont_cache_key + '_key'] = _data_key

            def _sparkline(data_list, color, height=28):
                """生成 SVG sparkline 迷你折线图"""
                if not data_list or len(data_list) < 2:
                    return "<span style='color:#ccc;font-size:0.7em;'>—</span>"
                lo, hi = min(data_list), max(data_list)
                rng = hi - lo if hi != lo else 1
                w, h = 80, height
                pts = []
                for i, v in enumerate(data_list):
                    x = i / (len(data_list) - 1) * w
                    y = h - (v - lo) / rng * (h - 4) - 2
                    pts.append(f"{x:.1f},{y:.1f}")
                poly = " ".join(pts)
                area_pts = f"0,{h} {poly} {w},{h}"
                return (
                    f'<svg width="{w}" height="{h}" style="display:inline-block;vertical-align:middle;">'
                    f'<polygon points="{area_pts}" fill="{color}" opacity="0.12"/>'
                    f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>'
                    f'<circle cx="{pts[-1].split(",")[0]}" cy="{pts[-1].split(",")[1]}" r="3" fill="{color}"/>'
                    f'</svg>'
                )

            dupont_tree_html = f"""
            <div style="margin:10px 0 18px;">
                <!-- ROE 顶层大卡片 -->
                <div style="display:flex;flex-direction:column;align-items:center;">
                    <div style="background:linear-gradient(135deg,#1a237e,#3949ab,#5c6bc0);color:white;
                                padding:18px 52px;border-radius:16px;text-align:center;
                                box-shadow:0 4px 20px rgba(26,35,126,0.35);min-width:260px;">
                        <div style="font-size:0.85em;opacity:0.85;letter-spacing:1px;margin-bottom:4px;">ROE 净资产收益率</div>
                        <div style="font-size:2.2em;font-weight:800;{roe_c}">{roe_s}</div>
                        <div style="margin-top:6px;">{_sparkline(_hist_roe, '#9fa8da', 32)}</div>
                    </div>
                    <!-- 连接线 -->
                    <div style="width:3px;height:28px;background:linear-gradient(to bottom,#5c6bc0,#90a4ae);margin:0 auto;border-radius:2px;"></div>
                    <div style="width:70%;border-top:3px solid #90a4ae;margin:0 auto;border-radius:2px;"></div>
                    <div style="width:70%;display:flex;justify-content:space-between;">
                        <div style="width:3px;height:28px;background:linear-gradient(to bottom,#90a4ae,#7b1fa2);border-radius:2px;"></div>
                        <div style="width:3px;height:28px;background:linear-gradient(to bottom,#90a4ae,#2e7d32);border-radius:2px;"></div>
                        <div style="width:3px;height:28px;background:linear-gradient(to bottom,#90a4ae,#e65100);border-radius:2px;"></div>
                    </div>
                </div>
                <!-- 三因素卡片 -->
                <div style="width:100%;display:flex;justify-content:space-between;gap:14px;margin-top:0;">
                    <div style="flex:1;text-align:center;background:linear-gradient(135deg,#f3e5f5,#ede7f6);
                                border-radius:14px;padding:16px 12px;border-top:4px solid #7b1fa2;
                                box-shadow:0 2px 8px rgba(123,31,162,0.12);
                                display:flex;flex-direction:column;min-width:0;">
                        <div style="font-size:0.82em;color:#7b1fa2;font-weight:700;letter-spacing:0.5px;">净利率</div>
                        <div style="font-size:1.6em;font-weight:800;margin:4px 0;{nm_c}">{nm_s}</div>
                        <div style="margin:4px 0;">{_sparkline(_hist_nm, '#7b1fa2')}</div>
                        <div style="font-size:0.72em;color:#888;margin-top:2px;">净利润 ÷ 营业收入</div>
                    </div>
                    <div style="flex:1;text-align:center;background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
                                border-radius:14px;padding:16px 12px;border-top:4px solid #2e7d32;
                                box-shadow:0 2px 8px rgba(46,125,50,0.12);
                                display:flex;flex-direction:column;min-width:0;">
                        <div style="font-size:0.82em;color:#2e7d32;font-weight:700;letter-spacing:0.5px;">× 资产周转率</div>
                        <div style="font-size:1.6em;font-weight:800;margin:4px 0;{at_c}">{at_s}</div>
                        <div style="margin:4px 0;">{_sparkline(_hist_at, '#2e7d32')}</div>
                        <div style="font-size:0.72em;color:#888;margin-top:2px;">营业收入 ÷ 总资产</div>
                    </div>
                    <div style="flex:1;text-align:center;background:linear-gradient(135deg,#fff3e0,#ffe0b2);
                                border-radius:14px;padding:16px 12px;border-top:4px solid #e65100;
                                box-shadow:0 2px 8px rgba(230,81,0,0.12);
                                display:flex;flex-direction:column;min-width:0;">
                        <div style="font-size:0.82em;color:#e65100;font-weight:700;letter-spacing:0.5px;">× 权益乘数</div>
                        <div style="font-size:1.6em;font-weight:800;margin:4px 0;{em_c}">{em_s}</div>
                        <div style="margin:4px 0;">{_sparkline(_hist_em, '#e65100')}</div>
                        <div style="font-size:0.72em;color:#888;margin-top:2px;">总资产 ÷ 净资产</div>
                    </div>
                </div>
                <div style="margin-top:14px;text-align:center;font-size:0.8em;color:#888;">
                    ROE = 净利率 × 资产周转率 × 权益乘数 &nbsp;│&nbsp; ● 最新值 &nbsp;│&nbsp; — 近{len(_periods_all)}年趋势
                </div>
            </div>
            """
            st.markdown(dupont_tree_html, unsafe_allow_html=True)

            # 文字解读 — 更紧凑的卡片式布局
            drivers = dupont.get('drivers', [])
            if drivers:
                driver_cards = ""
                for d in drivers:
                    driver_cards += (
                        f"<div style='background:#f8f9fa;border-left:3px solid #1565c0;"
                        f"border-radius:6px;padding:6px 12px;margin:3px 0;"
                        f"font-size:0.85em;color:#444;'>{d}</div>"
                    )
                st.markdown(
                    f"<div style='margin-top:4px;'>"
                    f"<div style='font-size:0.85em;font-weight:600;color:#333;margin-bottom:4px;'>📝 分析解读</div>"
                    f"{driver_cards}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info('数据不足，无法进行杜邦分析')
    else:
        st.info('暂无原始数据')

    # ════════════════════════════════════════
    # 四、波特五力分析
    # ════════════════════════════════════════
    st.markdown("---")
    st.subheader(f'⚔️ 波特五力分析 ({sel_period})')

    if raw_data:
        _porter_cache_key = f"_porter_{_data_key}_{sel_period}"
        if st.session_state.get(_porter_cache_key + '_key') == f"{_data_key}_{sel_period}":
            forces = st.session_state[_porter_cache_key]
        else:
            forces = analyze_porter_five_forces(raw_data, sel_period)
            st.session_state[_porter_cache_key] = forces
            st.session_state[_porter_cache_key + '_key'] = f"{_data_key}_{sel_period}"
        if forces:
            level_color_map = {'强': '#43a047', '中': '#f0a500', '弱': '#e53935'}
            level_bg_map = {'强': '#e8f5e9', '中': '#fff8e1', '弱': '#ffebee'}

            cards_html = (
                "<div style='display:flex;gap:12px;align-items:stretch;'>"
            )
            for force in forces:
                lc = level_color_map.get(force['level'], '#888')
                lb = level_bg_map.get(force['level'], '#f5f5f5')
                cards_html += (
                    f"<div style='flex:1 1 0;min-width:0;text-align:center;"
                    f"padding:22px 14px;background:{lb};"
                    f"border-radius:14px;border-top:4px solid {lc};"
                    f"box-shadow:0 2px 8px rgba(0,0,0,0.06);"
                    f"display:flex;flex-direction:column;"
                    f"min-height:220px;'>"
                    f"<div style='font-size:2.5em;margin-bottom:10px;'>{force['icon']}</div>"
                    f"<div style='font-size:1.05em;font-weight:700;color:#333;margin-bottom:12px;'>{force['name']}</div>"
                    f"<div style='font-size:1.5em;font-weight:bold;color:{lc};margin-bottom:14px;'>"
                    f"{force['emoji']} {force['level']}</div>"
                    f"<div style='font-size:0.95em;color:#555;line-height:1.7;flex:1;'>{force['reason']}</div>"
                    f"</div>"
                )
            cards_html += "</div>"
            st.markdown(cards_html, unsafe_allow_html=True)
        else:
            st.info('数据不足，无法进行波特五力分析')
    else:
        st.info('暂无原始数据')

    # ════════════════════════════════════════
    # 五、风险评估（紧凑标签式）
    # ════════════════════════════════════════
    st.markdown("---")
    st.subheader(f'⚠️ 风险提示 ({sel_period})')
    if 'risk_factors' in data and data['risk_factors']:
        risks = data['risk_factors']
        # 标签流式布局：每个风险一个小胶囊，自动换行
        chips_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin:4px 0;'>"
        for risk in risks:
            chips_html += (
                f"<div style='background:#fff8f0;border:1px solid #ffe0b2;"
                f"border-radius:16px;padding:4px 12px;"
                f"font-size:0.82em;color:#555;white-space:nowrap;'>"
                f"⚠️ {risk}</div>"
            )
        chips_html += "</div>"
        st.markdown(chips_html, unsafe_allow_html=True)
    else:
        st.info('暂无风险提示')

    # ════════════════════════════════════════
    # 六、投资建议
    # ════════════════════════════════════════
    st.markdown("---")
    st.subheader('💡 投资建议')
    if 'investment_recommendation' in data:
        recommendation = data['investment_recommendation']
        st.info(recommendation)
    else:
        st.info('暂无投资建议')

class DataProcessor:
    """数据处理协调器"""

    def __init__(self):
        self.data_source_manager = get_data_source_manager()
        self.metrics_calculator = FinancialMetrics()
        self.trend_analyzer = TrendAnalysis()
        self.insights_generator = InsightsGenerator()
        self.chart_generator = ChartGenerator()

    def process_stock_data(self, stock_code: str, start_year: str, end_year: str, period: str, period_label: str = '', stock_info: Dict = None) -> Dict[str, Any]:
        """处理股票数据"""
        result = {
            'charts': {},
            'insights': {},
            'latest_period': None,
            'trend_analysis': {},
            'period_data': {},
            'period_patterns': {},
            'periods': []
        }

        # 检查缓存
        cache_key = f"{stock_code}_{start_year}_{end_year}_{period}"
        cache_data = cache_manager.get('stock_analysis', cache_key)

        if cache_data:
            print(f"使用缓存数据: {cache_key}")
            cached_result = cache_data.copy()
            # 重新生成图表（因为图表对象不能缓存）
            cached_result['charts'] = self._regenerate_charts(cached_result, period_label)
            return cached_result

        # 加载和处理数据
        raw_data = self._load_stock_data(stock_code, start_year, end_year, period)

        if not raw_data:
            return result

        # 计算财务指标
        financial_metrics = self._calculate_all_metrics(raw_data)

        # 生成图表
        charts = self._generate_charts(raw_data, financial_metrics, period, period_label)

        # 生成洞察
        insights = self._generate_insights(financial_metrics, stock_code)

        # 生成执行摘要和风险因素（传入 raw_data 和 stock_info 以支持丰富摘要）
        executive_summary = self.insights_generator.generate_executive_summary(
            financial_metrics, raw_data=raw_data, stock_info=stock_info)
        risk_factors = self.insights_generator.generate_risk_factors(financial_metrics)

        # 趋势分析
        periods = sorted(raw_data.keys())
        if len(periods) > 1:
            trend_analysis = self._perform_trend_analysis(raw_data, periods)
            result['trend_analysis'] = trend_analysis

        # 获取最新周期数据
        latest_period_data = self._get_latest_period_data(raw_data, financial_metrics, periods)

        # 填充结果
        result['charts'] = charts
        result['insights'] = insights
        result['executive_summary'] = executive_summary
        result['risk_factors'] = risk_factors
        result['investment_recommendation'] = self._generate_investment_recommendation(financial_metrics)
        result['latest_period'] = latest_period_data
        result['periods'] = periods
        result['_raw_data'] = raw_data

        # 保存到缓存（不缓存图表，但缓存原始数据以支持趋势分析）
        cacheable_result = result.copy()
        cacheable_result['charts'] = {}  # 图表不缓存
        cache_manager.set(cacheable_result, 'stock_analysis', cache_key)

        return result

    def _load_stock_data(self, stock_code: str, start_year: str, end_year: str, period: str) -> Dict[str, Any]:
        """加载股票数据"""
        try:
            raw_data = self.data_source_manager.get_stock_financial_data(
                stock_code, start_year, end_year, period
            )
            source_name = self.data_source_manager.active_source_name
            print(f"[{source_name}] 成功加载 {stock_code} 数据，共 {len(raw_data)} 个周期")
            return raw_data
        except Exception as e:
            print(f"加载股票数据时出错: {e}")
            return {}

    def _calculate_all_metrics(self, raw_data: Dict) -> Dict[str, Any]:
        """计算所有财务指标"""
        metrics = {
            'profitability_ratios': {},
            'growth_rates': {},
            'liquidity_ratios': {},
            'leverage_ratios': {}
        }

        if not raw_data:
            return metrics

        # 提取数据用于计算（兼容新旧字段名）
        income_data = {'营业收入': [], '归母净利润': [], '营业成本': []}
        balance_data = {'总资产': [], '总负债': [], '所有者权益': [],
                       '流动资产': [], '流动负债': [], '存货': []}

        periods = sorted(raw_data.keys())
        for period in periods:
            period_data = raw_data[period]

            # 收入数据
            income_stmt = period_data.get('income_statement', {})
            # 营业收入：优先用"营业收入"，没有则用"营业总收入"
            rev = income_stmt.get('营业收入', [0])[0] or income_stmt.get('营业总收入', [0])[0]
            income_data['营业收入'].append(rev)
            income_data['归母净利润'].append(income_stmt.get('归母净利润', [0])[0])
            income_data['营业成本'].append(income_stmt.get('营业成本', [0])[0])

            # 资产负债数据（兼容新旧字段名）
            balance_sheet = period_data.get('balance_sheet', {})
            balance_data['总资产'].append(
                balance_sheet.get('资产总计', [0])[0] or balance_sheet.get('总资产', [0])[0])
            balance_data['总负债'].append(
                balance_sheet.get('负债合计', [0])[0] or balance_sheet.get('总负债', [0])[0])
            balance_data['所有者权益'].append(
                balance_sheet.get('所有者权益合计', [0])[0])
            balance_data['流动资产'].append(
                balance_sheet.get('流动资产合计', [0])[0] or balance_sheet.get('流动资产', [0])[0])
            balance_data['流动负债'].append(
                balance_sheet.get('流动负债合计', [0])[0] or balance_sheet.get('流动负债', [0])[0])
            balance_data['存货'].append(balance_sheet.get('存货', [0])[0])

        # 计算各项指标
        if income_data['营业收入']:
            metrics['profitability_ratios'] = self.metrics_calculator.calculate_profitability_ratios(income_data)
            metrics['growth_rates'] = self.metrics_calculator.calculate_growth_rates(income_data)

        if balance_data['总资产']:
            metrics['liquidity_ratios'] = self.metrics_calculator.calculate_liquidity_ratios(balance_data)
            metrics['leverage_ratios'] = self.metrics_calculator.calculate_leverage_ratios(balance_data)

        return metrics

    def _generate_charts(self, raw_data: Dict, metrics: Dict, period: str, period_label: str = '') -> Dict[str, Any]:
        """生成图表"""
        charts = {}
        periods = sorted(raw_data.keys())

        if not periods:
            return charts

        # 优先使用传入的中文周期标签，回退到 get_period_display_name
        display_name = period_label if period_label else get_period_display_name(period)

        # 营收趋势图 — 原始值除以 1e8 转为亿，保留两位小数
        revenue_values = []
        for p in periods:
            inc = raw_data[p].get('income_statement', {})
            v = inc.get('营业收入', [0])[0] or inc.get('营业总收入', [0])[0]
            revenue_values.append(v)
        revenue_data = {
            '周期': periods,
            '营业收入(亿)': [round(float(val) / 1e8, 2) if val is not None else 0.0 for val in revenue_values]
        }
        charts['revenue_chart'] = self.chart_generator.create_line_chart(
            revenue_data, '营业收入(亿)', f'营业收入趋势-{display_name}'
        )

        # 利润对比图 — 原始值除以 1e8 转为亿，保留两位小数
        profit_values = [raw_data[p].get('income_statement', {}).get('归母净利润', [0])[0] for p in periods]
        profit_data = {
            '周期': periods,
            '归母净利润(亿)': [round(float(val) / 1e8, 2) if val is not None else 0.0 for val in profit_values]
        }
        charts['profit_chart'] = self.chart_generator.create_bar_chart(
            profit_data, '归母净利润(亿)', f'归母净利润-{display_name}'
        )

        return charts

    def _regenerate_charts(self, cached_data: Dict) -> Dict[str, Any]:
        """重新生成图表（用于缓存数据）"""
        # 这里应该从缓存的数据重新生成图表
        # 简化处理，返回空图表
        return {}

    def _generate_insights(self, metrics: Dict, stock_code: str) -> Dict[str, List[str]]:
        """生成分析洞察"""
        return self.insights_generator.generate_comprehensive_report(metrics)

    def _perform_trend_analysis(self, raw_data: Dict, periods: List[str]) -> Dict[str, Any]:
        """执行趋势分析"""
        if len(periods) < 2:
            return {}

        # 计算营收和净利润的复合增长率（兼容新旧字段名）
        revenues, profits = [], []
        for p in periods:
            inc = raw_data[p].get('income_statement', {})
            revenues.append(inc.get('营业收入', [0])[0] or inc.get('营业总收入', [0])[0])
            profits.append(inc.get('归母净利润', [0])[0])
        if revenues and len(revenues) > 1:
            rev_cagr = self.trend_analyzer.calculate_compound_growth_rate(revenues)
            rev_direction = self.trend_analyzer.analyze_trend_direction(revenues)
            profit_cagr = self.trend_analyzer.calculate_compound_growth_rate(profits)
            profit_direction = self.trend_analyzer.analyze_trend_direction(profits)

            return {
                '营业收入': {
                    '复合增长率': rev_cagr,
                    '趋势方向': rev_direction,
                    '年均增长': rev_cagr
                },
                '归母净利润': {
                    '复合增长率': profit_cagr,
                    '趋势方向': profit_direction,
                    '年均增长': profit_cagr
                }
            }

        return {}

    def _get_latest_period_data(self, raw_data: Dict, metrics: Dict, periods: List[str]) -> Dict[str, Any]:
        """获取最新周期数据，同比直接使用接口返回值"""
        if not periods:
            return {}

        latest_period = periods[-1]
        _inc = raw_data.get(latest_period, {}).get('income_statement', {})

        revenue = _inc.get('营业收入', [0])[0] or _inc.get('营业总收入', [0])[0]
        profit = _inc.get('归母净利润', [0])[0]

        # 同比：直接取接口返回的 [value, yoy] 中 yoy 字段
        rev_entry = _inc.get('营业收入', [0]) or _inc.get('营业总收入', [0])
        profit_entry = _inc.get('归母净利润', [0])
        revenue_growth = rev_entry[1] if len(rev_entry) >= 2 and rev_entry[1] else 0
        profit_growth = profit_entry[1] if len(profit_entry) >= 2 and profit_entry[1] else 0

        # 净利率
        if revenue > 0 and profit > 0:
            ratio = profit / revenue
            if ratio > 1000:
                corrected_revenue = revenue * 100000000 if revenue < 10000 else revenue
                profit_margin = profit / corrected_revenue
            else:
                profit_margin = ratio
        else:
            profit_margin = 0

        # ROE：从 raw_data 计算
        _bs = raw_data.get(latest_period, {}).get('balance_sheet', {})
        equity = _bs.get('所有者权益合计', [0])[0]
        roe = (profit / equity) if equity else 0.15

        # 计算净利润率和 ROE 的同比 pp 差值
        margin_pp = 0
        roe_pp = 0
        if len(periods) > 1:
            prev_p = periods[-2]
            prev_inc = raw_data.get(prev_p, {}).get('income_statement', {})
            prev_rev = prev_inc.get('营业收入', [0])[0] or prev_inc.get('营业总收入', [0])[0]
            prev_profit = prev_inc.get('归母净利润', [0])[0]
            prev_bs = raw_data.get(prev_p, {}).get('balance_sheet', {})
            prev_equity = prev_bs.get('所有者权益合计', [0])[0]
            prev_margin = (prev_profit / prev_rev) if prev_rev else 0
            prev_roe = (prev_profit / prev_equity) if prev_equity else 0
            margin_pp = (profit_margin - prev_margin) * 100  # 转为 pp
            roe_pp = (roe - prev_roe) * 100  # 转为 pp

        return {
            'period': latest_period,
            'key_metrics': {
                'revenue': revenue,
                'net_profit': profit,
                'revenue_growth': revenue_growth,
                'profit_growth': profit_growth,
                'profit_margin': profit_margin,
                'roe': roe,
                'margin_change_pp': margin_pp,
                'roe_change_pp': roe_pp,
                # 兼容旧字段（不再使用但避免报错）
                'roe_change': roe_pp,
                'margin_change': margin_pp,
            }
        }

    def _generate_investment_recommendation(self, metrics: Dict[str, Any]) -> str:
        """生成投资建议"""
        # 获取关键指标
        profit_ratios = metrics.get('profitability_ratios', {})
        growth_rates = metrics.get('growth_rates', {})
        liquidity_ratios = metrics.get('liquidity_ratios', {})

        latest_profit_margin = profit_ratios.get('净利润率', [0])[-1] if profit_ratios.get('净利润率') else 0

        # 处理增长率，过滤掉None值
        revenue_growth_list = growth_rates.get('营业收入增长率', [0])
        latest_revenue_growth = 0
        if revenue_growth_list and len(revenue_growth_list) > 0:
            # 过滤掉None值，取最后一个有效值
            valid_growth_rates = [x for x in revenue_growth_list if x is not None]
            if valid_growth_rates:
                latest_revenue_growth = valid_growth_rates[-1]

        latest_current_ratio = liquidity_ratios.get('流动比率', [0])[-1] if liquidity_ratios.get('流动比率') else 0

        # 综合评分
        score = 0
        if latest_profit_margin > 0.25:
            score += 3
        elif latest_profit_margin > 0.15:
            score += 2
        else:
            score += 1

        if latest_revenue_growth > 0.2:
            score += 3
        elif latest_revenue_growth > 0.05:
            score += 2
        else:
            score += 1

        if latest_current_ratio > 2.0:
            score += 3
        elif latest_current_ratio > 1.0:
            score += 2
        else:
            score += 1

        if score >= 8:
            return "🎯 强烈推荐：公司财务表现卓越，盈利能力强，成长性良好，流动性充足。建议长期持有，分享公司成长红利。"
        elif score >= 6:
            return "👍 推荐：公司基本面稳健，各项指标健康。适合稳健型投资者，建议采用分批建仓策略。"
        elif score >= 4:
            return "⚖️ 中性：公司表现一般，建议观望。可小仓位配置，密切关注后续财务表现改善情况。"
        else:
            return "⚠️ 谨慎：多项指标低于健康水平，投资风险较高。建议等待基本面改善信号再考虑投资。"

    def _get_sample_year_data(self, year: str) -> Dict[str, Any]:
        """获取单年示例数据"""
        # 基于年份生成一些示例数据
        base_revenue = 1000 + (int(year) - 2021) * 200
        base_profit = 200 + (int(year) - 2021) * 40

        return {
            'income_statement': {
                '营业总收入': [base_revenue],
                '营业收入': [base_revenue],
                '归母净利润': [base_profit],
                '营业成本': [base_revenue * 0.6]
            },
            'balance_sheet': {
                '资产总计': [base_revenue * 2],
                '总资产': [base_revenue * 2],
                '负债合计': [base_revenue * 0.3],
                '总负债': [base_revenue * 0.3],
                '所有者权益合计': [base_revenue * 1.7],
                '流动资产合计': [base_revenue * 1.2],
                '流动资产': [base_revenue * 1.2],
                '流动负债合计': [base_revenue * 0.4],
                '流动负债': [base_revenue * 0.4],
                '存货': [base_revenue * 0.2]
            },
            'cash_flow': {
                '经营活动产生的现金流量净额': [base_profit * 1.1],
                '经营活动现金流净额': [base_profit * 1.1]
            }
        }

if __name__ == '__main__':
    main()