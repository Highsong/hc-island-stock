#!/usr/bin/env python3
"""
清除缓存并重新启动应用
"""

import os
import sys
import subprocess
import time
import signal

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.cache_manager import cache_manager

def clear_all_cache():
    """清除所有缓存"""
    print("🧹 清除缓存...")
    try:
        # 清除所有缓存
        cache_manager.clear_all()
        print("✅ 缓存清除完成")
    except Exception as e:
        print(f"❌ 清除缓存时出错: {e}")

def kill_streamlit_processes():
    """终止所有streamlit进程"""
    print("🔄 终止现有Streamlit进程...")
    try:
        # 使用taskkill终止streamlit进程
        subprocess.run(['taskkill', '/f', '/im', 'streamlit.exe'],
                      capture_output=True, shell=True)
        print("✅ Streamlit进程已终止")
    except Exception as e:
        print(f"⚠️ 终止进程时出错: {e}")

def main():
    """主函数"""
    print("🚀 开始清除缓存并重启应用...")
    print("=" * 50)

    # 清除缓存
    clear_all_cache()

    # 终止streamlit进程
    kill_streamlit_processes()

    print("\n💡 现在可以手动启动应用:")
    print("   streamlit run src/app_new.py")
    print("\n📝 或者运行:")
    print("   python start_app.py")

if __name__ == '__main__':
    main()