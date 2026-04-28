"""
投资组合数据管理 - 实盘组合
- 周记：持股名称、持股比例、当前市值、理想买点、年内卖点、当前股价、年内涨幅
           + 实盘净值行、对比基准行、日期行（特殊格式）
- 年化收益：年份、实盘年限、实盘当年涨幅、实盘净值、实盘年化、指数当年涨幅、指数价格、指数年化

所有外部 API 调用统一通过 src/adapters/ 适配器层，不直接 requests.get
"""

import json
import math
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# ─── 适配器导入 ───
import sys, os
_ADAPTERS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))
if _ADAPTERS_PATH not in sys.path:
    sys.path.insert(0, _ADAPTERS_PATH)
from adapters.xueqiu import fetch_detail_batch, fetch_kline_year_after, fetch_kline_week_after
from adapters.tencent import fetch_hkdcny_tencent

# ─── 路径 ───
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PORTFOLIO_FILE = os.path.join(DATA_DIR, "portfolio.json")

# ─── 本地 JSON ───
def load_portfolio() -> Dict[str, Any]:
    if not os.path.exists(PORTFOLIO_FILE):
        return {"holdings": [], "nav": {}, "annual_records": []}
    with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_portfolio(data: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── 工具 ───
def _f(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default

def _xueqiu_symbol(code: str, exchange: str) -> str:
    """生成雪球 API 用的 symbol：港股纯数字，A股带前缀"""
    if exchange == "HK":
        return code
    return f"{exchange}{code}"


# ════════════════════════════════════════════
# 周记表数据
# ════════════════════════════════════════════
def get_weekly_data() -> Dict[str, Any]:
    """
    组装周记表数据。

    普通行（股票）：持股名称 | 持股比例 | 当前市值(亿) | 理想买点(亿) | 年内卖点(亿) | 当前股价 | 年内涨幅
    特殊行1（实盘净值）：周涨幅 | 净值 | 年内涨幅
    特殊行2（沪深300）：周涨幅 | 价格 | 年内涨幅
    特殊行3（日期行）：港币汇率 | 年内跌幅 | 日期
    """
    pf = load_portfolio()
    holdings = pf.get("holdings", [])
    if not holdings:
        return {"rows": [], "special_rows": [], "summary": {}}

    # ── 分类 ──
    stock_holdings = []
    nav_holding = None
    index_holding = None
    fx_holding = None

    for h in holdings:
        cat = h.get("category", "")
        code = h.get("code", "")
        if cat == "实盘":
            nav_holding = h
        elif code == "510310":
            index_holding = h
        elif code == "HKDCNY":
            fx_holding = h
        elif h.get("exchange") and h.get("exchange") != "FX":
            stock_holdings.append(h)

    # ── 获取港币汇率（腾讯 API，一次调用）──
    fx_result = fetch_hkdcny_tencent()
    fx_data = fx_result.get("data") or {}
    fx_current = fx_data.get("current", 0.0)
    fx_year_chg_from_api = fx_data.get("year_chg", 0.0)
    print(f"[Portfolio] 汇率: {fx_current} (年内{fx_year_chg_from_api:+.2f}%) source={fx_result['source']} {fx_result['elapsed_ms']}ms", flush=True)

    # ── 批量获取所有持仓股票行情 ──
    stock_syms = [_xueqiu_symbol(h["code"], h["exchange"]) for h in stock_holdings]
    detail_result = fetch_detail_batch(stock_syms)
    details = detail_result.get("data") or {}
    got = len(details)
    print(f"[Portfolio] 批量报价: {got}/{len(stock_syms)} 只成功 source={detail_result['source']} {detail_result['elapsed_ms']}ms", flush=True)
    if got == 0:
        print(f"[Portfolio] ⚠️ 股票报价全部失败，请检查雪球 Cookie 是否过期", flush=True)

    # ── 获取沪深300后复权年K线 + 周K线 ──
    idx_kline_year_after = []
    idx_kline_week_after = []
    if index_holding:
        idx_sym = _xueqiu_symbol(index_holding["code"], index_holding["exchange"])
        year_result = fetch_kline_year_after(idx_sym)
        idx_kline_year_after = year_result.get("data") or []
        print(f"[Portfolio] 沪深300年K: {len(idx_kline_year_after)} 根 source={year_result['source']} {year_result['elapsed_ms']}ms", flush=True)
        week_result = fetch_kline_week_after(idx_sym, count=2)
        idx_kline_week_after = week_result.get("data") or []
        print(f"[Portfolio] 沪深300周K: {len(idx_kline_week_after)} 根 source={week_result['source']} {week_result['elapsed_ms']}ms", flush=True)

    # ── 构建普通股票行 ──
    stock_rows = []
    total_market_value = 0.0

    for h in stock_holdings:
        code = h.get("code", "")
        exchange = h.get("exchange", "")
        category = h.get("category", "")
        name = h.get("name", "")
        buy_point = _f(h.get("buy_point"))
        sell_point = _f(h.get("sell_point"))
        sym = _xueqiu_symbol(code, exchange)

        det = details.get(sym, {}) or {}
        current_price = det.get("current", 0)
        market_cap_raw = det.get("market_capital", 0)  # 元
        market_value = market_cap_raw / 1e8 if market_cap_raw > 0 else 0  # 转亿

        is_hkd = (exchange == "HK") or (exchange == "SZ" and category == "B股行业")
        if is_hkd and fx_current > 0:
            market_value = market_value * fx_current

        year_chg = det.get("year_chg", 0)
        total_market_value += market_value

        stock_rows.append({
            "name": name,
            "code": code,
            "exchange": exchange,
            "buy_point": int(buy_point) if buy_point > 0 else 0,
            "sell_point": int(sell_point) if sell_point > 0 else 0,
            "current_price": current_price,
            "market_value": round(market_value, 2),
            "year_chg": round(year_chg, 2),
            "is_special": False,
        })

    # ── 实盘净值行 ──
    special_rows = []
    if nav_holding:
        nav_current = _f(nav_holding.get("current_price"))
        nav_last_week = _f(nav_holding.get("last_week_price"))
        nav_year_start = _f(nav_holding.get("year_start_price"))

        nav_week_chg = ((nav_current - nav_last_week) / nav_last_week * 100) if nav_last_week else 0
        nav_year_chg = ((nav_current - nav_year_start) / nav_year_start * 100) if nav_year_start else 0

        special_rows.append({
            "label": "实盘净值",
            "col1_label": "周涨幅", "col1_value": round(nav_week_chg, 2),
            "col2_label": "实盘净值", "col2_value": nav_current,
            "col3_label": "年内涨幅", "col3_value": round(nav_year_chg, 2),
            "special_type": "nav",
        })

    # ── 对比基准行（沪深300） ──
    if index_holding:
        idx_current_after = 0.0
        idx_year_chg_after = 0.0
        if idx_kline_year_after:
            idx_current_after = _f(idx_kline_year_after[-1][5])   # close
            idx_year_chg_after = _f(idx_kline_year_after[-1][7])  # 年内涨幅%

        idx_week_chg = _f(idx_kline_week_after[-1][7]) if idx_kline_week_after else 0  # 周涨幅%

        special_rows.append({
            "label": "沪深300指数基金 510310",
            "col1_label": "周涨幅", "col1_value": round(idx_week_chg, 2),
            "col2_label": "指数价格", "col2_value": idx_current_after,
            "col3_label": "年内涨幅", "col3_value": round(idx_year_chg_after, 2),
            "special_type": "index",
        })

        index_holding["market_cap"] = idx_current_after

    # ── 日期行（港币汇率） ──
    # 年内涨幅优先级：用户手动设置年初汇率 > 腾讯API返回的年内涨幅
    fx_year_start_val = _f(fx_holding.get("year_start_price")) if fx_holding else 0
    if fx_year_start_val > 0:
        # 用户设置了年初汇率，用 (当前价/年初价 - 1) 计算
        fx_year_chg = ((fx_current - fx_year_start_val) / fx_year_start_val * 100)
    elif fx_year_chg_from_api != 0:
        # 未设置年初汇率，直接用腾讯API返回的年内涨幅
        fx_year_chg = fx_year_chg_from_api
    else:
        fx_year_chg = 0

    today_str = datetime.now().strftime("%Y/%m/%d")
    special_rows.append({
        "label": today_str,
        "col1_label": "港币汇率", "col1_value": round(fx_current, 4) if fx_current else 0,
        "col2_label": "", "col2_value": None,
        "col3_label": "年内跌幅", "col3_value": round(fx_year_chg, 2),
        "special_type": "fx",
    })

    return {
        "rows": stock_rows,
        "special_rows": special_rows,
        "summary": {
            "total_market_value": round(total_market_value, 2),
            "count": len(stock_rows),
        },
        "_idx_kline_year_after": idx_kline_year_after,  # 内部透传，供年化收益表复用
    }


# ════════════════════════════════════════════
# 年化收益表数据
# ════════════════════════════════════════════
def get_annualized_data(idx_kline_year_after: List[List] = None) -> Dict[str, Any]:
    """
    组装年化收益表数据。
    - 历史年份：直接读取 JSON 原始数据，不做任何修改
    - 最后一行（当年）动态计算：
      实盘当年涨幅 = (今年实盘净值 / 去年实盘净值) - 1
      实盘年化     = (今年实盘净值 / 1)^(1/年限) - 1，最初净值=1
      指数当年涨幅 = 复用周记表K线数据，不再重复查询
      指数年化     = (今年指数价格 / 初始指数价格)^(1/年限) - 1

    参数:
        idx_kline_year_after: 沪深300年后复权K线，由调用方传入以避免重复查询
    """
    pf = load_portfolio()
    annual_records = pf.get("annual_records", [])

    # 获取实盘净值最新值
    nav_current = 0.0
    for h in pf.get("holdings", []):
        if h.get("category") == "实盘":
            nav_current = _f(h.get("current_price"))
            break

    # 获取沪深300后复权最新价
    idx_price_current = 0.0
    idx_year_chg = 0.0
    if idx_kline_year_after is None:
        result = fetch_kline_year_after("SH510310")
        idx_kline_year_after = result.get("data") or []
        print(f"[Portfolio] 年化表独立查沪深300年K: {len(idx_kline_year_after)} 根 {result['elapsed_ms']}ms", flush=True)
    else:
        print(f"[Portfolio] 年化表复用周记表K线: {len(idx_kline_year_after)} 根", flush=True)
    if idx_kline_year_after:
        idx_price_current = _f(idx_kline_year_after[-1][5])   # close
        idx_year_chg = _f(idx_kline_year_after[-1][7])         # 年内涨幅%

    # 初始指数价格
    initial_index_price = _f(annual_records[0].get("index_price", 0)) if annual_records else 0.0

    rows = []
    for i, record in enumerate(annual_records):
        is_last = (i == len(annual_records) - 1)

        if is_last:
            real_nav = nav_current if nav_current > 0 else _f(record.get("real_nav", 0))
            index_price = idx_price_current if idx_price_current > 0 else _f(record.get("index_price", 0))
            real_years = record.get("real_years", 0)

            prev_record = annual_records[i - 1] if i > 0 else {}
            prev_real_nav = _f(prev_record.get("real_nav", 0))
            prev_index_price = _f(prev_record.get("index_price", 0))

            real_return = (real_nav / prev_real_nav - 1.0) if prev_real_nav > 0 else 0.0
            real_annualized = (math.pow(real_nav, 1.0 / real_years) - 1.0) if real_years > 0 and real_nav > 0 else 0.0

            # 指数当年涨幅：复用K线数据，与周记表口径一致
            index_return = idx_year_chg / 100.0  # K线返回的是百分比数值，转为小数
            if index_return == 0 and prev_index_price > 0 and index_price > 0:
                index_return = (index_price / prev_index_price - 1.0)

            index_annualized = (math.pow(index_price / initial_index_price, 1.0 / real_years) - 1.0) if real_years > 0 and initial_index_price > 0 and index_price > 0 else 0.0

            rows.append({
                "year": str(record.get("year", "")),
                "real_years": real_years,
                "real_return": real_return,
                "real_nav": real_nav,
                "real_annualized": real_annualized,
                "index_return": index_return,
                "index_price": index_price,
                "index_annualized": index_annualized,
            })
        else:
            rows.append({
                "year": str(record.get("year", "")),
                "real_years": record.get("real_years", 0),
                "real_return": record.get("real_return", 0),
                "real_nav": record.get("real_nav", 0),
                "real_annualized": record.get("real_annualized", 0),
                "index_return": record.get("index_return", 0),
                "index_price": record.get("index_price", 0),
                "index_annualized": record.get("index_annualized", 0),
            })

    return {"rows": rows}
