# 架构设计

## 系统概述

hc-island-stock 是一个基于 Streamlit 的 Web 应用，采用两层页面架构：

- **股票分析页**（`app_new.py`）：单只股票的深度财务分析
- **投资组合页**（`portfolio_view.py`）：实盘持仓跟踪

两个页面通过侧边栏按钮切换，使用 `st.session_state["_page_mode"]` 控制。

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit Web UI                     │
│  ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │   股票分析页       │    │   投资组合页                  │ │
│  │   app_new.py      │    │   portfolio_view.py          │ │
│  └────────┬───────────┘    └──────────────┬──────────────┘ │
│           │                               │               │
│  ┌────────▼───────────┐    ┌──────────────▼──────────────┐ │
│  │   分析引擎           │    │   投资组合数据逻辑             │ │
│  │   analysis/         │    │   data_portfolio.py          │ │
│  └────────┬───────────┘    └──────────────┬──────────────┘ │
│           │                               │               │
│  ┌────────▼───────────────────────────────▼──────────────┐ │
│  │              数据获取层 data_extraction/               │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │         DataSourceManager（责任链调度）            │  │ │
│  │  │  雪球 → AKShare → 示例数据（兜底）                │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └────────────────────────┬──────────────────────────────┘ │
│                           │                                │
│  ┌────────────────────────▼──────────────────────────────┐ │
│  │              适配层 adapters/                          │ │
│  │  xueqiu.py（雪球）  │  tencent.py（腾讯行情/港汇）      │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  可视化 visualization/  │  缓存 utils/                  │ │
│  │  dashboard_layout.py    │  cache_manager.py             │ │
│  │  chart_generator.py     │  (JSON文件, 7天过期)          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 页面独立原则

> ⚠️ 关键约束：分析页和投资组合页必须保持独立。

- `app_new.py` 和 `portfolio_view.py` 各自管理自己的数据源管理器实例
- 两页之间不共享数据源管理器
- 所有外部 API 调用必须通过 `src/adapters/` 适配层，禁止在业务逻辑中直接使用 `requests.get`

## 数据流

### 股票分析页数据流

```
用户输入股票代码
       │
       ▼
DataSourceManager.get_financial_data()
       │
       ├─ 1. XueqiuDataSource（雪球 Cookie）
       │     └─ 成功 → 返回完整财务数据
       │
       ├─ 2. AKShareDataSource（新浪/东方财富）
       │     └─ 成功 → 返回可用数据
       │
       └─ 3. SampleDataSource（兜底）
             └─ 返回示例数据模板
       │
       ▼
分析引擎（analysis/）
  ├── financial_metrics.py  → 计算各项财务比率
  ├── trend_analysis.py     → 趋势分析
  ├── dupont_analysis.py    → 杜邦分析拆解
  ├── porter_five_forces.py → 波特五力
  └── insights_generator.py → 智能评语 + 综合评级
       │
       ▼
可视化（visualization/）
  ├── dashboard_layout.py   → 页面布局/CSS
  └── chart_generator.py    → Plotly 图表
       │
       ▼
Streamlit 渲染
```

### 投资组合页数据流

```
portfolio.json（持仓配置）
       │
       ▼
data_portfolio.py
  ├── load_portfolio()      → 读取持仓配置
  ├── get_weekly_data()     → 周记数据（市值/涨幅）
  └── get_annualized_data() → 年化收益数据
       │
       ▼
适配层（adapters/）
  ├── xueqiu.py  → fetch_detail_batch() 批量获取行情
  └── tencent.py → fetch_hkdcny_tencent() 港汇换算
       │
       ▼
portfolio_view.py 渲染
  ├── Tab 1: 周记 — 持仓明细表格
  └── Tab 2: 年化收益 — 年度对比
```

## 模块说明

### adapters/ — 外部 API 适配层

所有外部 HTTP 调用集中在此目录，业务逻辑不直接调用 `requests`。

| 文件 | 职责 |
|------|------|
| `xueqiu.py` | 雪球行情 API（批量获取股票详情、K线数据） |
| `tencent.py` | 腾讯行情 API（港股/人民币换算汇率） |

### analysis/ — 分析引擎

| 文件 | 职责 |
|------|------|
| `financial_metrics.py` | 计算毛利率、净利率、ROE、资产负债率、流动比率等 |
| `trend_analysis.py` | 营收/利润/现金流趋势分析 |
| `dupont_analysis.py` | 杜邦分析：ROE = 净利率 × 资产周转率 × 权益乘数 |
| `porter_five_forces.py` | 波特五力行业竞争力评估 |
| `insights_generator.py` | 智能评语生成 + 综合评级（A-D 级，9 分制） |

### data_extraction/ — 数据获取层

| 文件 | 职责 |
|------|------|
| `stock_data_source.py` | AKShare 数据源（新浪/东方财富） |
| `xueqiu_data_source.py` | 雪球财务数据源（需 Cookie） |
| `sample_data_source.py` | 示例数据源（兜底降级） |
| `data_source_manager.py` | 责任链调度器，按优先级依次尝试各数据源 |

### visualization/ — 可视化

| 文件 | 职责 |
|------|------|
| `dashboard_layout.py` | Streamlit 页面布局、CSS 样式 |
| `chart_generator.py` | Plotly 图表生成（折线图、柱状图、雷达图等） |

## 缓存策略

- 位置：`data/cache/` 目录
- 格式：JSON 文件
- 过期：7 天
- 管理：`utils/cache_manager.py`

## 设计模式

### 责任链模式（数据源）

`DataSourceManager` 按优先级依次尝试各数据源，第一个成功返回的作为结果：

```
XueqiuDataSource → AKShareDataSource → SampleDataSource
```

### 适配器模式（外部 API）

所有外部 API 调用通过 `adapters/` 层封装，业务逻辑只调用适配器的公开函数。
