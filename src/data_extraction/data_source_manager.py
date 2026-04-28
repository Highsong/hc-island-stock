"""
数据源管理器

按优先级依次尝试各个数据源，第一个返回有效数据的数据源胜出。
数据源之间完全隔离，互不影响。

使用方式:
    manager = DataSourceManager()
    manager.register(XueqiuDataSource())
    manager.register(StockDataSource())       # AKShare
    manager.register(SampleDataSource())       # 最终兜底

    data = manager.get_stock_financial_data("600519", "2020", "2024", "year")
"""

from typing import List, Dict, Any, Optional
from data_extraction.data_source import DataSource


class DataSourceManager:
    """数据源调度管理器 — 责任链模式"""

    def __init__(self):
        self._sources: List[DataSource] = []
        self._last_successful_source: str = ""

    def register(self, source: DataSource) -> "DataSourceManager":
        """注册数据源（按注册顺序确定优先级）"""
        self._sources.append(source)
        return self

    @property
    def active_source_name(self) -> str:
        """返回最近一次成功获取数据的数据源名称"""
        return self._last_successful_source

    def get_stock_financial_data(
        self, stock_code: str, start_year: str, end_year: str, period: str
    ) -> Dict[str, Any]:
        """
        按优先级依次尝试各数据源获取财务数据。

        Returns:
            成功: 标准化的财务数据 dict
            全部失败: 空 dict（理论上不会发生，因为 SampleDataSource 始终可用）
        """
        xueqiu_available = False
        for source in self._sources:
            name = source.get_name()
            if not source.is_available():
                if "雪球" in name:
                    print(f"[DataSourceManager] ⚠️ {name} 不可用（Cookie 可能已过期），跳过")
                else:
                    print(f"[DataSourceManager] {name} 不可用，跳过")
                continue

            if "雪球" in name:
                xueqiu_available = True

            try:
                print(f"[DataSourceManager] 尝试从 {name} 获取数据...")
                data = source.get_stock_financial_data(
                    stock_code, start_year, end_year, period
                )
                if data and len(data) > 0:
                    self._last_successful_source = name
                    print(f"[DataSourceManager] ✅ {name} 获取成功，"
                          f"共 {len(data)} 年数据")
                    return data
                else:
                    print(f"[DataSourceManager] ⚠️ {name} 返回空数据，"
                          f"尝试下一数据源")
            except Exception as e:
                print(f"[DataSourceManager] ❌ {name} 出错: {e}，"
                      f"尝试下一数据源")
                continue

        # 理论上不会执行到这里（SampleDataSource 始终可用）
        print("[DataSourceManager] 所有数据源均失败，返回空数据")
        return {}

    def get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """
        按优先级依次尝试各数据源获取股票基本信息。
        """
        for source in self._sources:
            name = source.get_name()
            if not source.is_available():
                continue

            try:
                info = source.get_stock_info(stock_code)
                if info and info.get("name"):
                    self._last_successful_source = name
                    return info
            except Exception:
                continue

        return {
            "code": stock_code,
            "name": f"股票{stock_code}",
            "industry": "未知行业",
            "market": "未知市场",
        }
