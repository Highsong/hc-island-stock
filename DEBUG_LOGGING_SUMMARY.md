# 调试日志功能修改总结

## 修改目标
针对股票600519的2025年利润表数据获取问题，添加详细的接口调用前输入报文打印功能，以便于调试和问题定位。

## 修改内容

### 1. `_get_income_statement` 方法修改

**文件**: `src/data_extraction/stock_data_source.py`

**修改位置**: 第275-349行

**添加的调试信息**:
- 接口调用前的完整信息打印
- 详细的输入报文参数（JSON格式）
- 股票代码、数据周期、目标年份等信息
- 接口调用时间戳

**关键代码**:
```python
# 打印接口调用前的完整输入报文
print(f"\n{'='*80}")
print(f"准备调用利润表接口")
print(f"股票代码: {stock_code}")
print(f"数据周期: {period}")
print(f"目标年份: 2025")
print(f"接口调用时间: {datetime.now().isoformat()}")
print(f"{'='*80}\n")

# 打印详细的输入报文信息
request_params = {
    "stock_code": stock_code,
    "period": period,
    "target_year": "2025",
    "api_name": "ak.stock_profit_sheet_by_report_em"
}
print(f"输入报文参数: {json.dumps(request_params, ensure_ascii=False, indent=2)}")
```

### 2. `get_stock_financial_data` 方法修改

**修改位置**: 第47-114行

**添加的调试信息**:
- 股票财务数据请求详情打印
- 完整的请求参数信息

**关键代码**:
```python
# 打印完整的输入报文信息
print(f"\n{'='*100}")
print(f"股票财务数据请求详情")
print(f"股票代码: {stock_code}")
print(f"开始年份: {start_year}")
print(f"结束年份: {end_year}")
print(f"数据周期: {period}")
print(f"强制刷新: {force_refresh}")
print(f"请求时间: {datetime.now().isoformat()}")
print(f"{'='*100}\n")
```

### 3. `_fetch_real_a_stock_data` 方法修改

**修改位置**: 第846-870行

**添加的调试信息**:
- A股财务数据获取的详细信息
- 股票代码标准化过程
- 各类型财务数据的获取进度

**关键代码**:
```python
print(f"\n{'-'*80}")
print(f"开始获取A股财务数据")
print(f"原始股票代码: {stock_code}")
print(f"标准化代码: {clean_code}")
print(f"开始年份: {start_year}")
print(f"结束年份: {end_year}")
print(f"数据周期: {period}")
print(f"{'-'*80}\n")
```

### 4. `_fetch_with_retry` 方法修改

**修改位置**: 第926-956行

**添加的调试信息**:
- 重试机制调用的详细信息
- 函数名称、参数等调试信息
- 每次重试的状态信息

**关键代码**:
```python
# 打印重试机制的详细请求信息
print(f"\n{'-'*60}")
print(f"开始重试机制调用")
print(f"函数名称: {func_name}")
print(f"股票代码: {stock_code}")
print(f"参数: {args}")
print(f"关键字参数: {kwargs}")
print(f"最大重试次数: {self.max_retries}")
print(f"{'-'*60}\n")
```

### 5. 新浪接口输入报文打印

**修改位置**: 第320-345行

**添加的调试信息**:
- 新浪接口的完整输入报文参数

**关键代码**:
```python
# 打印新浪接口的输入报文
sina_request_params = {
    "stock_code": stock_code,
    "symbol": "利润表",
    "period": period,
    "target_year": "2025",
    "api_name": "ak.stock_financial_report_sina"
}
print(f"新浪接口输入报文参数: {json.dumps(sina_request_params, ensure_ascii=False, indent=2)}")
```

## 测试结果

### 测试脚本执行结果

通过 `demo_complete_debug.py` 脚本测试，输出结果显示：

1. **东方财富接口**: 调用失败，错误为 `TypeError: 'NoneType' object is not subscriptable`
2. **新浪接口**: 调用成功，返回101条记录，83列数据

### 调试信息输出示例

```
准备调用利润表接口
股票代码: 600519
数据周期: year
目标年份: 2025
接口调用时间: 2026-04-18T16:39:53.006040

东方财富接口输入报文参数:
{
  "stock_code": "600519",
  "period": "year",
  "target_year": "2025",
  "api_name": "ak.stock_profit_sheet_by_report_em"
}

尝试东方财富利润表接口: 600519
调用: ak.stock_profit_sheet_by_report_em('600519')
结果: 接口调用失败 - TypeError: 'NoneType' object is not subscriptable

新浪接口输入报文参数:
{
  "stock_code": "600519",
  "symbol": "利润表",
  "period": "year",
  "target_year": "2025",
  "api_name": "ak.stock_financial_report_sina"
}

尝试新浪利润表接口: 600519
调用: ak.stock_financial_report_sina('600519', symbol='利润表')
结果: 成功获取 101 条记录
数据形状: (101, 83)
```

## 修改效果

### 1. 完整的输入报文信息
现在可以在调用任何接口前看到完整的输入报文信息，包括：
- 股票代码（600519）
- 目标年份（2025）
- 数据周期（year）
- API接口名称
- 调用时间戳

### 2. 详细的错误定位
通过详细的调试信息，可以快速定位：
- 哪个接口调用失败
- 失败的具体原因
- 重试机制的执行过程

### 3. 问题分析
根据调试输出，我们发现：
- 东方财富接口存在解析错误（'NoneType' object is not subscriptable）
- 新浪接口工作正常，可以成功获取数据
- 完整的输入报文信息有助于分析接口调用失败的原因

## 验证结果

所有修改点都已成功应用并通过验证：
- ✓ `_get_income_statement` 方法修改
- ✓ `get_stock_financial_data` 方法修改  
- ✓ `_fetch_with_retry` 方法修改
- ✓ 完整的输入报文参数打印
- ✓ 调试日志测试运行成功

## 总结

通过本次修改，我们成功实现了在接口调用前打印完整输入报文的功能，这将大大有助于：
1. 快速定位接口调用问题
2. 分析请求参数是否正确
3. 调试API调用失败的原因
4. 验证数据获取流程的完整性

修改后的代码能够清晰地展示每个接口调用的详细输入参数，为后续的问题排查和调试提供了有力支持。