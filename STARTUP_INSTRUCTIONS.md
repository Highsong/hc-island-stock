# 系统启动说明

## 问题修复总结

已修复批处理文件的兼容性问题，并提供了多种启动方式。

## 启动选项

### 选项1: 使用修复的批处理文件（推荐）

```cmd
start_final.bat --clear-cache
```

### 选项2: 使用Python脚本（跨平台兼容）

```cmd
python start_app.py --clear-cache
```

### 选项3: 使用PowerShell脚本（Windows专用）

```powershell
powershell -ExecutionPolicy Bypass -File start_app.ps1 -ClearCache
```

## 功能说明

### 缓存清理功能

所有启动方式都支持`--clear-cache`参数，会清理：
- `data/cache/` - 主缓存目录
- `data/processed_data/` - 处理后的数据
- `__pycache__` - Python缓存目录
- `*.pyc` - Python编译文件
- `*.tmp`, `*.temp` - 临时文件

### 进程管理

系统会自动：
1. 检测并关闭已运行的Streamlit实例
2. 启动新的Streamlit应用
3. 在浏览器中打开 http://localhost:8501

## 故障排除

### 如果批处理文件仍然报错

错误信息如：
- `'cp' 不是内部或外部命令`
- `'ho' 不是内部或外部命令`

这通常是由于文件编码或换行符问题导致的。请使用Python或PowerShell替代方案。

### 如果Python脚本报Unicode错误

在Windows上可能会遇到Unicode编码问题。解决方案：
1. 使用英文路径
2. 或者使用PowerShell版本

### 如果端口被占用

Streamlit默认使用端口8501。如果端口被占用：
1. 系统会自动选择其他端口（如8502、8503等）
2. 或者手动指定端口：`streamlit run src/app_new.py --server.port 8502`

## 推荐的启动方式

### 开发环境
```cmd
python start_app.py --clear-cache
```

### 生产环境
```cmd
start_final.bat
```

### Windows服务器
```powershell
powershell -ExecutionPolicy Bypass -File start_app.ps1 -ClearCache
```

## 文件说明

- `start_final.bat` - 修复后的批处理文件
- `start_app.py` - Python启动脚本（推荐）
- `start_app.ps1` - PowerShell启动脚本
- `clear_cache.py` - 独立的缓存清理脚本
- `clear_cache.bat` - 独立的缓存清理批处理文件

## 注意事项

1. **首次运行**: 建议使用`--clear-cache`参数确保干净的状态
2. **编码问题**: 如果遇到中文显示问题，请确保控制台编码为UTF-8
3. **权限问题**: 确保有权限读写`data/`目录
4. **依赖安装**: 确保已运行`pip install -r requirements.txt`

## 验证启动成功

1. 控制台显示 "You can now view your Streamlit app in your browser"
2. 自动打开浏览器访问 http://localhost:8501
3. 页面正常显示股票分析系统界面

如果以上步骤都正常，说明系统已成功启动！