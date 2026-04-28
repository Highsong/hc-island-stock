# -*- coding: utf-8 -*-
# src/utils/cache_manager.py
"""
缓存管理工具
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
# Safe file operations to handle encoding issues
def safe_file_read(file_path: str) -> tuple[bool, Optional[Dict[str, Any]]]:
    """Safely read file with encoding handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        return True, content
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = json.load(f)
            return True, content
        except Exception as e:
            print(f"Failed to read file with GBK encoding: {e}")
            return False, None
    except Exception as e:
        print(f"Failed to read file {file_path}: {e}")
        return False, None

def safe_file_write(file_path: str, data: Dict[str, Any], ensure_ascii: bool = False) -> bool:
    """Safely write file with encoding handling"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=2)
        return True
    except Exception as e:
        print(f"Failed to write file {file_path}: {e}")
        return False

class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_key(self, *args) -> str:
        """生成缓存键"""
        key_string = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_file(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, *args) -> Optional[Dict[str, Any]]:
        """获取缓存数据"""
        cache_key = self._get_cache_key(*args)
        cache_file = self._get_cache_file(cache_key)

        if not os.path.exists(cache_file):
            return None

        try:
            # 使用安全的文件读取，处理编码问题
            success, data = safe_file_read(cache_file)
            if not success:
                return None

            # 检查缓存是否过期（7天）
            cache_time = datetime.fromisoformat(data.get('cache_time', '2000-01-01'))
            if datetime.now() - cache_time > timedelta(days=7):
                os.remove(cache_file)
                return None

            return data.get('content')

        except Exception as e:
            print(f"读取缓存失败: {e}")
            return None

    def set(self, content: Dict[str, Any], *args):
        """设置缓存数据"""
        cache_key = self._get_cache_key(*args)
        cache_file = self._get_cache_file(cache_key)

        try:
            cache_data = {
                'cache_time': datetime.now().isoformat(),
                'content': content
            }

            # 使用安全的文件写入，处理编码问题
            success = safe_file_write(cache_file, cache_data, ensure_ascii=False)
            if not success:
                print(f"安全写入失败，尝试ASCII转义")
                # 降级到ASCII转义模式
                success = safe_file_write(cache_file, cache_data, ensure_ascii=True)

        except Exception as e:
            print(f"保存缓存失败: {e}")

    def clear_expired(self):
        """清理过期缓存"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        # 使用安全的文件读取
                        success, data = safe_file_read(file_path)
                        if success:
                            cache_time = datetime.fromisoformat(data.get('cache_time', '2000-01-01'))
                            if datetime.now() - cache_time > timedelta(days=7):
                                os.remove(file_path)
                                print(f"清理过期缓存: {filename}")

                    except Exception as e:
                        print(f"处理缓存文件 {filename} 时出错: {e}")

        except Exception as e:
            print(f"清理缓存时出错: {e}")

    def clear_all(self):
        """清理所有缓存"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
            print("已清理所有缓存")
        except Exception as e:
            print(f"清理所有缓存时出错: {e}")

# 全局缓存管理器实例
cache_manager = CacheManager()