#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the actual webpage content to understand the issue"""

import requests
from bs4 import BeautifulSoup

def check_webpage_content():
    """Check what's actually returned by the East Money website"""
    print("=" * 80)
    print("CHECKING ACTUAL WEBPAGE CONTENT")
    print("=" * 80)

    url = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index"
    params = {"type": "web", "code": "600519"}  # Note: not using .lower()

    print(f"请求URL: {url}")
    print(f"参数: {params}")
    print()

    try:
        # 设置请求头模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应内容类型: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"响应编码: {response.encoding}")
        print()

        if response.status_code == 200:
            # 尝试不同的编码
            encodings_to_try = ['utf-8', 'gbk', 'gb2312', 'latin1']

            for encoding in encodings_to_try:
                try:
                    response.encoding = encoding
                    content = response.text
                    print(f"使用编码 {encoding} 成功")
                    print(f"内容长度: {len(content)}")
                    print(f"内容前500字符:")
                    print("-" * 50)
                    print(content[:500])
                    print("-" * 50)
                    print()

                    # 解析HTML
                    soup = BeautifulSoup(content, 'html.parser')

                    # 查找hidctype元素
                    hidctype_element = soup.find(attrs={"id": "hidctype"})
                    print(f"查找 hidctype 元素结果: {hidctype_element}")

                    if hidctype_element:
                        print(f"元素值: {hidctype_element.get('value')}")
                    else:
                        print("❌ 未找到 hidctype 元素")

                        # 查找所有input元素
                        all_inputs = soup.find_all('input')
                        print(f"\n所有input元素 ({len(all_inputs)} 个):")
                        for i, inp in enumerate(all_inputs[:10]):  # 只显示前10个
                            print(f"  {i+1}. id: {inp.get('id')}, name: {inp.get('name')}, value: {inp.get('value')}")

                        # 查找包含"ctype"的元素
                        ctype_elements = soup.find_all(string=lambda text: 'ctype' in str(text).lower())
                        print(f"\n包含'ctype'的文本元素 ({len(ctype_elements)} 个):")
                        for elem in ctype_elements[:5]:
                            print(f"  - {elem}")

                        # 查看页面标题
                        title = soup.find('title')
                        print(f"\n页面标题: {title.text if title else 'No title'}")

                        # 检查是否有错误信息
                        error_elements = soup.find_all(string=lambda text: 'error' in str(text).lower() or '错误' in str(text) or '异常' in str(text))
                        if error_elements:
                            print(f"\n可能的错误信息:")
                            for error in error_elements[:3]:
                                print(f"  - {error.strip()}")

                    break  # 成功解析后跳出循环

                except UnicodeDecodeError as e:
                    print(f"使用编码 {encoding} 失败: {e}")
                    continue

        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.content[:500]}")

    except Exception as e:
        print(f"请求异常: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)

if __name__ == "__main__":
    check_webpage_content()