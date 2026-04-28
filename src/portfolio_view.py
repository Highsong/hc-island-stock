"""
"我的投资"页面 - 实盘组合
Tab 1: 周记 — 持仓明细（买点/卖点/市值/价格变化）
Tab 2: 年化收益 — 实盘年度记录
"""

import asyncio
import streamlit as st
import pandas as pd
import tempfile, os, base64
from datetime import datetime
from data_portfolio import get_weekly_data, get_annualized_data, load_portfolio, save_portfolio


# ─── 样式 ───
CSS = """
<style>
.pf-section {
    font-size: 0.92rem;
    font-weight: 600;
    margin: 1rem 0 0.4rem 0;
    padding-bottom: 0.2rem;
    border-bottom: 2px solid rgba(128,128,128,0.3);
}

.table-wrapper { overflow-x: auto; margin-bottom: 1rem; }

.pf-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.pf-table th {
    background: rgba(128,128,128,0.15);
    font-weight: 600;
    padding: 0.5rem 0.6rem;
    text-align: center;
    border-bottom: 2px solid rgba(128,128,128,0.3);
    white-space: nowrap;
}
.pf-table td {
    padding: 0.4rem 0.6rem;
    text-align: center;
    border-bottom: 1px solid rgba(128,128,128,0.15);
    white-space: nowrap;
}
.pf-table tr:hover { background: rgba(128,128,128,0.08); }

.pf-table .tr-sep td { padding: 0; border: none; }

.pf-table .tr-special {
    background: rgba(255, 183, 77, 0.2) !important;
    font-weight: 600;
    font-size: 0.82rem;
}
.pf-table .tr-special td {
    border-top: 1px solid rgba(255, 152, 0, 0.4);
    border-right: 1px solid rgba(128,128,128,0.12);
    padding: 0.5rem 0.6rem;
}
.pf-table .tr-special td:last-child {
    border-right: none;
}

.buy  { color: #EF5350; font-weight: 600; }
.sell { color: #66BB6A; font-weight: 600; }

/* 编辑面板 */
.edit-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5rem 0;
}
.edit-table th {
    text-align: center;
    font-size: 0.78rem;
    color: #888;
    padding: 0.3rem 0.4rem;
    border-bottom: 1px solid rgba(128,128,128,0.2);
}
.edit-table td {
    padding: 0.2rem 0.4rem;
    text-align: center;
    vertical-align: middle;
}
.edit-table .stNumberInput {
    min-width: 80px;
}

/* 文章展示区 */
.article-section {
    margin-top: 1.5rem;
    padding: 1.2rem;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(21,101,192,0.05), rgba(103,58,183,0.05));
    border: 1px solid rgba(128,128,128,0.2);
}
</style>
"""

# ════════════════════════════════════════════
# 文章用表格 — 三种风格 CSS（支持自定义）
# ════════════════════════════════════════════

# 默认颜色配置（财经风/杂志风/仪表盘风共用 key 前缀）
_CSS_DEFAULTS = {
    # 财经风
    "fin_header_bg": "#f5f5f5", "fin_header_text": "#333", "fin_header_border": "#ccc",
    "fin_row_odd": "#ffffff", "fin_row_even": "#f8f9fa", "fin_row_hover": "#e3f2fd",
    "fin_cell_border": "#eee", "fin_cell_text": "#222",
    "fin_badge_pos_bg": "#ffebee", "fin_badge_pos_text": "#c62828",
    "fin_badge_neg_bg": "#e8f5e9", "fin_badge_neg_text": "#2e7d32",
    "fin_badge_neu_bg": "#f5f5f5", "fin_badge_neu_text": "#666",
    "fin_special_bg": "#fff8e1", "fin_special_border": "#ffe082", "fin_special_text": "#5d4037",
    "fin_sep": "#ffb300", "fin_buy": "#c62828", "fin_sell": "#2e7d32",
    "fin_border_w": 1,
    # 杂志风
    "mag_header_text": "#888", "mag_header_border": "#ddd",
    "mag_row_border": "#f0f0f0", "mag_row_hover": "#fafafa",
    "mag_cell_text": "#333", "mag_name_text": "#111",
    "mag_text_pos": "#d32f2f", "mag_text_neg": "#388e3c", "mag_text_neu": "#999",
    "mag_special_bg": "#fafafa", "mag_special_text": "#444", "mag_special_border": "#eee",
    "mag_sep": "#ddd", "mag_buy": "#d32f2f", "mag_sell": "#388e3c",
    "mag_border_w": 1,
    # 仪表盘风
    "dash_header_bg": "#e8f0fe", "dash_header_text": "#1565c0", "dash_header_border": "#90caf9",
    "dash_row_odd": "#ffffff", "dash_row_even": "#f5f9ff", "dash_row_hover": "#e1f5fe",
    "dash_cell_border": "#bbdefb", "dash_cell_text": "#1a237e",
    "dash_badge_pos_bg": "#fff3e0", "dash_badge_pos_text": "#bf360c",
    "dash_badge_neg_bg": "#e0f2f1", "dash_badge_neg_text": "#004d40",
    "dash_badge_neu_bg": "#f5f5f5", "dash_badge_neu_text": "#616161",
    "dash_special_bg": "#edf4fc", "dash_special_border": "#bbdefb", "dash_special_text": "#1565c0",
    "dash_sep": "#90caf9", "dash_buy": "#bf360c", "dash_sell": "#004d40",
    "dash_border_w": 1,
}

def _c(key):
    """从 session_state 读取自定义颜色，没有则用默认值"""
    return st.session_state.get(f"css_{key}", _CSS_DEFAULTS[key])

def _init_css_state():
    """初始化 session_state 中的颜色值（只在第一次调用时写入默认值）"""
    for k, v in _CSS_DEFAULTS.items():
        sk = f"css_{k}"
        if sk not in st.session_state:
            st.session_state[sk] = v

def _reset_css_state():
    """重置所有自定义颜色为默认值"""
    for k in list(st.session_state.keys()):
        if k.startswith("css_"):
            del st.session_state[k]
    _init_css_state()

_init_css_state()


_color_panel_counter = [0]

def _render_color_panel(style_key):
    """🎨 自定义颜色面板（popover 形式），style_key: fin / mag / dash"""
    _color_panel_counter[0] += 1
    uid = _color_panel_counter[0]
    with st.popover("🎨 自定义", width='content', key=f"popover_{style_key}_{uid}"):
        if style_key == "fin":
            _render_color_controls_fin(uid)
        elif style_key == "mag":
            _render_color_controls_mag(uid)
        elif style_key == "dash":
            _render_color_controls_dash(uid)
        if st.button("↩️ 恢复全部默认", key=f"reset_{style_key}_{uid}", width='stretch'):
            _reset_css_state()
            st.rerun()


def _render_color_controls_fin(uid):
    c1, c2, c3 = st.columns(3)
    st.caption("**专业财经风**")
    c1.markdown("表头")
    st.session_state["css_fin_header_bg"] = c1.color_picker("背景", _c("fin_header_bg"), key=f"fin_cp_hbg_{uid}")
    st.session_state["css_fin_header_text"] = c2.color_picker("文字", _c("fin_header_text"), key=f"fin_cp_ht_{uid}")
    st.session_state["css_fin_header_border"] = c3.color_picker("下边框", _c("fin_header_border"), key=f"fin_cp_hb_{uid}")
    c1.markdown("数据行")
    st.session_state["css_fin_row_odd"] = c1.color_picker("奇数行", _c("fin_row_odd"), key=f"fin_cp_ro_{uid}")
    st.session_state["css_fin_row_even"] = c2.color_picker("偶数行", _c("fin_row_even"), key=f"fin_cp_re_{uid}")
    st.session_state["css_fin_row_hover"] = c3.color_picker("悬停", _c("fin_row_hover"), key=f"fin_cp_rh_{uid}")
    c1.markdown("单元格")
    st.session_state["css_fin_cell_border"] = c1.color_picker("竖线", _c("fin_cell_border"), key=f"fin_cp_cb_{uid}")
    st.session_state["css_fin_cell_text"] = c2.color_picker("文字", _c("fin_cell_text"), key=f"fin_cp_ct_{uid}")
    st.session_state["css_fin_border_w"] = c3.slider("边框粗细", 1, 4, _c("fin_border_w"), key=f"fin_cp_bw_{uid}")
    c1.markdown("涨跌 Badge")
    st.session_state["css_fin_badge_pos_bg"] = c1.color_picker("涨背景", _c("fin_badge_pos_bg"), key=f"fin_cp_bpb_{uid}")
    st.session_state["css_fin_badge_pos_text"] = c2.color_picker("涨文字", _c("fin_badge_pos_text"), key=f"fin_cp_bpt_{uid}")
    st.session_state["css_fin_badge_neg_bg"] = c1.color_picker("跌背景", _c("fin_badge_neg_bg"), key=f"fin_cp_bnb_{uid}")
    st.session_state["css_fin_badge_neg_text"] = c2.color_picker("跌文字", _c("fin_badge_neg_text"), key=f"fin_cp_bnt_{uid}")
    c1.markdown("特殊行 / 横隔")
    st.session_state["css_fin_special_bg"] = c1.color_picker("背景", _c("fin_special_bg"), key=f"fin_cp_sb_{uid}")
    st.session_state["css_fin_special_border"] = c2.color_picker("边框", _c("fin_special_border"), key=f"fin_cp_sbr_{uid}")
    st.session_state["css_fin_special_text"] = c3.color_picker("文字", _c("fin_special_text"), key=f"fin_cp_st_{uid}")
    st.session_state["css_fin_sep"] = c1.color_picker("横隔线", _c("fin_sep"), key=f"fin_cp_sep_{uid}")
    st.session_state["css_fin_buy"] = c2.color_picker("买点", _c("fin_buy"), key=f"fin_cp_buy_{uid}")
    st.session_state["css_fin_sell"] = c3.color_picker("卖点", _c("fin_sell"), key=f"fin_cp_sell_{uid}")


def _render_color_controls_mag(uid):
    c1, c2, c3 = st.columns(3)
    st.caption("**极简杂志风**")
    c1.markdown("表头")
    st.session_state["css_mag_header_text"] = c1.color_picker("文字", _c("mag_header_text"), key=f"mag_cp_ht_{uid}")
    st.session_state["css_mag_header_border"] = c2.color_picker("下边框", _c("mag_header_border"), key=f"mag_cp_hb_{uid}")
    c1.markdown("数据行")
    st.session_state["css_mag_row_border"] = c1.color_picker("行分隔线", _c("mag_row_border"), key=f"mag_cp_rb_{uid}")
    st.session_state["css_mag_row_hover"] = c2.color_picker("悬停", _c("mag_row_hover"), key=f"mag_cp_rh_{uid}")
    st.session_state["css_mag_cell_text"] = c3.color_picker("文字", _c("mag_cell_text"), key=f"mag_cp_ct_{uid}")
    c1.markdown("文字颜色")
    st.session_state["css_mag_text_pos"] = c1.color_picker("涨", _c("mag_text_pos"), key=f"mag_cp_tp_{uid}")
    st.session_state["css_mag_text_neg"] = c2.color_picker("跌", _c("mag_text_neg"), key=f"mag_cp_tn_{uid}")
    st.session_state["css_mag_name_text"] = c3.color_picker("名称", _c("mag_name_text"), key=f"mag_cp_nt_{uid}")
    c1.markdown("特殊行 / 横隔")
    st.session_state["css_mag_special_bg"] = c1.color_picker("背景", _c("mag_special_bg"), key=f"mag_cp_sb_{uid}")
    st.session_state["css_mag_special_text"] = c2.color_picker("文字", _c("mag_special_text"), key=f"mag_cp_st_{uid}")
    st.session_state["css_mag_special_border"] = c3.color_picker("边框", _c("mag_special_border"), key=f"mag_cp_sbr_{uid}")
    st.session_state["css_mag_sep"] = c1.color_picker("横隔线", _c("mag_sep"), key=f"mag_cp_sep_{uid}")
    st.session_state["css_mag_border_w"] = c2.slider("边框粗细", 1, 4, _c("mag_border_w"), key=f"mag_cp_bw_{uid}")
    st.session_state["css_mag_buy"] = c1.color_picker("买点", _c("mag_buy"), key=f"mag_cp_buy_{uid}")
    st.session_state["css_mag_sell"] = c2.color_picker("卖点", _c("mag_sell"), key=f"mag_cp_sell_{uid}")


def _render_color_controls_dash(uid):
    c1, c2, c3 = st.columns(3)
    st.caption("**数据仪表盘风**")
    c1.markdown("表头")
    st.session_state["css_dash_header_bg"] = c1.color_picker("背景", _c("dash_header_bg"), key=f"dash_cp_hbg_{uid}")
    st.session_state["css_dash_header_text"] = c2.color_picker("文字", _c("dash_header_text"), key=f"dash_cp_ht_{uid}")
    st.session_state["css_dash_header_border"] = c3.color_picker("下边框", _c("dash_header_border"), key=f"dash_cp_hb_{uid}")
    c1.markdown("数据行")
    st.session_state["css_dash_row_odd"] = c1.color_picker("奇数行", _c("dash_row_odd"), key=f"dash_cp_ro_{uid}")
    st.session_state["css_dash_row_even"] = c2.color_picker("偶数行", _c("dash_row_even"), key=f"dash_cp_re_{uid}")
    st.session_state["css_dash_row_hover"] = c3.color_picker("悬停", _c("dash_row_hover"), key=f"dash_cp_rh_{uid}")
    c1.markdown("单元格")
    st.session_state["css_dash_cell_border"] = c1.color_picker("竖线", _c("dash_cell_border"), key=f"dash_cp_cb_{uid}")
    st.session_state["css_dash_cell_text"] = c2.color_picker("文字", _c("dash_cell_text"), key=f"dash_cp_ct_{uid}")
    st.session_state["css_dash_border_w"] = c3.slider("边框粗细", 1, 4, _c("dash_border_w"), key=f"dash_cp_bw_{uid}")
    c1.markdown("涨跌 Badge")
    st.session_state["css_dash_badge_pos_bg"] = c1.color_picker("涨背景", _c("dash_badge_pos_bg"), key=f"dash_cp_bpb_{uid}")
    st.session_state["css_dash_badge_pos_text"] = c2.color_picker("涨文字", _c("dash_badge_pos_text"), key=f"dash_cp_bpt_{uid}")
    st.session_state["css_dash_badge_neg_bg"] = c1.color_picker("跌背景", _c("dash_badge_neg_bg"), key=f"dash_cp_bnb_{uid}")
    st.session_state["css_dash_badge_neg_text"] = c2.color_picker("跌文字", _c("dash_badge_neg_text"), key=f"dash_cp_bnt_{uid}")
    c1.markdown("特殊行 / 横隔")
    st.session_state["css_dash_special_bg"] = c1.color_picker("背景", _c("dash_special_bg"), key=f"dash_cp_sb_{uid}")
    st.session_state["css_dash_special_border"] = c2.color_picker("边框", _c("dash_special_border"), key=f"dash_cp_sbr_{uid}")
    st.session_state["css_dash_special_text"] = c3.color_picker("文字", _c("dash_special_text"), key=f"dash_cp_st_{uid}")
    st.session_state["css_dash_sep"] = c1.color_picker("横隔线", _c("dash_sep"), key=f"dash_cp_sep_{uid}")
    st.session_state["css_dash_buy"] = c2.color_picker("买点", _c("dash_buy"), key=f"dash_cp_buy_{uid}")
    st.session_state["css_dash_sell"] = c3.color_picker("卖点", _c("dash_sell"), key=f"dash_cp_sell_{uid}")


def _build_css_fin():
    bw = _c("fin_border_w")
    return f"""<style>
.finance-wrap {{ margin-top: 0.8rem; }}
.finance-table {{ width:100%; border-collapse:collapse; font-size:0.8rem; }}
.finance-table thead th {{
    background: {_c("fin_header_bg")}; color: {_c("fin_header_text")}; font-weight:700;
    padding:0.6rem 0.7rem; text-align:center; border:{bw}px solid {_c("fin_cell_border")};
    border-bottom:2px solid {_c("fin_header_border")}; white-space:nowrap; font-size:0.8rem; letter-spacing:0.5px;
}}
.finance-table tbody tr:nth-child(odd)  {{ background: {_c("fin_row_odd")}; }}
.finance-table tbody tr:nth-child(even) {{ background: {_c("fin_row_even")}; }}
.finance-table tbody tr:hover {{ background: {_c("fin_row_hover")} !important; }}
.finance-table td {{
    padding:0.5rem 0.7rem; text-align:center; border:{bw}px solid {_c("fin_cell_border")};
    white-space:nowrap; color: {_c("fin_cell_text")}; font-weight:600;
}}
.finance-table .badge-pos {{
    display:inline-block; padding:0.15rem 0.55rem; border-radius:4px;
    background: {_c("fin_badge_pos_bg")}; color: {_c("fin_badge_pos_text")}; font-weight:700; font-size:0.75rem;
}}
.finance-table .badge-neg {{
    display:inline-block; padding:0.15rem 0.55rem; border-radius:4px;
    background: {_c("fin_badge_neg_bg")}; color: {_c("fin_badge_neg_text")}; font-weight:700; font-size:0.75rem;
}}
.finance-table .badge-neu {{
    display:inline-block; padding:0.15rem 0.55rem; border-radius:4px;
    background: {_c("fin_badge_neu_bg")}; color: {_c("fin_badge_neu_text")}; font-weight:600; font-size:0.75rem;
}}
.finance-table tr.finance-special td {{
    background: {_c("fin_special_bg")} !important;
    border-left:{bw}px solid {_c("fin_special_border")};
    border-top:{bw}px solid {_c("fin_special_border")};
    border-bottom:{bw}px solid {_c("fin_special_border")};
    border-right:{bw}px solid {_c("fin_special_border")};
    color: {_c("fin_special_text")}; font-weight:700;
}}
.finance-table tr.finance-special td:last-child {{ border-right:none; }}
.finance-table .buy  {{ color:{_c("fin_buy")}; font-weight:700; }}
.finance-table .sell {{ color:{_c("fin_sell")}; font-weight:700; }}
</style>"""


def _build_css_mag():
    bw = _c("mag_border_w")
    return f"""<style>
.magazine-wrap {{ margin-top: 0.8rem; }}
.magazine-table {{ width:100%; border-collapse:collapse; font-size:0.88rem; }}
.magazine-table thead th {{
    background: transparent; color:{_c("mag_header_text")}; font-weight:500;
    padding:0.7rem 0.8rem 0.5rem 0.8rem; text-align:center; border:none;
    border-bottom:2px solid {_c("mag_header_border")}; white-space:nowrap; font-size:0.82rem; letter-spacing:1px;
}}
.magazine-table tbody tr {{ border-bottom:1px solid {_c("mag_row_border")}; }}
.magazine-table tbody tr:hover {{ background: {_c("mag_row_hover")}; }}
.magazine-table td {{
    padding:0.7rem 0.8rem; text-align:center; white-space:nowrap;
    color:{_c("mag_cell_text")}; font-weight:500;
}}
.magazine-table .col-name {{ text-align:left !important; font-weight:600; color:{_c("mag_name_text")}; }}
.magazine-table .text-pos {{ color:{_c("mag_text_pos")}; font-weight:600; }}
.magazine-table .text-neg {{ color:{_c("mag_text_neg")}; font-weight:600; }}
.magazine-table .text-neu {{ color:{_c("mag_text_neu")}; }}
.magazine-table tr.magazine-special {{ background: {_c("mag_special_bg")}; }}
.magazine-table tr.magazine-special td {{
    font-weight:600; color:{_c("mag_special_text")};
    border-top:{bw}px solid {_c("mag_special_border")};
    border-right:{bw}px solid #f0f0f0;
}}
.magazine-table tr.magazine-special td:last-child {{ border-right:none; }}
.magazine-table .buy  {{ color:{_c("mag_buy")}; font-weight:700; }}
.magazine-table .sell {{ color:{_c("mag_sell")}; font-weight:700; }}
</style>"""


def _build_css_dash():
    bw = _c("dash_border_w")
    return f"""<style>
.dashboard-wrap {{ margin-top: 0.8rem; }}
.dashboard-table {{ width:100%; border-collapse:collapse; font-size:0.78rem; }}
.dashboard-table thead th {{
    background: {_c("dash_header_bg")}; color: {_c("dash_header_text")}; font-weight:700;
    padding:0.6rem 0.7rem; text-align:center; border:{bw}px solid {_c("dash_cell_border")};
    border-bottom:2px solid {_c("dash_header_border")}; white-space:nowrap;
    font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;
}}
.dashboard-table tbody tr:nth-child(odd)  {{ background: {_c("dash_row_odd")}; }}
.dashboard-table tbody tr:nth-child(even) {{ background: {_c("dash_row_even")}; }}
.dashboard-table tbody tr:hover {{ background: {_c("dash_row_hover")} !important; }}
.dashboard-table td {{
    padding:0.5rem 0.7rem; text-align:center; white-space:nowrap;
    color: {_c("dash_cell_text")}; font-weight:600; border:{bw}px solid {_c("dash_cell_border")};
}}
.dashboard-table .badge-pos {{
    display:inline-block; padding:0.15rem 0.55rem; border-radius:4px;
    background: {_c("dash_badge_pos_bg")}; color: {_c("dash_badge_pos_text")}; font-weight:700; font-size:0.75rem;
}}
.dashboard-table .badge-neg {{
    display:inline-block; padding:0.15rem 0.55rem; border-radius:4px;
    background: {_c("dash_badge_neg_bg")}; color: {_c("dash_badge_neg_text")}; font-weight:700; font-size:0.75rem;
}}
.dashboard-table .badge-neu {{
    display:inline-block; padding:0.15rem 0.55rem; border-radius:4px;
    background: {_c("dash_badge_neu_bg")}; color: {_c("dash_badge_neu_text")}; font-weight:600; font-size:0.75rem;
}}
.dashboard-table .mini-bar-cell {{ min-width:130px; }}
.dashboard-table .mini-bar-track {{
    display:inline-block; width:70px; height:8px;
    background:#e8e8e8; border-radius:4px; overflow:hidden; vertical-align:middle;
}}
.dashboard-table .mini-bar-fill-pos {{ display:block; height:100%; border-radius:4px; background:linear-gradient(90deg,#ff7043,#ffab91); }}
.dashboard-table .mini-bar-fill-neg {{ display:block; height:100%; border-radius:4px; background:linear-gradient(90deg,#26a69a,#80cbc4); }}
.dashboard-table tr.dashboard-special td {{
    border-left:{bw}px solid {_c("dash_special_border")};
    border-right:{bw}px solid {_c("dash_special_border")};
    background: {_c("dash_special_bg")} !important;
    color: {_c("dash_special_text")} !important;
}}
.dashboard-table tr.dashboard-special td:last-child {{ border-right:none; }}
.dashboard-table .buy  {{ color:{_c("dash_buy")}; font-weight:700; }}
.dashboard-table .sell {{ color:{_c("dash_sell")}; font-weight:700; }}
</style>"""


def _export_table_png(html_body, css, filename_prefix="table"):
    """把 HTML 表格用 Playwright 截图导出为 PNG，提供下载按钮（Windows 兼容）"""
    full_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{css}</head>
<body style="margin:0;padding:16px;background:#fff;display:inline-block;">
{html_body}
</body></html>"""
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp.write(full_html)
    tmp.close()
    png_path = tmp.name.replace(".html", ".png")

    async def _shot():
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 900, "height": 600})
            await page.goto(f"file:///{tmp.name}")
            await page.wait_for_timeout(500)
            await page.screenshot(path=png_path, full_page=True)
            await browser.close()

    try:
        # Windows 需要 ProactorEventLoop 才能支持 subprocess
        if os.name == "nt":
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_shot())
            loop.close()
        else:
            asyncio.run(_shot())
        with open(png_path, "rb") as f:
            img_bytes = f.read()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        b64 = base64.b64encode(img_bytes).decode()
        st.markdown(
            f'<a href="data:image/png;base64,{b64}" download="{filename_prefix}_{ts}.png" '
            f'style="display:inline-block;padding:0.3rem 0.8rem;background:#1565c0;color:#fff;'
            f'border-radius:4px;text-decoration:none;font-size:0.82rem;">📥 下载 PNG</a>',
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"导出失败：{e}")
    finally:
        os.unlink(tmp.name)
        if os.path.exists(png_path):
            os.unlink(png_path)


def _pct(v):
    """百分比，红涨绿跌"""
    if v is None:
        return "—"
    color = '#EF5350' if v > 0 else ('#66BB6A' if v < 0 else '#BDBDBD')
    sign = "+" if v > 0 else ""
    return f'<span style="color:{color};font-weight:600;">{sign}{v:.2f}%</span>'


def _iy(v):
    """亿整数"""
    if v is None or v == 0:
        return "—"
    return f"{v:,.0f}"


# ETF code 集合（价格需要3位小数）
_ETF_CODES = {"511880", "510310"}


def _price(v, exchange="", code=""):
    """
    股价格式化：
    - 港股(HK)：3位小数
    - ETF(银华日利511880/沪深300ETF510310)：3位小数
    - A股/SZ/SH股票：2位小数
    """
    if v is None or v == 0:
        return "—"
    if exchange == "HK" or code in _ETF_CODES:
        return f"{v:,.3f}"
    return f"{v:,.2f}"


def _nav(v):
    """净值/指数价格：四舍五入到3位小数（标准ROUND_HALF_UP）"""
    if v is None or v == 0:
        return "—"
    from decimal import Decimal, ROUND_HALF_UP
    d = Decimal(str(v)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    return f"{d:.3f}"


def _nav4(v):
    """净值：编辑4位小数"""
    if v is None or v == 0:
        return "—"
    return f"{v:.4f}"


def _int(v):
    """整数"""
    if v is None or v == 0:
        return "—"
    return f"{int(v):,}"


def _fmt_years(v):
    if isinstance(v, float) and v != int(v):
        return f"{v:.2f}"
    return str(int(v)) if v else "—"


# ════════════════════════════════════════════
# 周记 Tab
# ════════════════════════════════════════════
def _check_xueqiu_cookie() -> bool:
    """检查雪球 Cookie 是否有效，无效时显示 UI 提示"""
    import requests as _req
    cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "XueQiuCookie.txt")
    try:
        with open(cookie_path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            if raw.startswith("cookie="):
                raw = raw[len("cookie="):]
    except Exception:
        return False
    if not raw:
        return False
    try:
        resp = _req.get(
            "https://stock.xueqiu.com/v5/stock/f10/cn/company.json",
            params={"symbol": "SH600519"},
            headers={"Cookie": raw, "User-Agent": "Mozilla/5.0", "Referer": "https://xueqiu.com/"},
            timeout=5,
        )
        data = resp.json()
        error_code = data.get("error_code")
        if error_code == "400016":
            return False
        return "error_code" not in data or error_code == 0
    except Exception:
        return False

def render_weekly():
    st.markdown(CSS, unsafe_allow_html=True)

    col_t, col_b = st.columns([6, 1])
    with col_t:
        st.markdown("### 📝 投资周记")
    with col_b:
        if st.button("🔄 刷新", key="ref_w"):
            st.session_state["_pf_dirty"] = True
            st.rerun()

    # ── 雪球 Cookie 检测（仅入口调用一次）──
    if not _check_xueqiu_cookie():
        st.warning("⚠️ **雪球 Cookie 已过期**，实时行情（市值/股价/涨幅）无法获取。\n\n"
                    "**更新方法：** 打开 https://xueqiu.com → F12 Network → 随便点一个请求 → "
                    "复制 Cookie 中的 `xq_a_token` 值 → 更新 `config/XueQiuCookie.txt` → 点击刷新")

    dirty = st.session_state.get("_pf_dirty", False)
    if "_pf_weekly" not in st.session_state or dirty:
        with st.spinner("获取实时行情..."):
            st.session_state["_pf_weekly"] = get_weekly_data()
            st.session_state["_pf_dirty"] = False
    data = st.session_state["_pf_weekly"]

    rows = data.get("rows", [])
    special_rows = data.get("special_rows", [])
    summary = data.get("summary", {})

    if not rows and not special_rows:
        st.info("暂无持仓数据")
        return

    # ── 编辑面板 ──
    with st.expander("✏️ 编辑数据", expanded=False):
        _render_edit_panel(rows, special_rows)

    # ── 主表格 ──
    total_mv = summary.get("total_market_value", 0)
    pf = load_portfolio()
    manual_pcts = {}
    for h in pf.get("holdings", []):
        w = h.get("weight", 0)
        if w > 0 and isinstance(w, (int, float)) and w <= 100:
            manual_pcts[h["name"]] = w

    html_parts = [
        '<div class="table-wrapper">',
        '<table class="pf-table">',
        '<thead><tr>',
        '<th>持股名称</th><th>持股比例</th><th>当前市值</th>',
        '<th>理想买点</th><th>年内卖点</th><th>当前股价</th><th>年内涨幅</th>',
        '</tr></thead>',
        '<tbody>',
    ]

    for r in rows:
        # 优先使用手动设置的持股比例
        pct_val = manual_pcts.get(r["name"])
        if pct_val is None:
            pct_val = (r["market_value"] / total_mv * 100) if total_mv else 0

        buy_val = _int(r["buy_point"])
        sell_val = _int(r["sell_point"])
        buy_cls = ' class="buy"' if r["buy_point"] > 0 else ""
        sell_cls = ' class="sell"' if r["sell_point"] > 0 else ""

        html_parts.append(
            f'<tr>'
            f'<td style="text-align:left;font-weight:600;">{r["name"]}</td>'
            f'<td>{pct_val:.0f}%</td>'
            f'<td>{_iy(r["market_value"])}</td>'
            f'<td><span{buy_cls}>{buy_val}</span></td>'
            f'<td><span{sell_cls}>{sell_val}</span></td>'
            f'<td>{_price(r["current_price"], r.get("exchange", ""), r.get("code", ""))}</td>'
            f'<td>{_pct(r["year_chg"])}</td>'
            f'</tr>'
        )

    # 分隔行
    if special_rows and rows:
        html_parts.append(
            '<tr class="tr-sep"><td colspan="7" style="border-top:1px solid #ccc;padding:0;"></td></tr>'
        )

    # 特殊行 — 按用户要求的精确列布局
    for sr in special_rows:
        stype = sr.get("special_type", "")
        c1_val = sr.get("col1_value")  # 周涨幅数值
        c2_val = sr.get("col2_value")  # 净值/指数价格
        c3_val = sr.get("col3_value")  # 年内涨幅

        pct_html = _pct(c1_val) if c1_val is not None else "—"
        nav_html = _nav(c2_val) if c2_val is not None else ""
        year_html = _pct(c3_val) if c3_val is not None else "—"

        if stype == "nav":
            # 实盘净值行：
            # 第1列=名称 | 第2-3列合并=基金净值法(靠左) | 第4列=周涨幅文字 | 第5列=涨幅数字(无框线) | 第6列=净值 | 第7列=年内涨幅
            html_parts.append(
                '<tr class="tr-special">'
                f'<td style="text-align:left;font-weight:600;">实盘净值</td>'
                f'<td colspan="2" style="text-align:left;font-size:0.78rem;color:#999;padding-left:0.6rem;">基金净值法</td>'
                f'<td style="border-right:none;font-size:0.78rem;color:#999;">周涨幅</td>'
                f'<td style="border-left:none;">{pct_html}</td>'
                f'<td>{nav_html}</td>'
                f'<td>{year_html}</td>'
                '</tr>'
            )
        elif stype == "index":
            # 沪深300行：
            # 第1列=对比基准 | 第2-3列合并=沪深300指数基金 510310(靠左) | 第4-5列=周涨幅 | 第6列=价格 | 第7列=年内涨幅
            html_parts.append(
                '<tr class="tr-special">'
                f'<td style="text-align:left;font-weight:600;">对比基准</td>'
                f'<td colspan="2" style="text-align:left;font-size:0.78rem;color:#999;padding-left:0.6rem;">沪深300指数基金 510310</td>'
                f'<td style="border-right:none;font-size:0.78rem;color:#999;">周涨幅</td>'
                f'<td style="border-left:none;">{pct_html}</td>'
                f'<td>{nav_html}</td>'
                f'<td>{year_html}</td>'
                '</tr>'
            )
        elif stype == "fx":
            # 日期行：
            # 第1列=日期 | 第2-3列合并=市值亿元，腾讯古B股价为港币(靠左) | 第4-5列合并=港币汇率(靠右) | 第6列=汇率值 | 第7列=年内涨幅
            date_str = sr.get("label", "")
            fx_val = f"{c1_val:.4f}" if c1_val is not None else "—"
            html_parts.append(
                '<tr class="tr-special">'
                f'<td style="text-align:left;font-weight:600;">{date_str}</td>'
                f'<td colspan="2" style="text-align:left;font-size:0.78rem;color:#999;padding-left:0.6rem;">市值亿元，腾讯古B股价为港币</td>'
                f'<td colspan="2" style="text-align:right;font-size:0.78rem;color:#999;">港币汇率</td>'
                f'<td>{fx_val}</td>'
                f'<td>{year_html}</td>'
                '</tr>'
            )

    html_parts.append('</tbody></table></div>')
    st.markdown("\n".join(html_parts), unsafe_allow_html=True)

    # ── 文章用表格（三种风格切换）──
    _render_article_table_selector(rows, special_rows, total_mv, manual_pcts)

    # ── 数据概览（文章用）──
    _render_article_section(rows, special_rows, total_mv, manual_pcts)


def _render_edit_panel(rows, special_rows):
    """编辑面板 — 内部分三块折叠区域"""
    pf = load_portfolio()
    holdings_map = {h["name"]: h for h in pf.get("holdings", [])}

    # ── 持仓设置（可折叠）──
    with st.expander("📊 持仓设置 — 持股比例 / 买点 / 卖点", expanded=True):
        cols = st.columns([2, 1, 1, 1])
        cols[0].markdown("**股票**")
        cols[1].markdown("**持股比例 %**")
        cols[2].markdown("**理想买点 亿**")
        cols[3].markdown("**年内卖点 亿**")

        for r in rows:
            h = holdings_map.get(r["name"])
            if not h:
                continue

            cur_pct = h.get("weight", 0)
            if not isinstance(cur_pct, (int, float)) or cur_pct > 100 or cur_pct < 0:
                cur_pct = 0

            cols = st.columns([2, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**{r['name']}**")
                st.caption(f"现价 {_price(r['current_price'], r.get('exchange', ''), r.get('code', ''))} · 市值 {_iy(r['market_value'])}亿")
            with cols[1]:
                st.number_input("持股比例%", min_value=0, max_value=100,
                                value=int(cur_pct), step=1,
                                key=f"pct_{r['name']}", label_visibility="collapsed")
            with cols[2]:
                st.number_input("理想买点(亿)", min_value=0, step=100,
                                value=int(h.get("buy_point", 0)),
                                key=f"buy_{r['name']}", label_visibility="collapsed")
            with cols[3]:
                st.number_input("年内卖点(亿)", min_value=0, step=100,
                                value=int(h.get("sell_point", 0)),
                                key=f"sell_{r['name']}", label_visibility="collapsed")

    # ── 实盘净值（可折叠）──
    for sr in special_rows:
        if sr.get("special_type") == "nav":
            nav_h = None
            for h in pf.get("holdings", []):
                if h.get("category") == "实盘":
                    nav_h = h
                    break

            if nav_h:
                with st.expander("💰 实盘净值 — 基金净值法（4位小数）", expanded=False):
                    nc = st.columns(3)
                    with nc[0]:
                        st.markdown("**当前净值**")
                        st.number_input("当前净值", min_value=0.0, max_value=10.0,
                                        value=float(nav_h.get("current_price", 1.0)),
                                        step=0.0001, format="%.4f",
                                        key="edit_nav_current", label_visibility="collapsed")
                    with nc[1]:
                        st.markdown("**上周净值**")
                        st.number_input("上周净值", min_value=0.0, max_value=10.0,
                                        value=float(nav_h.get("last_week_price", 1.0)),
                                        step=0.0001, format="%.4f",
                                        key="edit_nav_last", label_visibility="collapsed")
                    with nc[2]:
                        st.markdown("**年初净值**")
                        st.number_input("年初净值", min_value=0.0, max_value=10.0,
                                        value=float(nav_h.get("year_start_price", 1.0)),
                                        step=0.0001, format="%.4f",
                                        key="edit_nav_year", label_visibility="collapsed")

    # ── 汇率设置（可折叠）──
    for h in pf.get("holdings", []):
        if h.get("code") == "HKDCNY":
            fx_cur_display = 0.0
            for sr in special_rows:
                if sr.get("special_type") == "fx":
                    fx_cur_display = sr.get("col1_value", 0.0) or 0.0
                    break

            with st.expander("💱 港币汇率设置 — 手动设置年初汇率", expanded=False):
                st.caption("年内涨跌幅依赖年初汇率，请手动设置以确保准确")
                nc = st.columns(2)
                with nc[0]:
                    st.markdown("**年初汇率**")
                    st.number_input("年初汇率", min_value=0.0, max_value=2.0,
                                    value=float(h.get("year_start_price", 0.92)),
                                    step=0.0001, format="%.4f",
                                    key="edit_fx_year_start", label_visibility="collapsed",
                                    help="年初汇率（如 0.9200），用于计算年内涨跌幅")
                with nc[1]:
                    st.markdown("**当前汇率（自动）**")
                    st.markdown(f"`{fx_cur_display:.4f}`" if fx_cur_display else "`—`")
                    st.caption("来自腾讯行情，实时数据")
            break

    # ── 保存按钮（始终可见）──
    st.markdown("")
    if st.button("💾 保存所有修改", key="save_all", type="primary", width='stretch'):
        _save_edits_to_json(rows)
        st.session_state["_pf_dirty"] = True
        st.success("✅ 已保存！页面即将刷新...")
        st.rerun()


def _save_edits_to_json(rows):
    """保存编辑到 portfolio.json"""
    pf = load_portfolio()
    holdings_map = {h["name"]: h for h in pf.get("holdings", [])}

    for r in rows:
        h = holdings_map.get(r["name"])
        if not h:
            continue
        if f"buy_{r['name']}" in st.session_state:
            h["buy_point"] = int(st.session_state[f"buy_{r['name']}"])
        if f"sell_{r['name']}" in st.session_state:
            h["sell_point"] = int(st.session_state[f"sell_{r['name']}"])
        if f"pct_{r['name']}" in st.session_state:
            h["weight"] = int(st.session_state[f"pct_{r['name']}"])

    for h in pf.get("holdings", []):
        if h.get("category") == "实盘":
            if "edit_nav_current" in st.session_state:
                h["current_price"] = round(st.session_state["edit_nav_current"], 4)
            if "edit_nav_last" in st.session_state:
                h["last_week_price"] = round(st.session_state["edit_nav_last"], 4)
            if "edit_nav_year" in st.session_state:
                h["year_start_price"] = round(st.session_state["edit_nav_year"], 4)
            break


    # 保存汇率年初值
    for h in pf.get("holdings", []):
        if h.get("code") == "HKDCNY":
            if "edit_fx_year_start" in st.session_state:
                h["year_start_price"] = round(st.session_state["edit_fx_year_start"], 4)
            break

    save_portfolio(pf)


def _render_article_section(rows, special_rows, total_mv, manual_pcts):
    """文章展示区 — Wind/同花顺风格专业财经卡片"""
    # 同步更新 manual_pcts（从最新 JSON 读）
    pf2 = load_portfolio()
    for h in pf2.get("holdings", []):
        w = h.get("weight", 0)
        if w > 0 and isinstance(w, (int, float)) and w <= 100:
            manual_pcts[h["name"]] = w

    st.markdown("---")
    st.markdown("### 📋 数据概览（文章用）")

    # ── 持仓组合卡片 ──
    st.markdown('<div class="article-section">', unsafe_allow_html=True)

    n_cols = min(len(rows), 3)
    for i in range(0, len(rows), n_cols):
        chunk = rows[i:i + n_cols]
        cols = st.columns(len(chunk))
        for j, r in enumerate(chunk):
            pct_val = manual_pcts.get(r["name"])
            if pct_val is None:
                pct_val = (r["market_value"] / total_mv * 100) if total_mv else 0
            yc = r["year_chg"]
            year_color = "#EF5350" if yc > 0 else ("#66BB6A" if yc < 0 else "#BDBDBD")
            sign = "+" if yc > 0 else ""

            # 计算买点/卖点进度条
            buy_pt = r["buy_point"]
            sell_pt = r["sell_point"]
            cur = r["current_price"]
            if buy_pt > 0 and sell_pt > buy_pt:
                # 当前价在买点下方=绿色(低估)，在卖点上方=红色(高估)
                rng = sell_pt - buy_pt
                if cur <= buy_pt:
                    buy_pct = 100
                    sell_pct = 0
                    zone = "below_buy"
                    zone_label = "低于买点"
                    zone_color = "#66BB6A"
                elif cur >= sell_pt:
                    buy_pct = 100
                    sell_pct = 100
                    zone = "above_sell"
                    zone_label = "高于卖点"
                    zone_color = "#EF5350"
                else:
                    buy_pct = (cur - buy_pt) / rng * 100
                    sell_pct = buy_pct
                    zone = "between"
                    zone_label = "持有区间"
                    zone_color = "#FFB74D"
            else:
                buy_pct = 0
                sell_pct = 0
                zone = ""
                zone_label = ""
                zone_color = "#BDBDBD"

            with cols[j]:
                # 专业财经卡片：大数字 + 关键指标 + 进度条
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(128,128,128,0.06),rgba(128,128,128,0.12));border-radius:10px;padding:1rem 0.9rem;border-top:3px solid {year_color};position:relative;overflow:hidden;">
                    <!-- 名称 + 仓位 -->
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
                        <span style="font-size:0.85rem;font-weight:700;">{r['name']}</span>
                        <span style="font-size:0.7rem;background:rgba(128,128,128,0.15);padding:0.1rem 0.4rem;border-radius:4px;">{pct_val:.0f}%仓位</span>
                    </div>
                    <!-- 大数字：当前价 -->
                    <div style="font-size:1.6rem;font-weight:800;letter-spacing:-0.5px;">{_price(cur, r.get('exchange', ''), r.get('code', ''))}</div>
                    <!-- 年内涨幅 badge -->
                    <div style="display:flex;align-items:center;gap:0.4rem;margin:0.3rem 0 0.5rem 0;">
                        <span style="background:{year_color}22;color:{year_color};font-size:0.75rem;font-weight:600;padding:0.1rem 0.5rem;border-radius:4px;">{sign}{yc:.2f}%</span>
                        <span style="font-size:0.65rem;color:#888;">年内涨幅</span>
                    </div>
                    <!-- 买点/卖点进度 -->
                    <div style="margin-top:0.3rem;">
                        <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#999;margin-bottom:0.15rem;">
                            <span>买点 {_int(buy_pt)}</span>
                            <span style="color:{zone_color};font-weight:600;">{zone_label}</span>
                            <span>卖点 {_int(sell_pt)}</span>
                        </div>
                        <div style="background:rgba(128,128,128,0.15);border-radius:3px;height:5px;overflow:hidden;position:relative;">
                            <div style="width:{min(buy_pct,100)}%;height:100%;background:linear-gradient(90deg,#66BB6A,#FFB74D);border-radius:3px;"></div>
                        </div>
                    </div>
                    <!-- 市值 -->
                    <div style="font-size:0.65rem;color:#888;margin-top:0.35rem;">市值 {_iy(r['market_value'])}亿</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 净值与基准卡片 ──
    if special_rows:
        st.markdown('<div class="article-section" style="margin-top:0.8rem;">', unsafe_allow_html=True)

        cols = st.columns(len(special_rows))
        for i, sr in enumerate(special_rows):
            stype = sr.get("special_type", "")
            c1 = _pct(sr["col1_value"]) if sr.get("col1_value") is not None else "—"
            c2 = _nav(sr["col2_value"]) if sr.get("col2_value") is not None else "—"
            c3 = _pct(sr["col3_value"]) if sr.get("col3_value") is not None else "—"

            # 根据类型选主题色
            if stype == "nav":
                accent = "#42A5F5"
                icon = "💰"
            elif stype == "index":
                accent = "#AB47BC"
                icon = "📊"
            else:
                accent = "#FFA726"
                icon = "💱"

            with cols[i]:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(128,128,128,0.06),rgba(128,128,128,0.12));border-radius:10px;padding:1rem 0.9rem;border-left:4px solid {accent};">
                    <div style="font-size:0.75rem;color:#999;margin-bottom:0.3rem;">{icon} {sr['label']}</div>
                    <div style="font-size:1.5rem;font-weight:800;margin:0.2rem 0;">{c2}</div>
                    <div style="display:flex;gap:0.8rem;margin-top:0.4rem;">
                        <div>
                            <div style="font-size:0.65rem;color:#888;">{sr.get('col1_label','')}</div>
                            <div style="font-size:0.8rem;font-weight:600;">{c1}</div>
                        </div>
                        <div>
                            <div style="font-size:0.65rem;color:#888;">{sr.get('col3_label','')}</div>
                            <div style="font-size:0.8rem;font-weight:600;">{c3}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════
# 文章用表格 — 风格选择器
# ════════════════════════════════════════════
def _render_article_table_selector(rows, special_rows, total_mv, manual_pcts):
    """文章用表格风格选择器，三种风格切换 + 自定义颜色"""
    st.markdown("---")
    st.markdown("### 📊 文章用表格")

    # 同步最新权重
    pf2 = load_portfolio()
    for h in pf2.get("holdings", []):
        w = h.get("weight", 0)
        if w > 0 and isinstance(w, (int, float)) and w <= 100:
            manual_pcts[h["name"]] = w

    style = st.radio(
        "选择表格风格",
        ["🏦 专业财经风", "📰 极简杂志风", "🖥️ 数据仪表盘风"],
        horizontal=True,
        key="article_table_style",
        label_visibility="collapsed",
    )

    # 自定义颜色面板
    style_key = {"🏦 专业财经风": "fin", "📰 极简杂志风": "mag", "🖥️ 数据仪表盘风": "dash"}[style]
    _render_color_panel(style_key)

    if style == "🏦 专业财经风":
        _render_table_finance(rows, special_rows, total_mv, manual_pcts)
    elif style == "📰 极简杂志风":
        _render_table_magazine(rows, special_rows, total_mv, manual_pcts)
    elif style == "🖥️ 数据仪表盘风":
        _render_table_dashboard(rows, special_rows, total_mv, manual_pcts)


def _render_annual_table_selector(rows):
    """年化收益文章用表格风格选择器 + 自定义颜色"""
    st.markdown("---")
    st.markdown("### 📊 文章用表格（年化收益）")

    style = st.radio(
        "选择表格风格",
        ["🏦 专业财经风", "📰 极简杂志风", "🖥️ 数据仪表盘风"],
        horizontal=True,
        key="annual_table_style",
        label_visibility="collapsed",
    )

    style_key = {"🏦 专业财经风": "fin", "📰 极简杂志风": "mag", "🖥️ 数据仪表盘风": "dash"}[style]
    _render_color_panel(style_key)

    if style == "🏦 专业财经风":
        _render_annual_table_finance(rows)
    elif style == "📰 极简杂志风":
        _render_annual_table_magazine(rows)
    elif style == "🖥️ 数据仪表盘风":
        _render_annual_table_dashboard(rows)


# ── 辅助：涨跌 badge 财经风 ──
def _badge(v):
    if v is None:
        return '<span class="badge-neu">—</span>'
    if v > 0:
        return f'<span class="badge-pos">+{v:.2f}%</span>'
    if v < 0:
        return f'<span class="badge-neg">{v:.2f}%</span>'
    return '<span class="badge-neu">0.00%</span>'


def _badge_d(v):
    """仪表盘风 badge"""
    if v is None:
        return '<span class="badge-neu">—</span>'
    if v > 0:
        return f'<span class="badge-pos">+{v:.2f}%</span>'
    if v < 0:
        return f'<span class="badge-neg">{v:.2f}%</span>'
    return '<span class="badge-neu">0.00%</span>'


def _text_pct(v):
    """杂志风纯文字涨跌"""
    if v is None:
        return '<span class="text-neu">—</span>'
    if v > 0:
        return f'<span class="text-pos">+{v:.2f}%</span>'
    if v < 0:
        return f'<span class="text-neg">{v:.2f}%</span>'
    return '<span class="text-neu">0.00%</span>'


def _mini_bar(v, cls_prefix=""):
    """仪表盘风迷你柱状图"""
    if v is None or v == 0:
        return '<span style="color:#8b949e;font-size:0.7rem;">—</span>'
    pct = min(abs(v) / 30 * 100, 100)
    sign = "+" if v > 0 else ""
    if v > 0:
        return (
            f'<span class="{cls_prefix}mini-bar-track">'
            f'<span class="{cls_prefix}mini-bar-fill-pos" style="width:{pct}%;"></span>'
            f'</span>'
            f'<span class="{cls_prefix}mini-bar-label badge-pos">{sign}{v:.2f}%</span>'
        )
    else:
        return (
            f'<span class="{cls_prefix}mini-bar-track">'
            f'<span class="{cls_prefix}mini-bar-fill-neg" style="width:{pct}%;"></span>'
            f'</span>'
            f'<span class="{cls_prefix}mini-bar-label badge-neg">{v:.2f}%</span>'
        )


def _build_stock_rows_html(rows, total_mv, manual_pcts, tbl_cls, name_cls=""):
    """构建普通股票行 HTML（三种风格共用逻辑，className 不同）"""
    parts = []
    for r in rows:
        pct_val = manual_pcts.get(r["name"])
        if pct_val is None:
            pct_val = (r["market_value"] / total_mv * 100) if total_mv else 0
        buy_val = _int(r["buy_point"])
        sell_val = _int(r["sell_point"])
        exchange = r.get("exchange", "")
        code = r.get("code", "")

        # 年内涨幅列 — 三种风格不同渲染
        yc = r["year_chg"]
        if tbl_cls == "finance-table":
            year_col = f'<td>{_badge(yc)}</td>'
        elif tbl_cls == "dashboard-table":
            year_col = f'<td class="mini-bar-cell">{_mini_bar(yc)}</td>'
        else:  # magazine
            year_col = f'<td>{_text_pct(yc)}</td>'

        name_td = f'<td class="{name_cls}">{r["name"]}</td>' if name_cls else f'<td>{r["name"]}</td>'

        parts.append(
            f'<tr>'
            f'{name_td}'
            f'<td>{pct_val:.0f}%</td>'
            f'<td>{_iy(r["market_value"])}</td>'
            f'<td class="buy">{buy_val}</td>'
            f'<td class="sell">{sell_val}</td>'
            f'<td>{_price(r["current_price"], exchange, code)}</td>'
            f'{year_col}'
            f'</tr>'
        )
    return parts


def _build_special_rows_html(special_rows, tbl_cls, special_cls):
    """构建特殊行 HTML（三种风格共用逻辑）"""
    parts = []
    for sr in special_rows:
        stype = sr.get("special_type", "")
        c1_val = sr.get("col1_value")
        c2_val = sr.get("col2_value")
        c3_val = sr.get("col3_value")

        # 周涨幅 / 数值
        if tbl_cls == "finance-table":
            pct_html = _badge(c1_val)
            year_html = _badge(c3_val)
        elif tbl_cls == "dashboard-table":
            pct_html = _badge_d(c1_val)
            year_html = _badge_d(c3_val)
        else:
            pct_html = _text_pct(c1_val)
            year_html = _text_pct(c3_val)

        nav_html = _nav(c2_val) if c2_val is not None else ""
        c2_display = nav_html

        if stype == "nav":
            left_accents = {
                "finance-table": "",
                "magazine-table": "",
                "dashboard-table": "border-left-color:#42A5F5;",
            }
            la = left_accents.get(tbl_cls, "")
            parts.append(
                f'<tr class="{special_cls}" style="{la}">'
                f'<td>实盘净值</td>'
                f'<td colspan="2" style="text-align:left;font-size:0.76rem;color:#999;padding-left:0.6rem;">基金净值法</td>'
                f'<td style="border-right:none;font-size:0.76rem;color:#999;">周涨幅</td>'
                f'<td style="border-left:none;">{pct_html}</td>'
                f'<td>{c2_display}</td>'
                f'<td>{year_html}</td>'
                '</tr>'
            )
        elif stype == "index":
            la = "border-left-color:#AB47BC;" if tbl_cls == "dashboard-table" else ""
            parts.append(
                f'<tr class="{special_cls}" style="{la}">'
                f'<td>对比基准</td>'
                f'<td colspan="2" style="text-align:left;font-size:0.76rem;color:#999;padding-left:0.6rem;">沪深300指数基金 510310</td>'
                f'<td style="border-right:none;font-size:0.76rem;color:#999;">周涨幅</td>'
                f'<td style="border-left:none;">{pct_html}</td>'
                f'<td>{c2_display}</td>'
                f'<td>{year_html}</td>'
                '</tr>'
            )
        elif stype == "fx":
            la = "border-left-color:#FFA726;" if tbl_cls == "dashboard-table" else ""
            date_str = sr.get("label", "")
            fx_val = f"{c1_val:.4f}" if c1_val is not None else "—"
            # 汇率行：col1=港币汇率值, col2=空, col3=年内涨幅
            # 但汇率的 c1 是汇率值本身，不是涨幅
            parts.append(
                f'<tr class="{special_cls}" style="{la}">'
                f'<td>{date_str}</td>'
                f'<td colspan="2" style="text-align:left;font-size:0.76rem;color:#999;padding-left:0.6rem;">市值亿元，腾讯古B股价为港币</td>'
                f'<td colspan="2" style="text-align:right;font-size:0.76rem;color:#999;">港币汇率</td>'
                f'<td>{fx_val}</td>'
                f'<td>{year_html}</td>'
                '</tr>'
            )
    return parts


# ── 财经风周记表格 ──
def _render_table_finance(rows, special_rows, total_mv, manual_pcts):
    st.markdown(_build_css_fin(), unsafe_allow_html=True)
    html = [
        '<div class="finance-wrap" id="export-table">',
        '<table class="finance-table">',
        '<thead><tr>',
        '<th>持股名称</th><th>持股比例</th><th>当前市值</th>',
        '<th>理想买点</th><th>年内卖点</th><th>当前股价</th><th>年内涨幅</th>',
        '</tr></thead>',
        '<tbody>',
    ]
    html += _build_stock_rows_html(rows, total_mv, manual_pcts, "finance-table")
    if special_rows and rows:
        html.append(
            '<tr style="height:1px;padding:0;background:#ffb300;">'
            '<td colspan="7" style="padding:0;border:none;line-height:1px;">&nbsp;</td></tr>'
        )
    html += _build_special_rows_html(special_rows, "finance-table", "finance-special")
    html.append('</tbody></table></div>')
    st.markdown("\n".join(html), unsafe_allow_html=True)
    # 导出按钮
    table_html = "\n".join(html)
    cols = st.columns([1, 6])
    with cols[0]:
        if st.button("📥 导出", key="dl_finance"):
            _export_table_png(table_html, _build_css_fin(), "财经风表格")


# ── 杂志风周记表格 ──
def _render_table_magazine(rows, special_rows, total_mv, manual_pcts):
    st.markdown(_build_css_mag(), unsafe_allow_html=True)
    html = [
        '<div class="magazine-wrap" id="export-table">',
        '<table class="magazine-table">',
        '<thead><tr>',
        '<th>持股名称</th><th>持股比例</th><th>当前市值</th>',
        '<th>理想买点</th><th>年内卖点</th><th>当前股价</th><th>年内涨幅</th>',
        '</tr></thead>',
        '<tbody>',
    ]
    html += _build_stock_rows_html(rows, total_mv, manual_pcts, "magazine-table", "col-name")
    if special_rows and rows:
        html.append(
            '<tr style="height:1px;padding:0;background:#ddd;">'
            '<td colspan="7" style="padding:0;border:none;line-height:1px;">&nbsp;</td></tr>'
        )
    html += _build_special_rows_html(special_rows, "magazine-table", "magazine-special")
    html.append('</tbody></table></div>')
    st.markdown("\n".join(html), unsafe_allow_html=True)
    table_html = "\n".join(html)
    cols = st.columns([1, 6])
    with cols[0]:
        if st.button("📥 导出", key="dl_magazine"):
            _export_table_png(table_html, _build_css_mag(), "杂志风表格")


# ── 仪表盘风周记表格 ──
def _render_table_dashboard(rows, special_rows, total_mv, manual_pcts):
    st.markdown(_build_css_dash(), unsafe_allow_html=True)
    html = [
        '<div class="dashboard-wrap" id="export-table">',
        '<table class="dashboard-table">',
        '<thead><tr>',
        '<th>持股名称</th><th>持股比例</th><th>当前市值</th>',
        '<th>理想买点</th><th>年内卖点</th><th>当前股价</th><th>年内涨幅</th>',
        '</tr></thead>',
        '<tbody>',
    ]
    html += _build_stock_rows_html(rows, total_mv, manual_pcts, "dashboard-table")
    if special_rows and rows:
        html.append(
            '<tr style="height:1px;padding:0;background:#90caf9;">'
            '<td colspan="7" style="padding:0;border:none;line-height:1px;">&nbsp;</td></tr>'
        )
    html += _build_special_rows_html(special_rows, "dashboard-table", "dashboard-special")
    html.append('</tbody></table></div>')
    st.markdown("\n".join(html), unsafe_allow_html=True)
    table_html = "\n".join(html)
    cols = st.columns([1, 6])
    with cols[0]:
        if st.button("📥 导出", key="dl_dashboard"):
            _export_table_png(table_html, _build_css_dash(), "仪表盘风表格")


# ── 年化收益表格 — 财经风 ──
def _render_annual_table_finance(rows):
    st.markdown(_build_css_fin(), unsafe_allow_html=True)
    html = [
        '<div class="finance-wrap" id="export-table">',
        '<table class="finance-table">',
        '<thead><tr>',
        '<th>年份</th><th>实盘年限</th><th>实盘当年涨幅</th><th>实盘净值</th>',
        '<th>实盘年化</th><th>指数当年涨幅</th><th>指数价格</th><th>指数年化</th>',
        '</tr></thead>',
        '<tbody>',
    ]
    for r in rows:
        rr = r["real_return"]
        ra = r["real_annualized"]
        ir = r["index_return"]
        ia = r["index_annualized"]
        html.append(
            f'<tr>'
            f'<td style="font-weight:600;">{r["year"]}</td>'
            f'<td>{_fmt_years(r["real_years"])}</td>'
            f'<td>{_badge(rr * 100) if isinstance(rr, (int, float)) else "—"}</td>'
            f'<td>{_nav(r["real_nav"])}</td>'
            f'<td>{_badge(ra * 100) if isinstance(ra, (int, float)) else "—"}</td>'
            f'<td>{_badge(ir * 100) if isinstance(ir, (int, float)) else "—"}</td>'
            f'<td>{_nav(r["index_price"])}</td>'
            f'<td>{_badge(ia * 100) if isinstance(ia, (int, float)) else "—"}</td>'
            f'</tr>'
        )
    html.append('</tbody></table></div>')
    st.markdown("\n".join(html), unsafe_allow_html=True)
    table_html = "\n".join(html)
    cols = st.columns([1, 7])
    with cols[0]:
        if st.button("📥 导出", key="dl_annual_finance"):
            _export_table_png(table_html, _build_css_fin(), "年化收益_财经风")


# ── 年化收益表格 — 杂志风 ──
def _render_annual_table_magazine(rows):
    st.markdown(_build_css_mag(), unsafe_allow_html=True)
    html = [
        '<div class="magazine-wrap" id="export-table">',
        '<table class="magazine-table">',
        '<thead><tr>',
        '<th>年份</th><th>实盘年限</th><th>实盘当年涨幅</th><th>实盘净值</th>',
        '<th>实盘年化</th><th>指数当年涨幅</th><th>指数价格</th><th>指数年化</th>',
        '</tr></thead>',
        '<tbody>',
    ]
    for r in rows:
        rr = r["real_return"]
        ra = r["real_annualized"]
        ir = r["index_return"]
        ia = r["index_annualized"]
        html.append(
            f'<tr>'
            f'<td style="font-weight:600;">{r["year"]}</td>'
            f'<td>{_fmt_years(r["real_years"])}</td>'
            f'<td>{_text_pct(rr * 100) if isinstance(rr, (int, float)) else "—"}</td>'
            f'<td>{_nav(r["real_nav"])}</td>'
            f'<td>{_text_pct(ra * 100) if isinstance(ra, (int, float)) else "—"}</td>'
            f'<td>{_text_pct(ir * 100) if isinstance(ir, (int, float)) else "—"}</td>'
            f'<td>{_nav(r["index_price"])}</td>'
            f'<td>{_text_pct(ia * 100) if isinstance(ia, (int, float)) else "—"}</td>'
            f'</tr>'
        )
    html.append('</tbody></table></div>')
    st.markdown("\n".join(html), unsafe_allow_html=True)
    table_html = "\n".join(html)
    cols = st.columns([1, 7])
    with cols[0]:
        if st.button("📥 导出", key="dl_annual_magazine"):
            _export_table_png(table_html, _build_css_mag(), "年化收益_杂志风")


# ── 年化收益表格 — 仪表盘风 ──
def _render_annual_table_dashboard(rows):
    st.markdown(_build_css_dash(), unsafe_allow_html=True)
    html = [
        '<div class="dashboard-wrap">',
        '<table class="dashboard-table">',
        '<thead><tr>',
        '<th>年份</th><th>实盘年限</th><th>实盘当年涨幅</th><th>实盘净值</th>',
        '<th>实盘年化</th><th>指数当年涨幅</th><th>指数价格</th><th>指数年化</th>',
        '</tr></thead>',
        '<tbody>',
    ]
    for r in rows:
        rr = r["real_return"]
        ra = r["real_annualized"]
        ir = r["index_return"]
        ia = r["index_annualized"]
        html.append(
            f'<tr>'
            f'<td style="font-weight:600;">{r["year"]}</td>'
            f'<td>{_fmt_years(r["real_years"])}</td>'
            f'<td class="mini-bar-cell">{_mini_bar(rr * 100) if isinstance(rr, (int, float)) else "—"}</td>'
            f'<td>{_nav(r["real_nav"])}</td>'
            f'<td class="mini-bar-cell">{_mini_bar(ra * 100) if isinstance(ra, (int, float)) else "—"}</td>'
            f'<td class="mini-bar-cell">{_mini_bar(ir * 100) if isinstance(ir, (int, float)) else "—"}</td>'
            f'<td>{_nav(r["index_price"])}</td>'
            f'<td class="mini-bar-cell">{_mini_bar(ia * 100) if isinstance(ia, (int, float)) else "—"}</td>'
            f'</tr>'
        )
    html.append('</tbody></table></div>')
    st.markdown("\n".join(html), unsafe_allow_html=True)
    table_html = "\n".join(html)
    cols = st.columns([1, 7])
    with cols[0]:
        if st.button("📥 导出", key="dl_annual_dashboard"):
            _export_table_png(table_html, _build_css_dash(), "年化收益_仪表盘风")


# ════════════════════════════════════════════
# 年化收益 Tab
# ════════════════════════════════════════════
def render_annualized():
    st.markdown(CSS, unsafe_allow_html=True)

    col_t, col_b = st.columns([6, 1])
    with col_t:
        st.markdown("### 📅 年化收益率")
    with col_b:
        if st.button("🔄 刷新", key="ref_a"):
            st.session_state["_pf_ann_dirty"] = True
            st.rerun()

    dirty = st.session_state.get("_pf_ann_dirty", False)
    if "_pf_annualized" not in st.session_state or dirty:
        with st.spinner("读取数据..."):
            # 复用周记表已查询的沪深300年K线，避免重复API调用
            weekly_data = st.session_state.get("_pf_weekly", {})
            idx_kline = weekly_data.get("_idx_kline_year_after")
            st.session_state["_pf_annualized"] = get_annualized_data(idx_kline_year_after=idx_kline)
            st.session_state["_pf_ann_dirty"] = False
    data = st.session_state["_pf_annualized"]

    rows = data.get("rows", [])
    if not rows:
        st.info("暂无年化收益数据")
        return

    st.markdown('<div class="pf-section">📊 实盘年度记录</div>', unsafe_allow_html=True)

    table_rows = []
    for r in rows:
        rr = r["real_return"]
        ra = r["real_annualized"]
        ir = r["index_return"]
        ia = r["index_annualized"]
        table_rows.append({
            "年份": str(r["year"]),
            "实盘年限": _fmt_years(r["real_years"]),
            "实盘当年涨幅": _pct(rr * 100) if isinstance(rr, (int, float)) else "—",
            "实盘净值": _nav(r["real_nav"]),
            "实盘年化": _pct(ra * 100) if isinstance(ra, (int, float)) else "—",
            "指数当年涨幅": _pct(ir * 100) if isinstance(ir, (int, float)) else "—",
            "指数价格": _nav(r["index_price"]),
            "指数年化": _pct(ia * 100) if isinstance(ia, (int, float)) else "—",
        })

    df = pd.DataFrame(table_rows)
    html = df.to_html(escape=False, index=False, classes="pf-table")
    st.markdown(f'<div class="table-wrapper">{html}</div>', unsafe_allow_html=True)

    # ── 文章用表格（三种风格切换）──
    _render_annual_table_selector(rows)

    # ── 历年收益概览（文章用）──
    _render_annual_article(rows)


def _render_annual_article(rows):
    st.markdown("---")
    st.markdown("### 📋 历年收益概览（文章用）")
    st.markdown('<div class="article-section">', unsafe_allow_html=True)

    for r in rows:
        year = str(r["year"])
        real_ret = r["real_return"] * 100 if isinstance(r["real_return"], (int, float)) else 0
        idx_ret = r["index_return"] * 100 if isinstance(r["index_return"], (int, float)) else 0
        nav = r["real_nav"]
        idx_price = r["index_price"]
        real_bar = min(abs(real_ret) / 30 * 100, 100)
        idx_bar = min(abs(idx_ret) / 30 * 100, 100)
        real_color = "#EF5350" if real_ret > 0 else "#66BB6A"
        idx_color = "#EF5350" if idx_ret > 0 else "#66BB6A"

        st.markdown(f"""
        <div style="margin:0.5rem 0;">
            <div style="display:flex;align-items:center;gap:0.5rem;">
                <div style="width:90px;font-weight:600;font-size:0.85rem;">{year}</div>
                <div style="flex:1;">
                    <div style="font-size:0.7rem;color:#999;margin-bottom:0.1rem;">实盘 {nav:.3f} ({real_ret:+.1f}%)</div>
                    <div style="background:rgba(128,128,128,0.15);border-radius:4px;height:8px;overflow:hidden;">
                        <div style="width:{real_bar}%;height:100%;background:{real_color};float:{'right' if real_ret < 0 else 'left'};"></div>
                    </div>
                </div>
                <div style="flex:1;">
                    <div style="font-size:0.7rem;color:#999;margin-bottom:0.1rem;">指数 {idx_price:.3f} ({idx_ret:+.1f}%)</div>
                    <div style="background:rgba(128,128,128,0.15);border-radius:4px;height:8px;overflow:hidden;">
                        <div style="width:{idx_bar}%;height:100%;background:{idx_color};float:{'right' if idx_ret < 0 else 'left'};"></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ─── 主入口 ───
def render_portfolio_page():
    st.markdown("## 💼 我的投资")
    tab1, tab2 = st.tabs(["📝 周记", "📅 年化收益"])
    with tab1:
        render_weekly()
    with tab2:
        render_annualized()
