# src/visualization/dashboard_layout.py
import streamlit as st
from typing import Dict, List, Any
import plotly.graph_objects as go
from datetime import datetime

class DashboardLayout:
    """仪表板布局管理器"""

    def __init__(self):
        self.page_config = {
            'page_title': '股票财务分析系统',
            'page_icon': '📊',
            'layout': 'wide',
            'initial_sidebar_state': 'expanded'
        }

    def setup_page(self):
        """设置页面配置"""
        st.set_page_config(**self.page_config)

        # 自定义CSS样式
        st.markdown("""
        <style>
        :root {
            --fv-cat-text: #0d47a1;
            --fv-cat-border: #90caf9;
            --fv-hl-bg: #e3f2fd;
            --fv-hl-text: #1565c0;
            --fv-hl-border: #90caf9;
            --fv-row-border: #e0e0e0;
            --fv-yoy-pos: #c62828;
            --fv-yoy-neg: #2e7d32;
            --fv-yoy-neu: #616161;
            --fv-header-border: #666;
            --fv-subheader-border: #bbb;
            --fv-subheader-text: #757575;
            --fv-blank-bg: #f5f5f5;
        }
        /* Streamlit dark 模式：通过 html[data-theme="dark"] 或 .stApp 检测 */
        html[data-theme="dark"] {
            --fv-cat-text: #bbdefb;
            --fv-cat-border: #444;
            --fv-hl-bg: #1565c020;
            --fv-hl-text: #64b5f6;
            --fv-hl-border: #444;
            --fv-row-border: #333;
            --fv-yoy-pos: #ef5350;
            --fv-yoy-neg: #66bb6a;
            --fv-yoy-neu: #bdbdbd;
            --fv-header-border: #555;
            --fv-subheader-border: #444;
            --fv-subheader-text: #9e9e9e;
            --fv-blank-bg: #1a1a1a;
        }
        /* 也兼容 prefers-color-scheme */
        @media (prefers-color-scheme: dark) {
            :root:not([data-theme="light"]) {
                --fv-cat-text: #bbdefb;
                --fv-cat-border: #444;
                --fv-hl-bg: #1565c020;
                --fv-hl-text: #64b5f6;
                --fv-hl-border: #444;
                --fv-row-border: #333;
                --fv-yoy-pos: #ef5350;
                --fv-yoy-neg: #66bb6a;
                --fv-yoy-neu: #bdbdbd;
                --fv-header-border: #555;
                --fv-subheader-border: #444;
                --fv-subheader-text: #9e9e9e;
                --fv-blank-bg: #1a1a1a;
            }
        }
        .main {
            padding: 0rem 1rem;
        }
        .stMetric {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 0.5rem solid #d32f2f;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: #000000 !important;
        }
        .stMetric .st-emotion-cache-1v4smiu {
            color: #000000 !important;
        }
        .stMetric .st-emotion-cache-10trblm {
            color: #000000 !important;
        }
        .stMetric .st-emotion-cache-1wmy9hl {
            color: #000000 !important;
        }
        .insight-box {
            background-color: #f8f9fa;
            border: 2px solid #0d47a1;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
            color: #0d47a1;
            font-weight: 600;
            line-height: 1.5;
        }
        .chart-container {
            background: linear-gradient(135deg, #ffffff, #f5f6f8);
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
            margin: 12px 0;
            border: 1px solid #e8eaed;
        }
        html[data-theme="dark"] .chart-container {
            background: linear-gradient(135deg, #1e1e2e, #252535);
            border-color: #333;
            box-shadow: 0 2px 12px rgba(0,0,0,0.3), 0 1px 3px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)

        # 回到顶部按钮 — 用 JS 直接注入到 body，绕过 Streamlit 容器限制
        st.markdown("""
        <script>
        (function(){
            // 避免重复注入
            if (document.getElementById('back-to-top-btn')) return;
            var btn = document.createElement('button');
            btn.id = 'back-to-top-btn';
            btn.innerHTML = '⬆';
            btn.title = '回到顶部';
            btn.style.cssText = 'position:fixed;bottom:32px;right:32px;z-index:2147483647;width:50px;height:50px;border-radius:50%;background:linear-gradient(135deg,#1565c0,#0d47a1);color:white;border:none;cursor:pointer;font-size:1.6em;line-height:50px;text-align:center;box-shadow:0 4px 20px rgba(21,101,192,0.5);opacity:0;transform:translateY(10px);transition:opacity 0.3s,transform 0.3s;pointer-events:none;';
            btn.onclick = function(){ window.scrollTo({top:0,behavior:'smooth'}); };
            btn.onmouseover = function(){ btn.style.transform='translateY(-2px)'; btn.style.boxShadow='0 6px 24px rgba(21,101,192,0.6)'; };
            btn.onmouseout = function(){ btn.style.transform='translateY(0)'; btn.style.boxShadow='0 4px 20px rgba(21,101,192,0.5)'; };
            document.body.appendChild(btn);
            window.addEventListener('scroll', function(){
                if (window.scrollY > 300) {
                    btn.style.opacity = '1';
                    btn.style.transform = 'translateY(0)';
                    btn.style.pointerEvents = 'auto';
                } else {
                    btn.style.opacity = '0';
                    btn.style.transform = 'translateY(10px)';
                    btn.style.pointerEvents = 'none';
                }
            }, {passive: true});
        })();
        </script>
        """, unsafe_allow_html=True)

    def create_sidebar(self, available_years: List[str]) -> Dict[str, Any]:
        """创建侧边栏"""

        start_year = st.sidebar.selectbox(
            '开始年份',
            available_years,
            index=len(available_years) - 5  # 默认5年前
        )

        end_year = st.sidebar.selectbox(
            '结束年份',
            available_years,
            index=len(available_years) - 1  # 默认今年
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
            'start_year': start_year,
            'end_year': end_year,
            'metrics': selected_metrics,
            'export_format': export_format
        }

    def create_main_tabs(self):
        """创建主标签页"""
        return st.tabs([
            '📊 财务概览',
            '📈 趋势分析',
            '📊 财务数据',
            '📋 综合报告'
        ])

    def display_key_metrics(self, metrics_data: Dict[str, float], year: str = None,
                           period_label: str = ''):
        """显示关键指标卡片

        营业收入/净利润：同比直取接口 yoy，格式 ±x.xx%
        净利润率/ROE：同比需计算 pp 差值，格式 ±x.xxpp
        """
        if year and period_label:
            year_info = f" ({year}{period_label})"
        elif year:
            year_info = f" ({year}年)"
        else:
            year_info = ""
        st.subheader(f'🔑 关键财务指标{year_info}')

        col1, col2, col3, col4 = st.columns(4)

        # ── 营业收入：接口直取 yoy ──
        rev_growth = metrics_data.get('revenue_growth', 0)
        rev_color = '#43a047' if rev_growth >= 0 else '#e53935'
        rev_sign = '+' if rev_growth >= 0 else ''

        # ── 归母净利润：接口直取 yoy ──
        profit_growth = metrics_data.get('profit_growth', 0)
        profit_color = '#43a047' if profit_growth >= 0 else '#e53935'
        profit_sign = '+' if profit_growth >= 0 else ''

        # ── 净利润率：计算 pp 差值 ──
        margin_pp = metrics_data.get('margin_change_pp', 0)
        margin_color = '#43a047' if margin_pp >= 0 else '#e53935'
        margin_sign = '+' if margin_pp >= 0 else ''

        # ── ROE：计算 pp 差值 ──
        roe_pp = metrics_data.get('roe_change_pp', 0)
        roe_color = '#43a047' if roe_pp >= 0 else '#e53935'
        roe_sign = '+' if roe_pp >= 0 else ''

        card_html = """
        <style>
        .metric-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa);
            padding: 14px 16px;
            border-radius: 10px;
            border-left: 4px solid #1565c0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            text-align: center;
            margin: 2px;
        }
        .metric-label { color: #888; font-size: 0.82em; margin-bottom: 4px; }
        .metric-value { color: #222; font-size: 1.4em; font-weight: 700; margin-bottom: 2px; }
        .metric-delta { font-size: 0.85em; font-weight: 600; }
        </style>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">营业收入</div>
                <div class="metric-value">¥{metrics_data.get('revenue', 0) / 1e8:.2f}亿</div>
                <div class="metric-delta" style="color:{rev_color}">{rev_sign}{rev_growth:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">归母净利润</div>
                <div class="metric-value">¥{metrics_data.get('net_profit', 0) / 1e8:.2f}亿</div>
                <div class="metric-delta" style="color:{profit_color}">{profit_sign}{profit_growth:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">净利润率</div>
                <div class="metric-value">{metrics_data.get('profit_margin', 0):.2%}</div>
                <div class="metric-delta" style="color:{margin_color}">{margin_sign}{margin_pp:.2f}pp</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">ROE</div>
                <div class="metric-value">{metrics_data.get('roe', 0):.2%}</div>
                <div class="metric-delta" style="color:{roe_color}">{roe_sign}{roe_pp:.2f}pp</div>
            </div>
            """, unsafe_allow_html=True)

    def display_insights(self, insights: Dict[str, List[str]],
                         scores: Dict[str, int] = None):
        """显示分析洞察（雷达图 + Bento 宫格评分卡）

        布局：上方综合评分条 + 左雷达图右Bento宫格
        Bento 宫格：2×N 网格，每个格子 = 图标 + 类别 + 星级 + 一句话
        """
        st.subheader('💡 智能分析洞察')

        if scores is None:
            scores = {}

        active = {k: v for k, v in insights.items() if v}
        if not active:
            st.info('暂无分析数据')
            return

        cats = list(active.keys())
        total_score = sum(scores.get(c, 0) for c in cats)
        max_score = len(cats) * 3
        overall_pct = total_score / max_score if max_score else 0

        if overall_pct >= 0.8:
            overall_label, overall_color, overall_bg = '优秀', '#43a047', '#e8f5e9'
        elif overall_pct >= 0.6:
            overall_label, overall_color, overall_bg = '良好', '#f0a500', '#fff8e1'
        elif overall_pct >= 0.4:
            overall_label, overall_color, overall_bg = '一般', '#ff9800', '#fff3e0'
        else:
            overall_label, overall_color, overall_bg = '关注', '#e53935', '#ffebee'

        # ── 综合评分条 ──
        st.markdown(
            f"<div style='text-align:center;padding:8px 16px;margin:4px 0 12px;"
            f"background:{overall_bg};border-radius:10px;border-left:4px solid {overall_color};'>"
            f"<span style='font-size:0.8em;color:#888;'>综合评分</span> "
            f"<span style='font-size:1.2em;font-weight:bold;color:{overall_color};margin:0 8px;'>"
            f"{total_score}/{max_score}</span> "
            f"<span style='font-size:0.95em;font-weight:600;color:{overall_color};'>{overall_label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # ── 左：雷达图 / 右：Bento 宫格 ──
        left_col, right_col = st.columns([1, 1])

        with left_col:
            radar_cats = [self._get_category_name(c)[:4] for c in cats]
            radar_vals = [scores.get(c, 0) for c in cats]
            radar_cats_closed = radar_cats + [radar_cats[0]]
            radar_vals_closed = radar_vals + [radar_vals[0]]

            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=radar_vals_closed, theta=radar_cats_closed, fill='toself',
                fillcolor='rgba(21,101,192,0.15)',
                line=dict(color='#1565c0', width=2.5),
                marker=dict(size=8, color='#1565c0', line=dict(width=2, color='white')),
                name='评分',
            ))
            fig.add_trace(go.Scatterpolar(
                r=[3] * len(radar_cats_closed), theta=radar_cats_closed,
                fill='none', line=dict(color='#ccc', width=1, dash='dot'),
                hoverinfo='skip', showlegend=False,
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, range=[0, 3.5],
                        tickvals=[1, 2, 3], ticktext=['1', '2', '3'],
                        tickfont=dict(size=9),
                        gridcolor='rgba(200,200,200,0.4)',
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=11, color='#333'),
                        gridcolor='rgba(200,200,200,0.4)',
                    ),
                    bgcolor='rgba(250,250,252,1)',
                ),
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=20),
                height=260,
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

        with right_col:
            # Bento 宫格：2列 × N行
            GRID_COLORS = [
                ('#e8f5e9', '#43a047', '#c8e6c9'),
                ('#fff8e1', '#f0a500', '#ffecb3'),
                ('#ffebee', '#e53935', '#ffcdd2'),
                ('#e3f2fd', '#1565c0', '#bbdefb'),
                ('#f3e5f5', '#7b1fa2', '#e1bee7'),
            ]
            ncols = 2
            nrows = (len(cats) + ncols - 1) // ncols
            grid_cols = st.columns(ncols)
            for i, cat in enumerate(cats):
                row = i // ncols
                col = i % ncols
                icon = self._get_category_icon(cat)
                name = self._get_category_name(cat)[:4]
                score = scores.get(cat, 0)
                stars = '⭐' * score + '·' * (3 - score) if score else '—'
                text = active[cat][0] if active[cat] else ''

                bg, border, _line = GRID_COLORS[i % len(GRID_COLORS)]

                with grid_cols[col]:
                    st.markdown(
                        f"<div style='background:{bg};border-radius:10px;"
                        f"border-top:3px solid {border};"
                        f"padding:10px 12px;margin:3px 2px;"
                        f"height:100%;box-sizing:border-box;'>"
                        f"<div style='display:flex;align-items:center;gap:6px;margin-bottom:4px;'>"
                        f"<span style='font-size:1.4em;'>{icon}</span>"
                        f"<span style='font-size:0.9em;font-weight:700;color:#333;'>{name}</span>"
                        f"<span style='font-size:0.75em;margin-left:auto;'>{stars}</span>"
                        f"</div>"
                        f"<div style='font-size:0.82em;color:#555;line-height:1.4;'>{text}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    def display_chart_with_export(self, fig: go.Figure, chart_title: str,
                                 export_format: str = 'PNG'):
        """显示图表并提供导出功能"""
        st.markdown(f"""
        <div class="chart-container">
        """, unsafe_allow_html=True)

        st.plotly_chart(fig, width='stretch')

        # 导出按钮
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button(f'导出 {export_format}', key=f'export_{chart_title}'):
                self._export_chart(fig, chart_title, export_format)

        st.markdown("""
        </div>
        """, unsafe_allow_html=True)

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
        filename = f"股票分析_{title.replace(' ', '_')}.{format_type.lower()}"

        try:
            if format_type == 'PNG':
                fig.write_image(filename, scale=2)
            elif format_type == 'PDF':
                fig.write_image(filename)

            st.success(f'图表已导出为 {filename}')
        except Exception as e:
            st.error(f'导出失败: {e}')