# API失败行为修复报告

## 问题描述

用户反馈：接口调用失败时，页面仍然显示数据（模拟数据），但要求是接口失败时不要展示任何数据。

## 根本原因

在`src/data_extraction/stock_data_source.py`中，当AKShare API调用失败时，系统会回退到生成和返回示例数据，而不是返回空数据。

## 修复内容

### 1. 修改主数据获取函数

**文件**: `src/data_extraction/stock_data_source.py`

**修改前** (第112-115行):
```python
# 如果API调用失败，返回示例数据（绝对不缓存）
result = self._generate_sample_data(stock_code, start_year, end_year)
print(f"使用示例数据（不缓存）: {stock_code}")
return result
```

**修改后**:
```python
# 如果API调用失败，不返回任何数据
print(f"API调用失败，不返回模拟数据: {stock_code}")
return {}
```

### 2. 修改A股数据获取函数

**修改前** (第163-167行):
```python
# 网络查询失败，使用示例数据（绝对不缓存）
result = self._generate_sample_data(stock_code, start_year, end_year)
print(f"使用示例数据（不缓存）: {stock_code}")
return result
```

**修改后**:
```python
# 网络查询失败，不返回任何数据
print(f"API调用失败，不返回数据: {stock_code}")
return {}
```

### 3. 修改港股数据获取函数

**修改前** (第201-205行):
```python
# 网络查询失败，使用示例数据（绝对不缓存）
result = self._generate_enhanced_sample_data(stock_code, start_year, end_year)
print(f"使用示例数据（不缓存）: {stock_code}")
return result
```

**修改后**:
```python
# 网络查询失败，不返回任何数据
print(f"API调用失败，不返回数据: {stock_code}")
return {}
```

### 4. 更新所有相关消息

将所有"使用示例数据"的消息更改为"不返回数据"，明确表示不会返回任何数据。

## 修复验证

### 代码检查
- ✅ 移除了所有`_generate_sample_data()`函数调用
- ✅ 移除了所有`_generate_enhanced_sample_data()`函数调用
- ✅ 保留了函数定义（以防将来需要）
- ✅ 所有失败路径现在都返回空字典`{}`

### 行为验证

**修复前**:
```
第一次点击: API失败 → 返回示例数据 → 页面显示模拟数据
第二次点击: API失败 → 返回示例数据 → 页面显示模拟数据
```

**修复后**:
```
第一次点击: API失败 → 返回空数据 → 页面无数据显示
第二次点击: API失败 → 返回空数据 → 页面无数据显示
```

## 当前状态

由于AKShare接口存在系统性问题，目前所有API调用都会失败：
- `stock_profit_sheet_by_report_em`: 'NoneType' object is not subscriptable
- `stock_balance_sheet_by_report_em`: 'NoneType' object is not subscriptable
- `stock_cash_flow_sheet_by_report_em`: 'NoneType' object is not subscriptable

因此，系统现在会：
1. 尝试调用AKShare API
2. API调用失败
3. 记录详细的错误日志
4. 返回空字典`{}`
5. 页面不显示任何数据

## 未来恢复

当AKShare API恢复正常时，系统会自动：
1. 成功获取真实数据
2. 缓存真实数据（仅在成功时）
3. 返回真实数据给页面
4. 页面显示真实财务数据

## 测试验证

可以通过以下方式验证修复效果：

1. **运行测试脚本**:
   ```bash
   python test_api_failure_behavior.py
   ```

2. **检查输出**: 应该显示"Got empty dict (no data returned)"

3. **观察页面**: 当API失败时，页面应该没有数据显示

## 总结

✅ **修复完成**: 接口调用失败时不再返回模拟数据，而是返回空数据
✅ **错误日志**: 仍然记录详细的API失败信息用于调试
✅ **缓存清理**: 保持原有的缓存清理逻辑
✅ **未来兼容**: 当API恢复时自动恢复正常功能

现在系统符合要求：**接口调用失败时，不展示任何数据**。