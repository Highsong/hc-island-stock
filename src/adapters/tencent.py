"""
腾讯行情 API 适配器
数据源：https://qt.gtimg.cn/ （无需登录，无需 cookie）

字段说明（以 HKDCNY 为例）：
  [3]  = 当前价
  [18] = 年内涨幅 %
  [19] = 年内最高
  [20] = 年内最低
"""

import time
import requests
from typing import Dict, Any, Optional


def _f(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def fetch_hkdcny_tencent() -> Dict[str, Any]:
    """
    获取港币兑人民币实时行情（腾讯）
    API: https://qt.gtimg.cn/?q=whHKDCNY

    返回:
        {
            "data": {"current": float, "year_chg": float, "year_high": float, "year_low": float} | None,
            "source": "tencent",
            "elapsed_ms": int
        }
    """
    t0 = int(time.time() * 1000)
    result = {"data": None, "source": "tencent", "elapsed_ms": 0}
    try:
        url = "https://qt.gtimg.cn/?q=whHKDCNY"
        resp = requests.get(url, timeout=10)
        raw = resp.text
        # 解析: v_whHKDCNY="310~港元人民币~HKDCNY~0.8716~...~-2.87~0.9408~0.8694~...";
        data_str = raw.split('"')[1] if '"' in raw else ""
        fields = data_str.split("~") if data_str else []
        if len(fields) > 18:
            current = _f(fields[3])
            if current > 0:
                result["data"] = {
                    "current": round(current, 4),
                    "year_chg": _f(fields[18]),    # 年内涨幅 %
                    "year_high": _f(fields[19]),    # 年内最高
                    "year_low": _f(fields[20]),     # 年内最低
                }
    except Exception as e:
        print(f"[Adapter/Tencent] HKDCNY error: {e}")
    result["elapsed_ms"] = int(time.time() * 1000) - t0
    return result
