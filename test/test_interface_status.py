#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试当前接口调用状态
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_interface_calls():
    """测试接口调用状态"""
    print("=" * 60)
    print("接口调用状态测试")
    print("=" * 60)

    try:
        from src.data_extraction.stock_data_source import StockDataSource

        # 创建数据源实例
        data_source = StockDataSource()

        print("1. 测试股票信息获取...")
        try:
            stock_info = data_source.get_stock_info("600519")
            print(f"   [OK] 股票信息获取成功: {stock_info.get('name', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] 股票信息获取失败: {e}")

        print("\n2. 测试财务数据获取...")
        try:
            # 测试获取数据（这会触发接口调用）
            financial_data = data_source.get_stock_financial_data(
                "600519", "2023", "2024", "year"
            )

            if financial_data and len(financial_data) > 0:
                print(f"   [OK] 财务数据获取成功: {len(financial_data)} 个周期")

                # 检查数据质量
                for year, data in financial_data.items():
                    if isinstance(data, dict):
                        has_income = bool(data.get('income_statement'))
                        has_balance = bool(data.get('balance_sheet'))
                        has_cashflow = bool(data.get('cash_flow'))
                        print(f"   {year}年: 利润表{has_income}, 资产负债表{has_balance}, 现金流量表{has_cashflow}")
                        break
            else:
                print("   [WARN] 财务数据获取为空，可能使用示例数据")

        except Exception as e:
            print(f"   [FAIL] 财务数据获取失败: {e}")
            import traceback
            traceback.print_exc()

        print("\n3. 检查AKShare可用性...")
        try:
            import akshare as ak
            print(f"   [OK] AKShare已安装，版本: {getattr(ak, '__version__', 'Unknown')}")

            # 测试新浪接口
            print("\n4. 测试新浪接口...")
            try:
                df = ak.stock_financial_report_sina("600519", symbol="利润表")
                if df is not None and hasattr(df, 'shape'):
                    print(f"   [OK] 新浪利润表接口工作正常，返回 {df.shape[0]} 行数据")
                else:
                    print("   [FAIL] 新浪接口返回数据异常")
            except Exception as e:
                print(f"   [FAIL] 新浪接口调用失败: {e}")

        except ImportError:
            print("   [FAIL] AKShare未安装")
        except Exception as e:
            print(f"   [FAIL] AKShare检查失败: {e}")

        print("\n" + "=" * 60)
        print("接口状态检查完成")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_interface_calls()