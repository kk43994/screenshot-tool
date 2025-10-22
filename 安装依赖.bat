@echo off
chcp 65001 >nul
title 安装截图助手依赖
color 0A

echo ========================================
echo    截图助手 - 依赖安装程序
echo ========================================
echo.
echo 正在检查 Python 环境...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [错误] 未检测到 Python！
    echo.
    echo 请先安装 Python 3.7 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python --version
echo.
echo ========================================
echo 正在安装依赖库...
echo ========================================
echo.

echo [1/3] 安装 Pillow (图像处理库)...
pip install pillow
echo.

echo [2/3] 安装 pywin32 (Windows 系统库)...
pip install pywin32
echo.

echo [3/3] 安装 keyboard (热键库)...
pip install keyboard
echo.

echo ========================================
echo 验证安装...
echo ========================================
echo.

python -c "import PIL; import win32clipboard; import keyboard; print('✓ 所有依赖安装成功！')"

if errorlevel 1 (
    color 0C
    echo.
    echo [警告] 部分依赖可能安装失败
    echo 请检查上方的错误信息
) else (
    color 0A
    echo.
    echo ========================================
    echo    安装完成！可以开始使用了
    echo ========================================
)

echo.
pause