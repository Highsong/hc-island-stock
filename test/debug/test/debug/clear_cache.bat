@echo off
chcp 65001 > nul
echo =======================================
echo Clearing ALL cache and temporary files...
echo =======================================

echo Running cache cleanup...

REM Clear main cache directory
if exist data\cache\ (
    echo Clearing data\cache\*.json ...
    del /q data\cache\*.json 2>nul
    del /q data\cache\*.log 2>nul
    echo ✓ Main cache cleared
) else (
    echo Cache directory not found, creating...
    mkdir data\cache
)

REM Clear processed data cache
if exist data\processed_data\ (
    echo Clearing data\processed_data\* ...
    del /q data\processed_data\*.json 2>nul
    del /q data\processed_data\*.csv 2>nul
    echo ✓ Processed data cache cleared
)

REM Clear any Python cache files
if exist __pycache__\ (
    echo Clearing __pycache__ ...
    rmdir /s /q __pycache__ 2>nul
    echo ✓ Root __pycache__ cleared
)

if exist src\__pycache__\ (
    echo Clearing src\__pycache__ ...
    rmdir /s /q src\__pycache__ 2>nul
    echo ✓ src\__pycache__ cleared
)

if exist src\*\__pycache__\ (
    echo Clearing src subdirectory caches...
    for /d %%d in (src\*\__pycache__) do rmdir /s /q "%%d" 2>nul
    echo ✓ src subdirectory caches cleared
)

REM Clear any temporary files
del /q *.tmp 2>nul
del /q *.temp 2>nul
echo ✓ Temporary files cleared

echo.
echo =======================================
echo ✓ All cache and temporary files cleared!
echo =======================================
echo.
pause