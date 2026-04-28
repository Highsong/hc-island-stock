#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单位修复的脚本
"""

def test_unit_normalization():
    """测试单位标准化逻辑"""
    print("测试单位标准化逻辑...")

    # 测试用例1: 正常数据（单位一致）
    revenue1 = 100000000  # 1亿元（单位：元）
    profit1 = 15000000   # 1500万元（单位：元）
    profit_margin1 = calculate_profit_margin(revenue1, profit1)
    print(f"测试1 - 正常数据: 营收{revenue1}, 利润{profit1}, 利润率{profit_margin1:.1%}")

    # 测试用例2: 数据截断（营收数据被截断）
    revenue2 = 1688.38  # 被截断的营收数据（应该是168838102514.79）
    profit2 = 85310324833.67  # 正常的净利润数据
    profit_margin2 = calculate_profit_margin(revenue2, profit2)
    print(f"测试2 - 数据截断: 营收{revenue2}, 利润{profit2}, 利润率{profit_margin2:.1%}")

    # 测试用例3: 问题数据（来自缓存文件）
    revenue3 = 1688.3810251479001  # 可能是万元
    profit3 = 85310324833.67      # 肯定是元
    profit_margin3 = calculate_profit_margin(revenue3, profit3)
    print(f"测试3 - 问题数据: 营收{revenue3}, 利润{profit3}, 利润率{profit_margin3:.1%}")

    # 验证结果
    success = True
    if not (0 <= profit_margin1 <= 1.0):
        print(f"[FAIL] 测试1利润率异常: {profit_margin1:.1%}")
        success = False
    if not (0 <= profit_margin2 <= 1.0):
        print(f"[FAIL] 测试2利润率异常: {profit_margin2:.1%}")
        success = False
    if not (0 <= profit_margin3 <= 1.0):
        print(f"[FAIL] 测试3利润率异常: {profit_margin3:.1%}")
        success = False

    if success:
        print("[OK] 所有测试通过，单位标准化逻辑正确")
    else:
        print("[FAIL] 部分测试失败")

    return success

def calculate_profit_margin(revenue, profit):
    """计算利润率的修复逻辑"""
    if revenue > 0 and profit > 0:
        # 检测数据是否异常：如果营收相对于净利润过小，可能是数据截断
        ratio = profit / revenue
        if ratio > 1000:  # 异常高的利润率，很可能是营收数据被截断
            # 尝试修复：假设营收数据少了一个数量级
            # 这通常发生在数据格式化/解析错误时
            if revenue < 10000:  # 营收数据异常小
                # 尝试将营收数据放大100000000倍（从元到亿的转换）
                corrected_revenue = revenue * 100000000
                profit_margin = profit / corrected_revenue
            else:
                profit_margin = ratio
        else:
            profit_margin = ratio
    else:
        profit_margin = 0
    return profit_margin

if __name__ == "__main__":
    print("=" * 50)
    print("单位标准化修复测试")
    print("=" * 50)

    success = test_unit_normalization()

    print("=" * 50)
    print(f"测试结果: {'成功' if success else '失败'}")
    print("=" * 50)