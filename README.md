# hc-island-stock

> 基于 Streamlit 的 A 股/港股价值投资分析平台。支持财务指标分析、杜邦分析、波特五力、趋势分析、智能评语生成，以及实盘投资组合跟踪。

## 功能概览

### 📊 股票分析页
- 输入股票代码（A 股）或名称，实时获取财务数据
- 核心财务指标：毛利率、净利率、ROE、资产负债率、流动比率等
- 杜邦分析拆解：净利率 × 资产周转率 × 权益乘数
- 波特五力行业竞争力分析
- 营收/利润/现金流趋势图（Plotly 交互式图表）
- 智能评语生成：基于盈利能力、成长性、流动性自动评分（A-D 级）

### 💼 我的投资组合页
- 持仓明细表格：股票代码、名称、持仓比例、当前市值
- 理想买点 / 卖点参考价
- 年内涨幅追踪
- 实盘净值 vs 对比基准（沪深 300）
- 年度收益记录：实盘年化 vs 指数年化

## 技术栈

| 组件 | 选型 |
|------|------|
| Web 框架 | Streamlit |
| 图表库 | Plotly |
| 数据源 | 雪球（财务数据）、AKShare（新浪/东方财富）、腾讯行情（港汇） |
| 缓存 | 本地 JSON 文件，7 天过期 |
| 分析模块 | 自研：杜邦分析、波特五力、趋势分析、智能评语 |

## 项目结构

```
hc-island-stock/
├── src/
│   ├── app_new.py              # 主入口（分析页）
│   ├── portfolio_view.py       # 投资组合页
│   ├── data_portfolio.py       # 投资组合数据逻辑
│   ├── adapters/               # 外部 API 适配层
│   │   ├── xueqiu.py           # 雪球行情 API
│   │   └── tencent.py          # 腾讯行情（港汇换算）
│   ├── analysis/               # 分析引擎
│   │   ├── financial_metrics.py    # 财务指标计算
│   │   ├── trend_analysis.py       # 趋势分析
│   │   ├── dupont_analysis.py      # 杜邦分析
│   │   ├── porter_five_forces.py   # 波特五力
│   │   └── insights_generator.py   # 智能评语生成
│   ├── data_extraction/        # 数据获取层
│   │   ├── stock_data_source.py    # AKShare 数据源
│   │   ├── xueqiu_data_source.py   # 雪球财务数据源
│   │   ├── sample_data_source.py   # 示例数据（兜底）
│   │   └── data_source_manager.py  # 数据源调度（责任链）
│   ├── visualization/          # 可视化
│   │   ├── dashboard_layout.py     # 页面布局/CSS
│   │   └── chart_generator.py      # Plotly 图表生成
│   └── utils/
│       └── cache_manager.py        # JSON 文件缓存
├── config/
│   ├── XueQiuCookie.txt        # 雪球认证 Cookie（需手动配置）
│   └── XueQiuCookie.example.txt
├── data/
│   ├── portfolio.json          # 持仓配置
│   └── cache/                  # 数据缓存目录
├── docs/                       # 详细文档
│   ├── ARCHITECTURE.md
│   ├── DATA_SOURCES.md
│   ├── CONFIG.md
│   └── TEST.md
├── test/                       # 测试与示例脚本
└── README.md
```

## 快速开始

详见 [QUICK_START.md](QUICK_START.md)

## 环境要求

- Python >= 3.9
- 依赖见 `requirements.txt`

## 文档

- [快速开始](QUICK_START.md) — 5 分钟上手
- [配置说明](docs/CONFIG.md) — Cookie 获取、持仓配置
- [架构设计](docs/ARCHITECTURE.md) — 数据流、模块关系
- [数据源说明](docs/DATA_SOURCES.md) — 数据获取优先级与降级策略
- [测试指南](docs/TEST.md) — 如何运行测试

## 数据源优先级

```
雪球（需 Cookie）> AKShare（新浪/东方财富）> 示例数据（兜底降级）
```

## 注意事项

1. **雪球 Cookie**：财务数据（资产负债表、利润表、现金流量表）重度依赖雪球 Cookie。未配置时自动降级到有瑕疵的 AKShare + 示例数据。
2. **网络环境**：AKShare 在某些网络环境下可能不稳定，系统会自动降级。
3. **港股支持**：组合页面的港股持仓通过腾讯行情获取港汇换算。

## License

MIT
