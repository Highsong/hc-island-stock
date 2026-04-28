#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试净利润率修复的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_profit_margin_calculation():
    """测试净利润率计算是否正确"""
    print("开始测试净利润率计算修复...")

    try:
        # 模拟有问题的数据（单位：元）
        revenue_yuan = 1688.3810251479001  # 营业收入（元）
        profit_yuan = 85310324833.67      # 净利润（元）

        # 转换为亿元
        revenue_billion = revenue_yuan / 100000000  # 0.01688亿元
        profit_billion = profit_yuan / 100000000    # 853.103亿元

        # 计算净利润率
        profit_margin = profit_billion / revenue_billion if revenue_billion > 0 else 0

        print(f"原始数据:")
        print(f"  营业收入: {revenue_yuan:.2f}元 = {revenue_billion:.4f}亿元")
        print(f"  净利润: {profit_yuan:.2f}元 = {profit_billion:.3f}亿元")
        print(f"  计算出的净利润率: {profit_margin:.1%}")

        # 验证结果是否合理
        if 0 <= profit_margin <= 2.0:  # 净利润率应该在0-200%之间
            print("   [OK] 净利润率计算结果合理")
            return True
        else:
            print(f"   [FAIL] 净利润率异常: {profit_margin:.1%}")
            return False

    except Exception as e:
        print(f"   [ERROR] 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_new_profit_margin():
    """测试app_new.py中的净利润率计算"""
    print("\n测试app_new.py中的净利润率计算...")

    try:
        from src.app_new import DataProcessor

        # 创建测试数据（模拟原始数据，单位：元）
        test_raw_data = {
            '2025': {
                'income_statement': {
                    '营业收入': [1688.3810251479001],  # 单位：元
                    '净利润': [85310324833.67]         # 单位：元
                },
                'balance_sheet': {
                    '总资产': [2000000000],
                    '总负债': [600000000],
                    '所有者权益': [1400000000],
                    '流动资产': [1200000000],
                    '流动负债': [400000000],
                    '存货': [200000000]
                }
            }
        }

        # 创建DataProcessor实例
        processor = DataProcessor()

        # 测试_get_latest_period_data方法
        periods = ['2025']
        latest_data = processor._get_latest_period_data(test_raw_data, {}, periods)

        if latest_data and 'key_metrics' in latest_data:
            profit_margin = latest_data['key_metrics'].get('profit_margin', 0)
            print(f"  计算出的净利润率: {profit_margin:.1%}")

            # 验证结果
            if 0 <= profit_margin <= 2.0:
                print("   [OK] app_new.py净利润率计算正确")
                return True
            else:
                print(f"   [FAIL] app_new.py净利润率异常: {profit_margin:.1%}")
                return False
        else:
            print("   [FAIL] 无法获取最新期间数据")
            return False

    except Exception as e:
        print(f"   [ERROR] 测试app_new.py时出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("净利润率修复测试")
    print("=" * 60)

    test1_success = test_profit_margin_calculation()
    test2_success = test_app_new_profit_margin()

    overall_success = test1_success and test2_success

    print("\n" + "=" * 60)
    print(f"测试结果: {'成功' if overall_success else '失败'}")
    print("=" * 60)

    if overall_success:
        print("✅ 净利润率修复验证通过！")
        print("修复前: 5052788651.6%")
        print("修复后: 合理范围内的百分比")
    else:
        print("❌ 净利润率修复存在问题，需要进一步检查")

    sys.exit(0 if overall_success else 1)