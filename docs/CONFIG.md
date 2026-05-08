# 配置说明

## 雪球 Cookie 配置

财务数据（资产负债表/利润表/现金流量表）依赖雪球 Cookie。

### 获取步骤

1. 用浏览器打开 <https://xueqiu.com>
2. 登录雪球账号（免费注册即可）
3. 按 `F12` 打开开发者工具
4. 切到 **Application** 标签 → **Cookies** → `https://xueqiu.com`
5. 找到名为 `xq_a_token` 的 Cookie
6. 复制其 Value 值
7. 粘贴到 `config/XueQiuCookie.txt` 文件中（单行，无引号、无空格）

### 文件示例

`config/XueQiuCookie.txt` 内容：
```
abc123def456ghi789...
```

### 注意事项

- Cookie 会过期，如果财务数据突然无法加载，重新获取即可
- `config/XueQiuCookie.example.txt` 是示例文件，不要直接修改它
- 没有 Cookie 也能运行，系统会降级到 AKShare + 示例数据

## 持仓配置

编辑 `data/portfolio.json` 配置你的实盘持仓。

### JSON 结构

```json
{
  "holdings": [
    {
      "code": "000858",
      "exchange": "SZ",
      "name": "五粮液",
      "weight": 0.25,
      "buy_price": 135.0,
      "sell_target": 200.0,
      "shares": 1000
    }
  ],
  "nav": {
    "2024-01-01": 1.0,
    "2024-06-01": 1.12
  },
  "annual_records": [
    {
      "year": 2024,
      "portfolio_return": 0.15,
      "index_return": 0.08,
      "portfolio_nav": 1.15,
      "index_nav": 1.08
    }
  ]
}
```

### 字段说明

#### holdings（持仓数组）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 股票代码（纯数字） |
| exchange | string | 是 | 交易所：`SZ`（深圳）、`SH`（上海）、`HK`（港股） |
| name | string | 是 | 股票名称 |
| weight | number | 是 | 持仓比例（0-1 之间） |
| buy_price | number | 否 | 理想买点（元） |
| sell_target | number | 否 | 年内卖点（元） |
| shares | number | 否 | 持仓股数 |

#### nav（净值记录）

键值对格式：`"日期": 净值倍数`

- 日期格式：`YYYY-MM-DD`
- 净值：相对于初始资金的倍数（1.0 = 初始值）

#### annual_records（年度记录数组）

| 字段 | 类型 | 说明 |
|------|------|------|
| year | number | 年份 |
| portfolio_return | number | 当年涨幅（0.15 = 15%） |
| index_return | number | 指数当年涨幅 |
| portfolio_nav | number | 累计净值 |
| index_nav | number | 指数累计净值 |

### 示例配置

以下是一个包含 A 股和港股的示例：

```json
{
  "holdings": [
    {
      "code": "000858",
      "exchange": "SZ",
      "name": "五粮液",
      "weight": 0.20,
      "buy_price": 130.0,
      "sell_target": 200.0,
      "shares": 800
    },
    {
      "code": "00700",
      "exchange": "HK",
      "name": "腾讯控股",
      "weight": 0.15,
      "buy_price": 350.0,
      "sell_target": 500.0,
      "shares": 500
    }
  ],
  "nav": {
    "2024-01-01": 1.0
  },
  "annual_records": []
}
```

## 自动加载规则

以下文件/目录会自动加载（无需额外配置）：

- `config/XueQiuCookie.txt` — 启动时自动读取
- `data/portfolio.json` — 进入投资组合页时自动读取
- `data/cache/` — 缓存目录，自动创建
