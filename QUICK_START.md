# 快速开始

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

核心依赖：`streamlit` `plotly` `akshare` `pandas` `numpy` `requests`

## 2. 启动应用

```bash
streamlit run src/app_new.py
```

浏览器自动打开 `http://localhost:8501`。

## 3. 首次使用

### 3.1 配置雪球 Cookie（推荐）

财务数据（资产负债表/利润表/现金流量表）需要雪球 Cookie 才能获取完整数据。

1. 浏览器打开 <https://xueqiu.com> 并登录
2. 按 F12 打开开发者工具 → Application → Cookies → `https://xueqiu.com`
3. 复制 `xq_a_token` 的值
4. 将值写入 `config/XueQiuCookie.txt`（单行，无引号）

```
abc123def456...
```

> 没有 Cookie 也勉强能用，系统会降级到 AKShare + 示例数据，【且数据将变得不可信】。

### 3.2 配置持仓（可选）

编辑 `data/portfolio.json`，格式见 [docs/CONFIG.md](docs/CONFIG.md)。

## 4. 使用

### 股票分析页

1. 左侧边栏输入股票代码（如 `000858`）或名称（如 `五粮液`）
2. 选择分析时间范围
3. 查看财务指标、趋势图表、杜邦分析、波特五力、智能评语

### 投资组合页

1. 左侧边栏点击「我的投资」
2. Tab 1「周记」：查看持仓明细、买点/卖点、年内涨幅
3. Tab 2「年化收益」：查看年度实盘收益 vs 指数对比

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 数据加载失败 | 检查网络；配置雪球 Cookie 获取更稳定的数据 |
| AKShare 报错 | 正常现象，系统会自动降级到示例数据 |
| 图表不显示 | 确保浏览器支持 JavaScript |
| 港股数据不准确 | 检查 `adapters/tencent.py` 港汇接口是否正常 |

## 下一步

- [配置说明](docs/CONFIG.md) — 详细的 Cookie 获取步骤、持仓配置格式
- [架构设计](docs/ARCHITECTURE.md) — 了解系统架构和数据流
- [数据源说明](docs/DATA_SOURCES.md) — 数据获取策略和降级机制
