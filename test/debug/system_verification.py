#!/usr/bin/env python3
"""
系统验证脚本 - 验证股票分析系统的完整功能
"""

import sys
import os
import subprocess

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查依赖包...")
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'akshare', 'numpy'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - 未安装")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("✅ 所有依赖包已安装")
        return True

def check_file_structure():
    """检查文件结构"""
    print("\n📁 检查文件结构...")

    required_files = [
        'src/app_new.py',
        'src/data_extraction/stock_data_source.py',
        'src/analysis/financial_metrics.py',
        'src/analysis/insights_generator.py',
        'src/visualization/chart_generator.py',
        'src/utils/cache_manager.py',
        'requirements.txt'
    ]

    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - 文件不存在")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n⚠️  缺少文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 文件结构完整")
        return True

def test_core_functionality():
    """测试核心功能"""
    print("\n⚙️  测试核心功能...")

    try:
        from app_new import DataProcessor
        from data_extraction.stock_data_source import StockDataSource
        from analysis.insights_generator import InsightsGenerator

        # 测试数据处理器
        processor = DataProcessor()
        result = processor.process_stock_data('600519', '2020', '2024', 'year')

        if not result or not result.get('periods'):
            print("  ❌ 数据处理器测试失败")
            return False
        print(f"  ✅ 数据处理器 - 成功处理 {len(result['periods'])} 个周期")

        # 测试数据源
        ds = StockDataSource()
        stock_info = ds.get_stock_info('600519')
        if not stock_info or 'name' not in stock_info:
            print("  ❌ 数据源测试失败")
            return False
        print(f"  ✅ 数据源 - 成功获取股票信息: {stock_info.get('name')}")

        # 测试洞察生成
        ig = InsightsGenerator()
        insights = ig.generate_comprehensive_report(result.get('trend_analysis', {}))
        if not insights:
            print("  ❌ 洞察生成测试失败")
            return False
        print(f"  ✅ 洞察生成 - 成功生成 {len(insights)} 个洞察")

        print("✅ 核心功能测试完成")
        return True

    except Exception as e:
        print(f"  ❌ 核心功能测试异常: {e}")
        return False

def main():
    """主验证函数"""
    print("🚀 开始系统验证...")
    print("=" * 50)

    all_passed = True

    # 检查依赖
    if not check_dependencies():
        all_passed = False

    # 检查文件结构
    if not check_file_structure():
        all_passed = False

    # 测试核心功能
    if not test_core_functionality():
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 系统验证通过！")
        print("\n💡 接下来可以：")
        print("  1. 运行 streamlit run src/app_new.py 启动应用")
        print("  2. 在浏览器中访问 http://localhost:8501")
    else:
        print("❌ 系统验证失败，请修复上述问题")

    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)