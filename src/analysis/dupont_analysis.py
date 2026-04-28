"""
杜邦分析模块
ROE = 净利率 × 总资产周转率 × 权益乘数

对最新一期进行分解，并与上年同期对比，分析 ROE 变化的驱动因素。
"""
from typing import Dict, Any, Optional, Tuple


def _safe_div(a: float, b: float) -> Optional[float]:
    """安全除法，除零返回 None"""
    if b and b != 0:
        return a / b
    return None


def _safe_float(v) -> float:
    """从 [val, yoy] 或纯数值中取 float"""
    if isinstance(v, (list, tuple)) and len(v) > 0:
        return float(v[0]) if v[0] is not None else 0.0
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _get_inc(raw_data: Dict, period: str, field: str, fallback: str = None) -> float:
    """从 income_statement 取数值"""
    inc = raw_data.get(period, {}).get('income_statement', {})
    v = inc.get(field, [0])[0]
    if (v is None or v == 0) and fallback:
        v = inc.get(fallback, [0])[0]
    return _safe_float(v)


def _get_bs(raw_data: Dict, period: str, field: str, fallback: str = None) -> float:
    """从 balance_sheet 取数值"""
    bs = raw_data.get(period, {}).get('balance_sheet', {})
    v = bs.get(field, [0])[0]
    if (v is None or v == 0) and fallback:
        v = bs.get(fallback, [0])[0]
    return _safe_float(v)


def calculate_dupont(raw_data: Dict[str, Any], period: str) -> Dict[str, Optional[float]]:
    """计算单期杜邦三因素

    Returns:
        {
            'roe': float,
            'net_margin': float,      # 净利率
            'asset_turnover': float,  # 总资产周转率
            'equity_multiplier': float,  # 权益乘数
            'revenue': float,
            'net_profit': float,
            'total_assets': float,
            'total_equity': float,
        }
    """
    rev = _get_inc(raw_data, period, '营业收入', '营业总收入')
    profit = _get_inc(raw_data, period, '归母净利润')
    total_assets = _get_bs(raw_data, period, '资产总计', '总资产')
    total_equity = _get_bs(raw_data, period, '所有者权益合计')

    net_margin = _safe_div(profit, rev)
    asset_turnover = _safe_div(rev, total_assets)
    equity_multiplier = _safe_div(total_assets, total_equity)
    roe = _safe_div(profit, total_equity)  # 直接计算验证

    return {
        'roe': roe,
        'net_margin': net_margin,
        'asset_turnover': asset_turnover,
        'equity_multiplier': equity_multiplier,
        'revenue': rev,
        'net_profit': profit,
        'total_assets': total_assets,
        'total_equity': total_equity,
    }


def calculate_dupont_with_comparison(raw_data: Dict[str, Any],
                                      period: str = None) -> Dict[str, Any]:
    """计算指定期间（默认最新）+ 上年同期杜邦三因素，用于对比分析

    Args:
        raw_data: 原始财务数据
        period: 指定分析期间（如 '2023'），None 则取最新

    Returns:
        {
            'latest': {...},   # 指定期间
            'previous': {...}, # 上年同期
            'delta': {         # 变化量
                'roe': float,
                'net_margin': float,
                'asset_turnover': float,
                'equity_multiplier': float,
            },
            'drivers': [str],  # 文字解读
            'period': str,     # 实际分析的期间
        }
    """
    periods = sorted(raw_data.keys())
    if not periods:
        return {'latest': {}, 'previous': {}, 'delta': {}, 'drivers': ['数据不足'], 'period': ''}

    latest_period = period if period and period in raw_data else periods[-1]
    result = {
        'latest': calculate_dupont(raw_data, latest_period),
        'previous': {},
        'delta': {},
        'drivers': [],
        'period': latest_period,
    }

    if len(periods) >= 2:
        prev_period = periods[-2]
        result['previous'] = calculate_dupont(raw_data, prev_period)
        # 计算变化
        for key in ('roe', 'net_margin', 'asset_turnover', 'equity_multiplier'):
            lv = result['latest'].get(key)
            pv = result['previous'].get(key)
            if lv is not None and pv is not None:
                result['delta'][key] = lv - pv
            else:
                result['delta'][key] = None

    # ── 生成文字解读 ──
    drivers = result['drivers']
    delta = result['delta']
    latest = result['latest']

    roe_val = latest.get('roe')
    if roe_val is not None:
        drivers.append(f"最新一期 ROE = **{roe_val:.1%}**")

    if not delta or all(v is None for v in delta.values()):
        drivers.append("（仅一期数据，无法进行同比分析）")
        return result

    roe_delta = delta.get('roe')
    if roe_delta is not None:
        direction = "上升" if roe_delta > 0 else "下降"
        drivers.append(f"ROE 同比 **{direction}** {abs(roe_delta):.1%}")

    # 分析各因素贡献
    margin_delta = delta.get('net_margin')
    turnover_delta = delta.get('asset_turnover')
    em_delta = delta.get('equity_multiplier')

    contributors = []
    if margin_delta is not None and abs(margin_delta) > 0.001:
        d = "提升" if margin_delta > 0 else "下降"
        contributors.append(f"净利率 {d} {abs(margin_delta):.1%}")
    if turnover_delta is not None and abs(turnover_delta) > 0.001:
        d = "提升" if turnover_delta > 0 else "下降"
        contributors.append(f"资产周转率 {d} {abs(turnover_delta):.2f}")
    if em_delta is not None and abs(em_delta) > 0.001:
        d = "上升" if em_delta > 0 else "下降"
        contributors.append(f"权益乘数 {d} {abs(em_delta):.2f}")

    if contributors:
        drivers.append("主要驱动因素：" + "、".join(contributors))

    # 综合评价
    prev_roe = result['previous'].get('roe')
    if roe_val is not None and prev_roe is not None:
        if roe_val > 0.25 and roe_delta is not None and roe_delta >= 0:
            drivers.append("🏆 ROE 处于较高水平且持续改善，盈利能力优异")
        elif roe_val > 0.15 and (roe_delta is None or roe_delta >= -0.01):
            drivers.append("✅ ROE 处于合理区间，盈利能力稳定")
        elif roe_delta is not None and roe_delta < -0.03:
            drivers.append("⚠️ ROE 同比明显下滑，需关注盈利质量变化")
        else:
            drivers.append("📊 ROE 水平一般，关注后续改善空间")

    return result
