"""
外部 API 适配器层
所有外部数据源调用统一封装，便于维护、切换、耗时统计

每个 adapter 函数返回统一结构:
    {"data": ..., "source": "adapter_name", "elapsed_ms": int}
"""
from .tencent import fetch_hkdcny_tencent
from .xueqiu import fetch_detail_batch, fetch_kline_year_after, fetch_kline_week_after

__all__ = [
    "fetch_hkdcny_tencent",
    "fetch_detail_batch",
    "fetch_kline_year_after",
    "fetch_kline_week_after",
]
