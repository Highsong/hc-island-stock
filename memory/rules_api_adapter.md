---
name: API Adapter 封装规则
description: 所有外部 API 调用统一封装为 adapter 层
type: feedback
---

**规则：所有外部 API 统一封装为 adapter**

**Why:** 当前 API 调用散落在 data_portfolio.py 等文件中，难以维护、切换数据源、统计耗时。

**How to apply:**
- 所有外部 API 调用（雪球、腾讯、CDN 等）必须通过 `src/adapters/` 下的 adapter 函数调用
- 每个 adapter 函数统一返回结构，包含 `{data, source, elapsed_ms}`
- adapter 内部处理错误、重试、日志
- 业务层（data_portfolio.py 等）不直接调用 `requests.get`，只调用 adapter

**Adapter 结构建议：**
```
src/adapters/
  __init__.py    # 导出所有 adapter
  xueqiu.py      # 雪球 API（quote、kline）
  tencent.py     # 腾讯行情（汇率等）
  currency.py    # 汇率 CDN（备用）
```

**关于并发：** 先不加，避免被封禁。串联调用。
