"""
示例数据源 — 最终兜底

当所有真实数据源都不可用时，使用硬编码的模拟数据。
数据基于800亿营收、35%净利率的模板，按年份递增。

注意：示例数据中的"净利润"字段实际对应归母净利润口径。
"""

from typing import Dict, Any


def generate_sample_data(
    stock_code: str, start_year: str, end_year: str
) -> Dict[str, Any]:
    """
    生成示例财务数据

    Returns:
        标准化的财务数据 dict，格式与其他数据源一致
    """
    result = {}
    try:
        start_y = int(start_year)
        end_y = int(end_year)

        for year in range(start_y, end_y + 1):
            base_revenue = 80_000_000_000 + (year - start_y) * 5_000_000_000
            base_profit = base_revenue * 0.35

            result[str(year)] = {
                "income_statement": {
                    "营业收入": [base_revenue],
                    "净利润": [base_profit],
                    "营业成本": [base_revenue * 0.4],
                    "销售费用": [base_revenue * 0.08],
                    "管理费用": [base_revenue * 0.05],
                    "财务费用": [base_revenue * -0.01],
                },
                "balance_sheet": {
                    "总资产": [base_revenue * 2.5],
                    "总负债": [base_revenue * 0.8],
                    "所有者权益": [base_revenue * 1.7],
                    "流动资产": [base_revenue * 1.5],
                    "流动负债": [base_revenue * 0.6],
                    "存货": [base_revenue * 0.3],
                },
                "cash_flow": {
                    "经营活动现金流": [base_profit * 1.1],
                    "投资活动现金流": [base_profit * -0.3],
                    "筹资活动现金流": [base_profit * -0.2],
                    "现金净增加额": [base_profit * 0.6],
                },
            }
    except Exception as e:
        print(f"[SampleData] 生成示例数据失败: {e}")

    return result


class SampleDataSource:
    """示例数据源 — 始终可用，作为最终兜底"""

    def get_name(self) -> str:
        return "示例数据(演示)"

    def is_available(self) -> bool:
        return True  # 始终可用

    def get_stock_financial_data(
        self, stock_code: str, start_year: str, end_year: str, period: str
    ) -> Dict[str, Any]:
        print(f"[{self.get_name()}] 生成 {stock_code} 的示例数据 "
              f"({start_year}-{end_year})")
        return generate_sample_data(stock_code, start_year, end_year)

    def get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        known_stocks = {
            "600519": {"name": "贵州茅台", "industry": "白酒", "market": "沪市A股"},
            "000001": {"name": "平安银行", "industry": "银行", "market": "深市A股"},
            "000002": {"name": "万科A", "industry": "房地产", "market": "深市A股"},
            "600000": {"name": "浦发银行", "industry": "银行", "market": "沪市A股"},
            "600036": {"name": "招商银行", "industry": "银行", "market": "沪市A股"},
            "601318": {"name": "中国平安", "industry": "保险", "market": "沪市A股"},
            "000858": {"name": "五粮液", "industry": "白酒", "market": "深市A股"},
            "002415": {"name": "海康威视", "industry": "安防设备", "market": "深市A股"},
            "300059": {"name": "东方财富", "industry": "互联网服务", "market": "深市A股"},
        }

        code = stock_code.strip().lstrip("SHZJB")
        if code in known_stocks:
            s = known_stocks[code]
            return {
                "code": stock_code,
                "name": s["name"],
                "industry": s["industry"],
                "market": s["market"],
                "area": "未知地区",
                "pe": 0, "pb": 0,
                "total_share": 0, "circulating_share": 0,
            }
        return {
            "code": stock_code,
            "name": f"股票{stock_code}",
            "industry": "未知行业",
            "market": "未知市场",
            "area": "未知地区",
            "pe": 0, "pb": 0,
            "total_share": 0, "circulating_share": 0,
        }
