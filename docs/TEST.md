# 测试指南

## 测试目录结构

```
test/
├── README.md           # 本文件
├── demos/              # 功能演示脚本
│   ├── demo_enhanced.py
│   ├── demo_financial_dashboard.py
│   ├── demo_quarterly_analysis.py
│   └── demo_stock_display.py
├── unit/               # 单元测试
│   ├── test_app.py
│   ├── test_main.py
│   ├── test_modification.py
│   └── test_network_fix.py
├── integration/        # 集成测试
│   ├── comprehensive_test.py
│   ├── extensive_test_suite.py
│   ├── final_system_test.py
│   ├── frontend_test.py
│   ├── full_test.py
│   ├── system_test.py
│   ├── ui_test.py
│   └── ultimate_test.py
└── debug/              # 调试脚本
    ├── test_akshare_calls.py
    ├── test_cached_data_fix.py
    ├── test_data_type_fix.py
    └── test_encoding_fix.py
```

## 运行方式

### 运行所有测试

```bash
# 从项目根目录
python -m pytest test/ -v
```

### 按类别运行

```bash
# 仅单元测试
python -m pytest test/unit/ -v

# 仅集成测试
python -m pytest test/integration/ -v

# 仅调试脚本（手动执行）
python test/debug/test_akshare_calls.py
```

### 运行单个脚本

```bash
# 集成测试
python test/integration/comprehensive_test.py

# 功能演示
python test/demos/demo_financial_dashboard.py

# 调试脚本
python test/debug/test_akshare_calls.py
```

## 测试类别说明

### demos/ — 功能演示

展示特定功能的运行效果，适合：
- 新功能验证
- 演示和教学
- 手动回归测试

### unit/ — 单元测试

测试单个模块/函数，适合：
- 验证财务指标计算逻辑
- 测试数据转换函数
- 适配器层 mock 测试

### integration/ — 集成测试

端到端流程测试，适合：
- 验证完整数据流（输入代码 → 输出分析）
- 多数据源切换测试
- UI 交互流程验证

### debug/ — 调试脚本

用于排查特定问题：
- `test_akshare_calls.py` — AKShare API 连通性测试
- `test_cached_data_fix.py` — 缓存数据验证
- `test_data_type_fix.py` — 数据类型问题排查
- `test_encoding_fix.py` — 编码问题排查

## 注意事项

1. **集成测试依赖网络**：需要能访问雪球/AKShare 接口
2. **调试脚本是手动工具**：不是自动化测试，直接 `python` 运行即可
3. **演示脚本可能需要 Streamlit 环境**：部分 demo 依赖 `st` 组件
