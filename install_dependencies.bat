@echo off
echo 正在安装茅台年报分析系统依赖...

REM 安装基础依赖
pip install numpy
pip install pandas
pip install python-dateutil
pip install openpyxl

REM 安装可视化依赖
pip install plotly

REM 安装PDF处理依赖
pip install pdfplumber

REM 最后安装Streamlit（依赖最多）
pip install streamlit

echo 依赖安装完成！
echo 运行: streamlit run src/app.py