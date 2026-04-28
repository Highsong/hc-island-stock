"""
波特五力分析模块
基于财务数据对行业竞争格局进行定性评估。

五力：
1. 供应商议价能力 — 毛利率越高、预付款越少 → 对供应商控制力越强
2. 购买者议价能力 — 应收账款越少、营收增长越稳 → 对下游控制力越强
3. 新进入者壁垒   — ROE 和净利率越高 → 行业壁垒越高（强=壁垒高）
4. 替代品抵御力   — 营收越稳定、现金流越充裕 → 抵御力越强（强=威胁低）
5. 行业竞争强度   — 毛利率越高、费用率越低 → 竞争压力越小（强=竞争优势大）
"""
from typing import Dict, Any, List, Tuple, Optional


def _safe_div(a: float, b: float) -> Optional[float]:
    if b and b != 0:
        return a / b
    return None


def _get_field(raw_data: Dict, period: str, table: str, field: str,
               fallback: str = None) -> float:
    """从 raw_data 取数值"""
    d = raw_data.get(period, {}).get(table, {})
    v = d.get(field, [0])[0]
    if (v is None or v == 0) and fallback:
        v = d.get(fallback, [0])[0]
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _rate(level: str) -> Tuple[str, str]:
    """返回 (emoji, 描述)"""
    rates = {
        '强': ('🟢', '强'),
        '中': ('🟡', '中等'),
        '弱': ('🔴', '弱'),
    }
    return rates.get(level, ('⚪', '未知'))


def analyze_porter_five_forces(raw_data: Dict[str, Any],
                               period: str = None,
                               stock_info: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """执行波特五力分析

    Args:
        raw_data: 原始财务数据
        period: 指定分析期间（如 '2023'），None 则取最新
        stock_info: 股票基本信息（保留兼容）

    Returns:
        [
            {
                'name': '供应商议价能力',
                'icon': '🏭',
                'level': '强' | '中' | '弱',
                'emoji': '🟢' | '🟡' | '🔴',
                'reason': '...',
            },
            ...
        ]
    """
    periods = sorted(raw_data.keys())
    if not periods:
        return []

    latest = period if period and period in raw_data else periods[-1]
    # 找前一年作为对比
    prev = None
    if latest in periods:
        idx = periods.index(latest)
        if idx > 0:
            prev = periods[idx - 1]

    inc = raw_data[latest].get('income_statement', {})
    bs = raw_data[latest].get('balance_sheet', {})
    cf = raw_data[latest].get('cash_flow', {})

    revenue = _get_field(raw_data, latest, 'income_statement', '营业收入', '营业总收入')
    profit = _get_field(raw_data, latest, 'income_statement', '归母净利润')
    op_cost = _get_field(raw_data, latest, 'income_statement', '营业成本')
    sales_fee = _get_field(raw_data, latest, 'income_statement', '销售费用')
    total_assets = _get_field(raw_data, latest, 'balance_sheet', '资产总计', '总资产')
    equity = _get_field(raw_data, latest, 'balance_sheet', '所有者权益合计')
    receivable = _get_field(raw_data, latest, 'balance_sheet', '应收账款')
    if not receivable:
        receivable = _get_field(raw_data, latest, 'balance_sheet', '应收票据及应收账款')
    prepayment = _get_field(raw_data, latest, 'balance_sheet', '预付款项')
    ocf = _get_field(raw_data, latest, 'cash_flow', '经营活动产生的现金流量净额',
                     '经营活动现金流净额')

    # 上年数据
    prev_revenue = prev_gross_margin = None
    if prev:
        prev_revenue = _get_field(raw_data, prev, 'income_statement', '营业收入', '营业总收入')
        prev_op_cost = _get_field(raw_data, prev, 'income_statement', '营业成本')
        if prev_revenue and prev_op_cost:
            prev_gross_margin = (prev_revenue - prev_op_cost) / prev_revenue

    net_margin = _safe_div(profit, revenue)
    gross_margin = _safe_div(revenue - op_cost, revenue) if revenue else None
    roe = _safe_div(profit, equity)
    ar_turnover = _safe_div(revenue, receivable) if receivable else None

    # ── 1. 供应商议价能力 ──
    # 逻辑：毛利率高 → 对供应商压价能力强；预付款少 → 不依赖特定供应商
    gm_score = 0
    reasons_1 = []
    if gross_margin is not None:
        if gross_margin > 0.6:
            gm_score += 2
            reasons_1.append(f"毛利率 {gross_margin:.1%} 极高，对上游议价能力很强")
        elif gross_margin > 0.3:
            gm_score += 1
            reasons_1.append(f"毛利率 {gross_margin:.1%} 较高，对上游有一定议价能力")
        else:
            reasons_1.append(f"毛利率 {gross_margin:.1%} 偏低，上游成本压力较大")

    if prepayment is not None and revenue:
        prepay_ratio = prepayment / revenue
        if prepay_ratio < 0.02:
            gm_score += 1
            reasons_1.append("预付款占比极低，不依赖特定供应商")
        elif prepay_ratio > 0.05:
            gm_score -= 1
            reasons_1.append(f"预付款占比 {prepay_ratio:.1%} 较高，供应商集中度可能较高")

    level_1 = '强' if gm_score >= 2 else ('中' if gm_score >= 1 else '弱')

    # ── 2. 购买者议价能力 ──
    # 逻辑：应收账款少 → 回款快 → 对下游控制力强；营收增长稳 → 产品竞争力强
    score_2 = 0
    reasons_2 = []
    if ar_turnover is not None:
        if ar_turnover > 10:
            score_2 += 2
            reasons_2.append(f"应收账款周转率 {ar_turnover:.1f} 极高，回款能力强")
        elif ar_turnover > 3:
            score_2 += 1
            reasons_2.append(f"应收账款周转率 {ar_turnover:.1f} 良好")
        else:
            reasons_2.append(f"应收账款周转率 {ar_turnover:.1f} 偏低，下游占款较多")

    if prev_revenue and revenue:
        rev_growth = (revenue - prev_revenue) / prev_revenue
        if rev_growth > 0.1:
            score_2 += 1
            reasons_2.append(f"营收增长 {rev_growth:.1%}，产品市场竞争力强")
        elif rev_growth < 0:
            score_2 -= 1
            reasons_2.append(f"营收下滑 {rev_growth:.1%}，可能面临下游需求疲软")

    level_2 = '强' if score_2 >= 2 else ('中' if score_2 >= 1 else '弱')

    # ── 3. 新进入者壁垒 ──
    # 逻辑：ROE 和净利率越高 → 行业壁垒越高（新进入者难以获得同等回报）
    score_3 = 0
    reasons_3 = []
    if roe is not None:
        if roe > 0.25:
            score_3 += 2
            reasons_3.append(f"ROE {roe:.1%} 极高，行业壁垒高，新进入者难以复制")
        elif roe > 0.15:
            score_3 += 1
            reasons_3.append(f"ROE {roe:.1%} 较高，行业有一定壁垒")
        else:
            reasons_3.append(f"ROE {roe:.1%} 偏低，行业进入门槛可能不高")

    if net_margin is not None and net_margin > 0.3:
        score_3 += 1
        reasons_3.append(f"净利率 {net_margin:.1%} 极高，品牌/技术护城河深")

    level_3 = '强' if score_3 >= 2 else ('中' if score_3 >= 1 else '弱')

    # ── 4. 替代品抵御力 ──
    # 逻辑：营收稳定 + 现金流充裕 → 替代品抵御力强
    score_4 = 0
    reasons_4 = []
    if ocf and profit:
        ocf_profit_ratio = ocf / profit if profit else None
        if ocf_profit_ratio and ocf_profit_ratio > 1.0:
            score_4 += 1
            reasons_4.append("经营现金流充裕，盈利质量高，产品被替代风险低")
        elif ocf_profit_ratio and ocf_profit_ratio < 0.5:
            reasons_4.append("经营现金流偏低，需关注盈利质量")

    if prev_revenue and revenue:
        volatility = abs(revenue - prev_revenue) / prev_revenue
        if volatility < 0.1:
            score_4 += 1
            reasons_4.append("营收稳定，产品需求刚性强，替代品威胁低")
        elif volatility > 0.3:
            score_4 -= 1
            reasons_4.append("营收波动较大，可能面临替代品冲击")

    level_4 = '强' if score_4 >= 2 else ('中' if score_4 >= 1 else '弱')

    # ── 5. 行业竞争强度 ──
    # 逻辑：毛利率高 + 销售费用率低 → 竞争压力小
    score_5 = 0
    reasons_5 = []
    if gross_margin is not None:
        if gross_margin > 0.5:
            score_5 += 2
            reasons_5.append(f"毛利率 {gross_margin:.1%} 极高，竞争压力小")
        elif gross_margin > 0.3:
            score_5 += 1
            reasons_5.append(f"毛利率 {gross_margin:.1%} 尚可")
        else:
            reasons_5.append(f"毛利率 {gross_margin:.1%} 偏低，行业竞争激烈")

    if sales_fee and revenue:
        fee_ratio = sales_fee / revenue
        if fee_ratio < 0.05:
            score_5 += 1
            reasons_5.append(f"销售费用率仅 {fee_ratio:.1%}，无需大量营销投入")
        elif fee_ratio > 0.15:
            score_5 -= 1
            reasons_5.append(f"销售费用率 {fee_ratio:.1%} 较高，竞争激烈")

    level_5 = '强' if score_5 >= 2 else ('中' if score_5 >= 1 else '弱')

    forces = [
        {'name': '供应商议价能力', 'icon': '🏭', 'level': level_1,
         'emoji': _rate(level_1)[0], 'reason': '；'.join(reasons_1) if reasons_1 else '数据不足'},
        {'name': '购买者议价能力', 'icon': '🛒', 'level': level_2,
         'emoji': _rate(level_2)[0], 'reason': '；'.join(reasons_2) if reasons_2 else '数据不足'},
        {'name': '新进入者壁垒',   'icon': '🚪', 'level': level_3,
         'emoji': _rate(level_3)[0], 'reason': '；'.join(reasons_3) if reasons_3 else '数据不足'},
        {'name': '替代品抵御力',   'icon': '🔄', 'level': level_4,
         'emoji': _rate(level_4)[0], 'reason': '；'.join(reasons_4) if reasons_4 else '数据不足'},
        {'name': '行业竞争强度',   'icon': '⚔️', 'level': level_5,
         'emoji': _rate(level_5)[0], 'reason': '；'.join(reasons_5) if reasons_5 else '数据不足'},
    ]

    return forces
