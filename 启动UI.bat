@echo off
cd /d "%~dp0"

REM 检查依赖
python -c "import win32clipboard" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    pip install pywin32 >nul 2>&1
)

start "" /B pythonw "截图助手UI.pyw"