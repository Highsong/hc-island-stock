#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detailed diagnosis of AKShare issue"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def diagnose_akshare_issue():
    """Diagnose the root cause of AKShare failure"""
    print("=" * 80)
    print("DETAILED AKShare ISSUE DIAGNOSIS")
    print("=" * 80)

    try:
        import akshare as ak
        import requests
        from bs4 import BeautifulSoup

        print(f"AKShare版本: {getattr(ak, '__version__', 'Unknown')}")
        print(f"AKShare路径: {ak.__file__}")

        # 查看AKShare内部代码
        print(f"\n1. 检查AKShare内部代码结构:")
        print("-" * 40)

        try:
            # 查看出问题的函数
            from akshare.stock_feature.stock_three_report_em import _stock_balance_sheet_by_report_ctype_em
            import inspect

            print("函数 _stock_balance_sheet_by_report_ctype_em 源码:")
            try:
                source = inspect.getsource(_stock_balance_sheet_by_report_ctype_em)
                print(source[:1000] + "..." if len(source) > 1000 else source)
            except Exception as e:
                print(f"无法获取源码: {e}")

        except Exception as e:
            print(f"无法导入相关函数: {e}")

        print(f"\n2. 尝试直接调用问题函数:")
        print("-" * 40)

        try:
            # 直接调用出问题的函数
            result = _stock_balance_sheet_by_report_ctype_em(symbol="600519")
            print(f"函数调用成功，返回: {result}")
        except Exception as e:
            print(f"函数调用失败: {type(e).__name__}: {e}")

            # 尝试获取网络请求的详细信息
            print(f"\n3. 网络请求诊断:")
            print("-" * 40)

            # 查看AKShare使用的URL
            try:
                # AKShare可能使用的URL模式
                test_urls = [
                    "http://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=600519",
                    "http://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/NewFinanceAnalysisAjax?companyType=&reportDateType=0&code=600519"
                ]

                for url in test_urls:
                    print(f"\n测试URL: {url}")
                    try:
                        response = requests.get(url, timeout=10)
                        print(f"HTTP状态码: {response.status_code}")
                        print(f"响应头: {dict(response.headers)}")
                        print(f"响应内容前500字符: {response.text[:500]}...")

                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            hidctype_element = soup.find(attrs={"id": "hidctype"})
                            print(f"查找 hidctype 元素: {hidctype_element}")
                            if hidctype_element:
                                print(f"元素值: {hidctype_element.get('value')}")
                            else:
                                print("❌ 未找到 hidctype 元素")
                                # 查找类似的元素
                                all_inputs = soup.find_all('input')
                                print(f"所有input元素: {[inp.get('id') for inp in all_inputs if inp.get('id')]}")

                    except Exception as req_error:
                        print(f"请求失败: {req_error}")

            except Exception as net_error:
                print(f"网络诊断失败: {net_error}")

        print(f"\n4. 新浪接口对比测试:")
        print("-" * 40)

        try:
            sina_result = ak.stock_financial_report_sina("600519", symbol="利润表")
            print(f"新浪接口调用成功，返回类型: {type(sina_result)}")
            if hasattr(sina_result, 'shape'):
                print(f"数据形状: {sina_result.shape}")
            if hasattr(sina_result, 'columns'):
                print(f"列名: {list(sina_result.columns)}")
        except Exception as sina_error:
            print(f"新浪接口也失败: {sina_error}")

    except Exception as e:
        print(f"诊断失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)

if __name__ == "__main__":
    diagnose_akshare_issue()