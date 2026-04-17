#!/usr/bin/env python3
# scripts/setup.py
import os
import subprocess
import sys

def setup_environment():
    """设置运行环境"""
    print("🚀 正在设置茅台年报分析系统...")

    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)

    # 安装依赖
    print("📦 安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装成功")
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败，请手动运行: pip install -r requirements.txt")
        sys.exit(1)

    # 创建必要的目录
    directories = [
        "data/raw_pdfs",
        "data/processed_data",
        "logs"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录: {directory}")

    # 检查示例数据
    sample_pdf = "data/raw_pdfs/02MT2025年年报.pdf"
    if os.path.exists(sample_pdf):
        print(f"✅ 检测到示例PDF文件: {sample_pdf}")
    else:
        print("⚠️  未检测到PDF文件，请将年报PDF放入 data/raw_pdfs/ 目录")

    print("\n🎉 环境设置完成！")
    print("\n📖 使用说明:")
    print("1. 将茅台年报PDF文件放入 data/raw_pdfs/ 目录")
    print("2. 运行: streamlit run src/app.py")
    print("3. 在浏览器中访问: http://localhost:8501")

if __name__ == "__main__":
    setup_environment()