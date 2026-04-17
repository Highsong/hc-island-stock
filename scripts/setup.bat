@echo off
REM scripts/setup.bat
echo 🚀 正在设置茅台年报分析系统...

REM 检查Python版本
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    exit /b 1
)

REM 安装依赖
echo 📦 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    exit /b 1
)

REM 创建目录
mkdir data\raw_pdfs 2>nul
mkdir data\processed_data 2>nul
mkdir logs 2>nul
echo ✅ 创建必要目录

REM 检查PDF文件
if exist "data\raw_pdfs\*.pdf" (
    echo ✅ 检测到PDF文件
) else (
    echo ⚠️  请将年报PDF放入 data\raw_pdfs\ 目录
)

echo.
echo 🎉 环境设置完成！
echo.
echo 📖 使用说明:
echo 1. 将茅台年报PDF文件放入 data\raw_pdfs\ 目录
echo 2. 运行: streamlit run src\app.py
echo 3. 在浏览器中访问: http://localhost:8501

pause