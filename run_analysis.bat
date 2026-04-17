@echo off
REM run_analysis.bat - 快速启动茅台年报分析系统
echo 🏮 茅台年报分析系统
echo ========================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装
    pause
    exit /b 1
)

REM 检查依赖
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo 📦 正在安装依赖...
    pip install -r requirements.txt
)

REM 检查PDF文件
if not exist "data\raw_pdfs\*.pdf" (
    echo ⚠️  未找到PDF文件，请将年报放入 data\raw_pdfs\ 目录
    echo 💡 支持的格式: 02MT2025年年报.pdf
    pause
)

echo 🚀 正在启动分析系统...
echo 📊 请在浏览器中访问: http://localhost:8501
echo.

streamlit run src\app.py

pause