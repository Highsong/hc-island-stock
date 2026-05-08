# 更新日志

## v1.0.0 — 初始版本

### 功能
- 股票分析页：财务指标、杜邦分析、波特五力、趋势图、智能评语
- 投资组合页：周记持仓明细、年化收益对比
- 三数据源责任链：雪球 → AKShare → 示例数据兜底
- 本地 JSON 缓存（7 天过期）
- 港股港汇换算（腾讯行情接口）

### 模块
- `src/app_new.py` — 主入口（分析页）
- `src/portfolio_view.py` — 投资组合页
- `src/data_portfolio.py` — 投资组合数据逻辑
- `src/adapters/` — 雪球 + 腾讯行情适配层
- `src/analysis/` — 分析引擎（财务指标、趋势、杜邦、波特五力、智能评语）
- `src/data_extraction/` — 数据获取层（三数据源 + 调度器）
- `src/visualization/` — 可视化（布局 + Plotly 图表）
- `src/utils/cache_manager.py` — JSON 文件缓存
