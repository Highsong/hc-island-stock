# 数据源说明

## 优先级链

数据获取采用责任链模式，按以下优先级依次尝试：

```
雪球（Xueqiu）> AKShare > 示例数据（Sample）
```

当高优先级数据源失败时，系统自动降级到下一个，确保始终有数据可展示。

## 数据源详解

### 1. 雪球（Xueqiu）— 最高优先级

**用途**：获取完整财务数据（资产负债表、利润表、现金流量表）

**依赖**：需要有效的雪球 Cookie（`xq_a_token`）

**实现**：`src/data_extraction/xueqiu_data_source.py`

**适配层**：`src/adapters/xueqiu.py`
- `fetch_detail_batch()` — 批量获取股票详情
- `fetch_kline_year_after()` — 获取年K线
- `fetch_kline_week_after()` — 获取周K线

**优点**：
- 数据完整，包含三张财务报表
- 更新及时

**缺点**：
- 需要手动获取并配置 Cookie
- Cookie 有过期风险
- 对 A 股财务数据覆盖有限（更适合港股）

### 2. AKShare — 中等优先级

**用途**：获取 A 股行情和部分财务数据

**依赖**：`akshare` Python 库，网络可访问新浪/东方财富接口

**实现**：`src/data_extraction/stock_data_source.py`

**数据来源**：
- 新浪财经（实时行情）
- 东方财富（财务数据）

**优点**：
- 无需认证
- A 股数据覆盖广

**缺点**：
- 某些网络环境下不稳定
- 接口可能随时变更
- 财务数据字段可能不完整

### 3. 示例数据（Sample）— 兜底降级

**用途**：当所有外部数据源都失败时，提供示例数据以保证页面可正常展示

**实现**：`src/data_extraction/sample_data_source.py`

**数据模板**：
- 营收：800 亿
- 净利率：35%
- 模拟 4 期财务数据

**用途**：
- 开发和演示环境
- 网络不可用时的兜底方案
- UI 功能验证

## 数据源调度器

`DataSourceManager`（`data_source_manager.py`）负责按优先级调度：

```python
# 伪代码
class DataSourceManager:
    def __init__(self):
        self.sources = [
            XueqiuDataSource(),    # 优先级 1
            AKShareDataSource(),   # 优先级 2
            SampleDataSource(),    # 优先级 3（兜底）
        ]

    def get_financial_data(self, symbol):
        for source in self.sources:
            try:
                data = source.fetch(symbol)
                if data:
                    return data
            except Exception:
                continue  # 降级到下一个
        return None  # 理论上不会到达（SampleDataSource 永远返回数据）
```

## 投资组合数据源

投资组合页使用独立的数据获取逻辑（`data_portfolio.py`），直接调用适配层：

| 数据 | 来源 |
|------|------|
| A 股行情 | `xueqiu.fetch_detail_batch()` |
| 港股行情 | `xueqiu.fetch_detail_batch()` |
| 港汇（HKD/CNY） | `tencent.fetch_hkdcny_tencent()` |

## 缓存机制

所有获取的数据都会缓存到 `data/cache/` 目录：

- **格式**：JSON 文件
- **过期时间**：7 天
- **键格式**：`{source}_{symbol}_{date}.json`
- **管理**：`utils/cache_manager.py`

缓存优先于网络请求，过期后才重新获取。

## 港汇换算

港股持仓的市值换算通过腾讯行情接口获取实时 HKD/CNY 汇率：

```
市值(CNY) = 市值(HKD) × 汇率
```

汇率接口：`adapters/tencent.py` → `fetch_hkdcny_tencent()`
