#!/usr/bin/env python3
# run_analysis.py - 快速启动脚本
import os
import sys
import subprocess
import webbrowser
import time

def check_dependencies():
    """检查依赖"""
    try:
        import streamlit
        import pandas
        import plotly
        import pdfplumber
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("📦 正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ 依赖安装完成")
            return True
        except:
            print("❌ 依赖安装失败")
            return False

def check_pdf_files():
    """检查PDF文件"""
    pdf_dir = "data/raw_pdfs"
    if not os.path.exists(pdf_dir):
        print(f"❌ 目录不存在: {pdf_dir}")
        return False

    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"⚠️  未找到PDF文件，请将年报放入 {pdf_dir} 目录")
        print("💡 支持的格式: 02MT2025年年报.pdf")
        return False

    print(f"✅ 找到 {len(pdf_files)} 个PDF文件")
    return True

def main():
    """主函数"""
    print("🏮 茅台年报分析系统")
    print("========================")
    print()

    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        return

    # 检查PDF文件
    if not check_pdf_files():
        input("按回车键退出...")
        return

    print("🚀 正在启动分析系统...")
    print("📊 即将打开浏览器...")
    print()

    # 启动Streamlit
    try:
        # 在后台启动浏览器
        webbrowser.open('http://localhost:8501')

        # 启动Streamlit应用
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/app.py"
        ], check=True)

    except KeyboardInterrupt:
        print("\n👋 系统已关闭")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()