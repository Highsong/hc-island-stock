"""
数据源抽象协议

定义所有数据源必须实现的接口，新增数据源只需实现此 Protocol 即可。
"""

from typing import Protocol, Dict, Any, Optional


class DataSource(Protocol):
    """数据源协议 — 所有数据源必须实现此接口"""

    def get_name(self) -> str:
        """返回数据源名称（用于日志和UI显示）"""
        ...

    def is_available(self) -> bool:
        """检查数据源是否可用（网络连通、依赖库已安装等）"""
        ...

    def get_stock_financial_data(
        self, stock_code: str, start_year: str, end_year: str, period: str
    ) -> Dict[str, Any]:
        """
        获取股票财务数据

        Args:
            stock_code: 股票代码（如 SH600519, 600519）
            start_year: 开始年份
            end_year: 结束年份
            period: 数据周期 ('year', 'quarter', 'year_half')

        Returns:
            格式: {
                "2024": {
                    "income_statement": {"营业收入": [val], "净利润": [val], ...},
                    "balance_sheet": {"总资产": [val], ...},
                    "cash_flow": {"经营活动现金流": [val], ...}
                },
                "2023": {...}
            }
            失败时返回空 dict {}
        """
        ...

    def get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票基本信息

        Returns:
            格式: {"code": ..., "name": ..., "industry": ..., "market": ..., ...}
            失败时返回空 dict {}
        """
        ...
