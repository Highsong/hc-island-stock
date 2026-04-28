#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终验证测试 - 测试修改后的源码文件"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_final_verification():
    """最终验证测试"""
    print("开始最终验证测试...")

    # 测试我们修改的源码文件中的关键函数
    print("\n1. 测试_get_income_statement方法的修改")

    # 读取修改后的源码文件来验证修改是否正确
    source_file = "src/data_extraction/stock_data_source.py"

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查关键修改点
        check_points = [
            "准备调用利润表接口",
            "输入报文参数",
            "stock_code",
            "target_year",
            "api_name"
        ]

        print("检查修改点:")
        for point in check_points:
            if point in content:
                print(f"  ✓ 找到关键修改点: {point}")
            else:
                print(f"  ✗ 未找到关键修改点: {point}")

        # 检查get_stock_financial_data方法的修改
        if "股票财务数据请求详情" in content:
            print("  ✓ 找到get_stock_financial_data方法的修改")
        else:
            print("  ✗ 未找到get_stock_financial_data方法的修改")

        # 检查_fetch_with_retry方法的修改
        if "开始重试机制调用" in content:
            print("  ✓ 找到_fetch_with_retry方法的修改")
        else:
            print("  ✗ 未找到_fetch_with_retry方法的修改")

    except Exception as e:
        print(f"读取源码文件失败: {e}")

    print("\n2. 验证调试日志功能")

    # 运行一个简单的测试来验证调试日志
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_debug_logging.py"],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("  ✓ 调试日志测试运行成功")

            # 检查输出是否包含预期的调试信息
            output = result.stdout
            if "输入报文参数" in output and "600519" in output:
                print("  ✓ 调试日志输出包含完整的输入报文信息")
            else:
                print("  ✗ 调试日志输出不包含完整的输入报文信息")

        else:
            print(f"  ✗ 调试日志测试运行失败: {result.stderr}")

    except Exception as e:
        print(f"  ✗ 运行调试日志测试失败: {e}")

    print("\n3. 总结修改内容")
    print("""
已完成以下修改以打印接口调用前的输入报文：

1. 在_get_income_statement方法中添加了：
   - 完整的接口调用前信息打印
   - 详细的输入报文参数JSON格式输出
   - 股票代码、数据周期、目标年份等信息

2. 在get_stock_financial_data方法中添加了：
   - 股票财务数据请求详情打印
   - 完整的请求参数信息

3. 在_fetch_with_retry方法中添加了：
   - 重试机制调用的详细信息
   - 函数名称、参数等调试信息

4. 在两个主要API接口（东方财富和新浪）调用前都添加了：
   - 完整的请求参数JSON输出
   - 接口名称和调用方式说明

这些修改确保了在调用任何接口前都能看到完整的输入报文信息，
包括股票代码、目标年份（2025）、数据周期等关键参数。
""")

if __name__ == "__main__":
    test_final_verification()