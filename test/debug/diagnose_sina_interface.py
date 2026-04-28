#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detailed diagnosis of Sina interface data issue"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def diagnose_sina_interface():
    """Diagnose why Sina interface returns structure but no data"""
    print("=" * 80)
    print("SINA INTERFACE DETAILED DIAGNOSIS")
    print("=" * 80)

    try:
        import akshare as ak
        import pandas as pd

        print(f"AKShare版本: {getattr(ak, '__version__', 'Unknown')}")
        print()

        # 测试股票列表
        test_stocks = ["600519", "000858", "000001"]

        for stock_code in test_stocks:
            print(f"\n{'='*60}")
            print(f"测试股票: {stock_code}")
            print(f"{'='*60}")

            # 1. 测试新浪利润表接口
            print(f"\n1. 新浪利润表接口测试:")
            print(f"   调用: ak.stock_financial_report_sina('{stock_code}', symbol='利润表')")

            try:
                df_sina = ak.stock_financial_report_sina(stock_code, symbol="利润表")

                print(f"   返回类型: {type(df_sina)}")
                print(f"   是否为None: {df_sina is None}")

                if df_sina is not None:
                    print(f"   DataFrame形状: {df_sina.shape}")
                    print(f"   是否为空: {df_sina.empty}")
                    print(f"   列名数量: {len(df_sina.columns) if hasattr(df_sina, 'columns') else 'N/A'}")

                    if hasattr(df_sina, 'columns'):
                        print(f"   前10个列名: {list(df_sina.columns)[:10]}")

                    if hasattr(df_sina, 'index'):
                        print(f"   索引: {df_sina.index}")
                        print(f"   索引长度: {len(df_sina.index)}")

                    # 检查是否有实际数据
                    if hasattr(df_sina, 'shape') and df_sina.shape[0] > 0:
                        print(f"   第一行数据: {df_sina.iloc[0].to_dict() if len(df_sina) > 0 else 'No data'}")
                        print(f"   数据类型: {df_sina.dtypes.to_dict() if hasattr(df_sina, 'dtypes') else 'N/A'}")
                    else:
                        print(f"   ❌ 无实际数据")

                    # 检查是否有NaN值
                    if hasattr(df_sina, 'isnull'):
                        nan_count = df_sina.isnull().sum().sum()
                        print(f"   NaN值总数: {nan_count}")

                        if nan_count == df_sina.size:
                            print(f"   ❌ 所有值都是NaN")
                        elif nan_count > 0:
                            print(f"   ⚠️  包含NaN值")

                else:
                    print(f"   ❌ 返回None")

            except Exception as e:
                print(f"   ❌ 调用失败: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()

            # 2. 尝试不同的symbol参数
            print(f"\n2. 测试不同的symbol参数:")
            symbols_to_test = ["利润表", "资产负债表", "现金流量表", "income", "balance", "cash"]

            for symbol in symbols_to_test:
                try:
                    print(f"   尝试symbol='{symbol}':")
                    df_test = ak.stock_financial_report_sina(stock_code, symbol=symbol)
                    if df_test is not None and hasattr(df_test, 'shape'):
                        print(f"     ✅ 成功，形状: {df_test.shape}")
                        if df_test.shape[0] > 0:
                            print(f"     数据预览: {df_test.iloc[0].to_dict()}")
                        break
                    else:
                        print(f"     ❌ 失败或空数据")
                except Exception as e:
                    print(f"     ❌ 错误: {e}")

            # 3. 检查AKShare内部实现
            print(f"\n3. AKShare内部实现检查:")
            try:
                # 查看新浪接口的实现
                import inspect
                source = inspect.getsource(ak.stock_financial_report_sina)
                print(f"   函数源码前20行:")
                lines = source.split('\n')[:20]
                for i, line in enumerate(lines, 1):
                    print(f"     {i:2d}: {line}")

                # 检查函数参数
                sig = inspect.signature(ak.stock_financial_report_sina)
                print(f"   函数签名: {sig}")

            except Exception as e:
                print(f"   ❌ 无法获取源码: {e}")

            # 4. 直接网络请求测试
            print(f"\n4. 直接网络请求测试:")
            try:
                import requests
                from bs4 import BeautifulSoup

                # 新浪财经可能的URL
                sina_urls = [
                    f"http://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/{stock_code}.phtml",
                    f"http://vip.stock.finance.sina.com.cn/corp/view/vFD_FinanceSummary.php?stockid={stock_code}",
                    f"http://money.finance.sina.com.cn/corp/go.php/vFD_{stock_code}/stockid/{stock_code}.phtml"
                ]

                for url in sina_urls:
                    try:
                        print(f"   测试URL: {url}")
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                        response = requests.get(url, headers=headers, timeout=10)
                        print(f"     状态码: {response.status_code}")
                        print(f"     内容长度: {len(response.text)}")

                        if response.status_code == 200 and len(response.text) > 1000:
                            print(f"     ✅ 获取到内容")
                            # 检查是否包含财务数据
                            if '利润表' in response.text or '营业收入' in response.text:
                                print(f"     ✅ 包含财务数据关键词")
                            else:
                                print(f"     ⚠️  未发现财务数据关键词")
                                print(f"     内容预览: {response.text[:200]}...")
                        else:
                            print(f"     ❌ 无有效内容")

                    except Exception as url_error:
                        print(f"     ❌ URL测试失败: {url_error}")

            except Exception as net_error:
                print(f"   ❌ 网络测试失败: {net_error}")

    except Exception as e:
        print(f"诊断失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("新浪接口诊断完成")
    print("=" * 80)

if __name__ == "__main__":
    diagnose_sina_interface()