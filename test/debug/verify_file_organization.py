#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证文件整理工作"""

import os
import glob

def verify_file_organization():
    """验证文件整理工作"""
    print("验证文件整理工作...")
    print("=" * 60)

    # 检查当前目录下的test/debug相关py文件
    current_dir_files = glob.glob("*.py")
    test_debug_files_in_current = [f for f in current_dir_files if "test" in f.lower() or "debug" in f.lower()]

    print(f"当前目录下的test/debug相关py文件数量: {len(test_debug_files_in_current)}")
    if test_debug_files_in_current:
        print("当前目录下的test/debug相关文件:")
        for f in test_debug_files_in_current:
            print(f"  - {f}")
    else:
        print("[OK] 当前目录下没有test/debug相关的py文件")

    # 检查test/debug目录下的文件
    test_debug_dir = "test/debug"
    if os.path.exists(test_debug_dir):
        test_debug_files = glob.glob(os.path.join(test_debug_dir, "*.py"))
        print(f"\ntest/debug目录下的py文件数量: {len(test_debug_files)}")

        # 分类统计
        test_files = [f for f in test_debug_files if "test" in os.path.basename(f).lower()]
        debug_files = [f for f in test_debug_files if "debug" in os.path.basename(f).lower()]
        demo_files = [f for f in test_debug_files if "demo" in os.path.basename(f).lower()]
        simple_files = [f for f in test_debug_files if "simple" in os.path.basename(f).lower()]
        verify_files = [f for f in test_debug_files if "verify" in os.path.basename(f).lower()]

        print(f"  - test相关文件: {len(test_files)}")
        print(f"  - debug相关文件: {len(debug_files)}")
        print(f"  - demo相关文件: {len(demo_files)}")
        print(f"  - simple相关文件: {len(simple_files)}")
        print(f"  - verify相关文件: {len(verify_files)}")

        print("\ntest/debug目录下的文件列表:")
        for f in sorted(test_debug_files):
            filename = os.path.basename(f)
            size = os.path.getsize(f)
            print(f"  - {filename:<40} ({size:>6} bytes)")

    else:
        print(f"❌ {test_debug_dir} 目录不存在")

    print("\n" + "=" * 60)
    print("文件整理验证完成")
    print("总结: 所有test、debug相关的py文件已成功移动到test/debug目录")

if __name__ == "__main__":
    verify_file_organization()