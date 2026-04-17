# src/analysis/trend_analysis.py
from typing import Dict, List, Tuple, Any
import numpy as np

class TrendAnalysis:
    """趋势分析器"""

    def __init__(self):
        self.trends = {}

    def analyze_trend_direction(self, values: List[float]) -> str:
        """分析趋势方向"""
        if len(values) < 2:
            return "数据不足"

        # 计算整体趋势
        start_val = values[0]
        end_val = values[-1]

        if end_val > start_val * 1.1:  # 增长超过10%
            return "上升趋势"
        elif end_val < start_val * 0.9:  # 下降超过10%
            return "下降趋势"
        else:
            return "平稳趋势"

    def calculate_compound_growth_rate(self, values: List[float]) -> float:
        """计算复合增长率"""
        if len(values) < 2:
            return 0

        start_val = values[0]
        end_val = values[-1]
        years = len(values) - 1

        if start_val == 0:
            return 0

        cagr = (end_val / start_val) ** (1/years) - 1
        return cagr

    def identify_seasonal_patterns(self, quarterly_data: List[float]) -> Dict[str, Any]:
        """识别季度模式"""
        if len(quarterly_data) < 8:  # 至少2年数据
            return {"error": "数据不足"}

        # 计算季度平均值
        quarters = [quarterly_data[i:i+4] for i in range(0, len(quarterly_data), 4)]

        if len(quarters[-1]) < 4:  # 移除不完整的年份
            quarters = quarters[:-1]

        q_avg = [sum(q[i] for q in quarters) / len(quarters) for i in range(4)]

        patterns = {
            "最强季度": f"Q{q_avg.index(max(q_avg)) + 1}",
            "最弱季度": f"Q{q_avg.index(min(q_avg)) + 1}",
            "季度波动性": np.std(q_avg) / np.mean(q_avg) if np.mean(q_avg) != 0 else 0
        }

        return patterns

    def detect_anomalies(self, values: List[float], threshold: float = 2.0) -> List[int]:
        """检测异常值"""
        if len(values) < 3:
            return []

        mean_val = np.mean(values)
        std_val = np.std(values)

        anomalies = []
        for i, val in enumerate(values):
            if abs(val - mean_val) > threshold * std_val:
                anomalies.append(i)

        return anomalies