# 数据源策略文档

## 数据源优先级（股票分析模块）

```
雪球(Xueqiu) > AKShare(新浪/东方财富) > 示例数据(SampleDataSource)
```

由 `DataSourceManager` 实现责任链模式，按注册顺序依次尝试。

### 1. 雪球 (Xueqiu) — 最高优先级

**数据源类：** `XueqiuDataSource`（`src/data_extraction/xueqiu_data_source.py`）

**API 端点：**
| 数据 | 端点 |
|------|------|
| 利润表 | `/v5/stock/finance/cn/income.json` |
| 资产负债表 | `/v5/stock/finance/cn/balance.json` |
| 现金流量表 | `/v5/stock/finance/cn/cash_flow.json` |
| 公司简介 | `/v5/stock/f10/cn/company.json` |

**Cookie 要求：** 需要有效的 `xq_a_token` Cookie
- 文件位置：`config/XueQiuCookie.txt`
- 格式：`cookie=xq_a_token=xxxxx` 或直接 `xq_a_token=xxxxx`
- 过期检测：`is_available()` 调用 company.json，返回 `error_code: 400016` 表示过期

**字段映射：**
- 利润表：`total_revenue`→营业收入, `net_profit_atsopc`→归母净利润(优先), `net_profit`→普通净利润(备选)
- 资产负债表：`total_assets`→总资产, `total_liab`→总负债, `total_holders_equity`→所有者权益
- 现金流量表：`ncf_from_oa`→经营活动现金流

**返回值格式：** `[数值, 增长率]`，取第一个元素

### 2. AKShare (新浪/东方财富) — 备选

**数据源类：** `StockDataSource`（`src/data_extraction/stock_data_source.py`）

当雪球不可用时自动 fallback。使用 AKShare 库调用新浪/东方财富接口。

### 3. 示例数据 (SampleDataSource) — 兜底

**数据源类：** `SampleDataSource`（`data_extraction/sample_data_source.py`）

始终可用，返回模拟数据，确保页面不会空白。

---

## 投资组合模块（独立数据源）

**⚠️ 注意：投资组合模块使用独立的数据源调用链，与股票分析模块完全隔离。**

**文件：** `src/data_portfolio.py`

**雪球 API 调用（直接调用，不经过 DataSourceManager）：**
| 数据 | 端点 | 函数 |
|------|------|------|
| 实时行情 | `/v5/stock/quote.json?symbol=xxx&extend=detail` | `fetch_detail()` |
| 周K线 | `/v5/stock/chart/kline.json?period=week` | `fetch_kline()` |
| 年后复权K线 | `/v5/stock/chart/kline.json?period=year&type=after&count=-1` | `fetch_kline_year_after()` |
| 港币汇率 | `/v5/stock/chart/kline.json?symbol=FXHKDCNY` | `fetch_hkdcny()` |

**Cookie 检测：** `_check_cookie_expired()` 检查 `error_code: 400016`

---

## Cookie 过期处理流程

1. `is_available()` 返回 `False`
2. `DataSourceManager` 跳过雪球，尝试 AKShare
3. 日志输出：`[Xueqiu] ⚠️ Cookie 已过期！`
4. UI 显示：`st.warning()` 提示用户更新 Cookie

## 更新 Cookie 方法

**无需登录雪球**，直接获取：

1. 打开 https://xueqiu.com（不需要登录）
2. 按 F12 打开开发者工具 → Network 标签
3. 随便点击一个请求
4. 复制 Request Headers 中 Cookie 的 `xq_a_token` 值
5. 更新 `config/XueQiuCookie.txt`
6. 刷新页面
