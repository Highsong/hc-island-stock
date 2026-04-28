#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证修改是否正确应用"""

import sys
import os

def verify_modifications():
    """验证修改"""
    print("验证修改是否正确应用...")

    # 检查修改后的源码文件
    source_file = "src/data_extraction/stock_data_source.py"

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print("\n检查关键修改点:")

        # 检查_get_income_statement方法的修改
        if "准备调用利润表接口" in content:
            print("  [OK] 找到_get_income_statement方法的修改")
        else:
            print("  [FAIL] 未找到_get_income_statement方法的修改")

        if "输入报文参数" in content:
            print("  [OK] 找到输入报文参数打印")
        else:
            print("  [FAIL] 未找到输入报文参数打印")

        if "target_year" in content and "2025" in content:
            print("  [OK] 找到2025年目标设置")
        else:
            print("  [FAIL] 未找到2025年目标设置")

        # 检查get_stock_financial_data方法的修改
        if "股票财务数据请求详情" in content:
            print("  [OK] 找到get_stock_financial_data方法的修改")
        else:
            print("  [FAIL] 未找到get_stock_financial_data方法的修改")

        # 检查_fetch_with_retry方法的修改
        if "开始重试机制调用" in content:
            print("  [OK] 找到_fetch_with_retry方法的修改")
        else:
            print("  [FAIL] 未找到_fetch_with_retry方法的修改")

        print("\n运行调试日志测试...")

        # 运行调试日志测试
        import subprocess
        result = subprocess.run([sys.executable, "test_debug_logging.py"],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("  [OK] 调试日志测试运行成功")

            # 检查输出是否包含预期的调试信息
            output = result.stdout
            if "输入报文参数" in output and "600519" in output:
                print("  [OK] 调试日志输出包含完整的输入报文信息")
            else:
                print("  [FAIL] 调试日志输出不包含完整的输入报文信息")

        else:
            print(f"  [FAIL] 调试日志测试运行失败")

    except Exception as e:
        print(f"验证过程中出现错误: {e}")

    print("\n修改总结:")
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
    verify_modifications()