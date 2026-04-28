@echo off
cd /d %~dp0..
chcp 65001 > nul
echo Starting Stock Analysis System
echo ============================
if "%1"=="--clear-cache" (
    echo Clearing cache
    rmdir /s /q data\cache 2>nul
    mkdir data\cache 2>nul
    del *.tmp 2>nul
    echo Cache cleared
) else (
    echo Forcing cache clear on startup
    rmdir /s /q data\cache 2>nul
    mkdir data\cache 2>nul
    del *.tmp 2>nul
    echo Cache cleared
)
echo Starting application...
streamlit run src\app_new.py
pause