@echo off
cd /d %~dp0..
REM 设置Python环境编码
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 设置控制台代码页为UTF-8
chcp 65001 > nul

echo 环境编码已设置为UTF-8
echo Environment encoding set to UTF-8

REM 验证设置
python -c "import sys; print('Python默认编码:', sys.getdefaultencoding()); print('文件系统编码:', sys.getfilesystemencoding())"

echo.
echo 现在可以运行应用了:
echo streamlit run src/app_new.py