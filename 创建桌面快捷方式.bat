@echo off
chcp 65001 >nul
title 创建桌面快捷方式
color 0B

echo.
echo ╔════════════════════════════════════════════╗
echo ║         创建桌面快捷方式                    ║
echo ╚════════════════════════════════════════════╝
echo.

REM 获取当前目录
set CURRENT_DIR=%~dp0
set CURRENT_DIR=%CURRENT_DIR:~0,-1%

REM 获取桌面路径
for /f "tokens=3*" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop') do set DESKTOP=%%b
call set DESKTOP=%DESKTOP%

echo 当前目录: %CURRENT_DIR%
echo 桌面路径: %DESKTOP%
echo.

REM 创建 VBS 脚本来生成快捷方式
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\截图助手.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CURRENT_DIR%\启动截图助手.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "截图助手 - 腾讯风格版" >> CreateShortcut.vbs
echo oLink.IconLocation = "C:\Windows\System32\SnippingTool.exe,0" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

echo 正在创建快捷方式...
cscript //nologo CreateShortcut.vbs

del CreateShortcut.vbs

if exist "%DESKTOP%\截图助手.lnk" (
    color 0A
    echo.
    echo [✓] 快捷方式创建成功！
    echo.
    echo 已在桌面创建"截图助手"快捷方式
    echo 双击即可启动截图助手（腾讯风格版）
) else (
    color 0C
    echo.
    echo [✗] 快捷方式创建失败！
    echo 请手动创建快捷方式
)

echo.
pause
