"""
雪球 API 适配器
数据源：https://stock.xueqiu.com/ （需要 cookie）

所有函数返回统一结构:
    {"data": ..., "source": "xueqiu", "elapsed_ms": int}
"""

import time
import requests
from typing import Dict, List, Any, Optional

# ─── Cookie 管理 ───
def _load_cookie() -> str:
    import os
    # __file__ = src/adapters/xueqiu.py → 往两级到项目根目录
    cookie_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "config", "XueQiuCookie.txt"
    )
    try:
        with open(cookie_path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            if raw.startswith("cookie="):
                raw = raw[len("cookie="):]
            return raw
    except Exception:
        return ""


def _headers() -> Dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": _load_cookie(),
        "Referer": "https://xueqiu.com/",
    }


def _f(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def fetch_detail_batch(symbols: List[str]) -> Dict[str, Any]:
    """
    批量获取多只股票实时行情（报价、市值、年内涨幅）
    API: /v5/stock/batch/quote.json?symbol=...&extend=detail

    返回:
        {
            "data": {symbol: {current, market_capital, year_chg, name}} | None,
            "source": "xueqiu",
            "elapsed_ms": int
        }
    """
    t0 = int(time.time() * 1000)
    result = {"data": None, "source": "xueqiu", "elapsed_ms": 0}
    if not symbols:
        result["elapsed_ms"] = int(time.time() * 1000) - t0
        return result

    joined = ",".join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={joined}&extend=detail"
    try:
        resp = requests.get(url, headers=_headers(), timeout=15)
        data = resp.json()
        items = data.get("data", {}).get("items", [])
        out = {}
        for item in items:
            q = item.get("quote", {})
            sym = q.get("symbol", "")
            if q.get("current"):
                out[sym] = {
                    "current": _f(q.get("current")),
                    "market_capital": _f(q.get("market_capital")),
                    "year_chg": _f(q.get("current_year_percent")),
                    "name": q.get("name", ""),
                }
        result["data"] = out
    except Exception as e:
        print(f"[Adapter/Xueqiu] batch detail error: {e}")
    result["elapsed_ms"] = int(time.time() * 1000) - t0
    return result


def fetch_kline_year_after(symbol: str) -> Dict[str, Any]:
    """
    获取后复权年K线，count=-1 只取最新一根
    API: /v5/stock/chart/kline.json?period=year&type=after&count=-1
    字段: [0]=ts, [5]=close, [7]=percent(年内涨幅%)

    返回:
        {
            "data": [[...]] | None (K线数组),
            "source": "xueqiu",
            "elapsed_ms": int
        }
    """
    t0 = int(time.time() * 1000)
    result = {"data": None, "source": "xueqiu", "elapsed_ms": 0}
    now_ms = int(time.time() * 1000)
    url = (f"https://stock.xueqiu.com/v5/stock/chart/kline.json?"
           f"symbol={symbol}&begin={now_ms}&period=year&type=after&count=-1&indicator=kline")
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        data = resp.json()
        items = (data.get("data") or {}).get("item", [])
        result["data"] = items if isinstance(items, list) else []
    except Exception as e:
        print(f"[Adapter/Xueqiu] year kline error {symbol}: {e}")
    result["elapsed_ms"] = int(time.time() * 1000) - t0
    return result


def fetch_kline_week_after(symbol: str, count: int = 2) -> Dict[str, Any]:
    """
    获取后复权周K线
    API: /v5/stock/chart/kline.json?period=week&type=after&count=-N
    字段: [5]=close, [7]=percent(周涨幅%)

    返回:
        {
            "data": [[...]] | None (K线数组),
            "source": "xueqiu",
            "elapsed_ms": int
        }
    """
    t0 = int(time.time() * 1000)
    result = {"data": None, "source": "xueqiu", "elapsed_ms": 0}
    now_ms = int(time.time() * 1000)
    url = (f"https://stock.xueqiu.com/v5/stock/chart/kline.json?"
           f"symbol={symbol}&begin={now_ms}&period=week&type=after&count=-{count}&indicator=kline")
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        data = resp.json()
        items = (data.get("data") or {}).get("item", [])
        result["data"] = items if isinstance(items, list) else []
    except Exception as e:
        print(f"[Adapter/Xueqiu] week kline error {symbol}: {e}")
    result["elapsed_ms"] = int(time.time() * 1000) - t0
    return result
