@echo off
REM 财务分析系统启动脚本（带编码设置）

@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ========================================
echo    财务分析系统启动脚本
echo ========================================
echo.
echo 设置UTF-8编码环境...
echo Setting UTF-8 encoding environment...
echo.

REM 检查Python环境
echo 检查Python环境...
echo Checking Python environment...
python --version
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH
    echo [ERROR] Python not installed or not in PATH
    pause
    exit /b 1
)

echo.
REM 检查依赖
 echo 检查依赖包...
echo Checking dependencies...
python -c "import streamlit, pandas, plotly, akshare" 2>nul
if errorlevel 1 (
    echo [警告] 缺少必要的依赖包，正在安装...
    echo [WARNING] Missing required packages, installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        echo [ERROR] Dependency installation failed
        pause
        exit /b 1
    )
)

echo.
echo 依赖检查完成，启动应用...
echo Dependencies checked, starting application...
echo.
echo 应用将在浏览器中打开:
echo Application will open in browser:
echo http://localhost:8501
echo.
echo 按Ctrl+C停止应用
echo Press Ctrl+C to stop application
echo.
echo ========================================

cd /d %~dp0..
streamlit run src/app_new.py

if errorlevel 1 (
    echo.
    echo [错误] 应用启动失败，请检查错误信息
    echo [ERROR] Application failed to start, please check error messages
    pause
    exit /b 1
)