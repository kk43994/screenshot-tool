@echo off
setlocal enabledelayedexpansion
title 截图助手 - 简易版
color 0A

set "SCREENSHOT_PATH=C:\Users\zhouk\Desktop\截图助手\current.png"
set "BACKUP_DIR=C:\Users\zhouk\Desktop\截图助手\screenshots"

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

cls
echo.
echo  ================================================
echo             截图助手 for Claude
echo  ================================================
echo.
echo  使用步骤：
echo  1. 按 Win+Shift+S 截图
echo  2. 回到这里按任意键保存
echo  3. 路径会自动复制，粘贴给 Claude
echo.
echo  固定路径: %SCREENSHOT_PATH%
echo.
echo  ================================================
echo.

:loop
echo  [准备就绪] 截图后按任意键保存 (Ctrl+C 退出)
pause >nul

powershell -NoProfile -Command "$img=[Windows.Forms.Clipboard]::GetImage();if($img){$img.Save('%SCREENSHOT_PATH%');$t=Get-Date -F 'yyyyMMdd_HHmmss';$img.Save('%BACKUP_DIR%\screenshot_'+$t+'.png');Set-Clipboard -Value '%SCREENSHOT_PATH%';Write-Host '';Write-Host '  [成功] 截图已保存！' -F Green;Write-Host '  路径: %SCREENSHOT_PATH%' -F Yellow;Write-Host '  (已复制到剪贴板)' -F Cyan;Write-Host ''}else{Write-Host '';Write-Host '  [错误] 剪贴板中没有图片！' -F Red;Write-Host '  请先用 Win+Shift+S 截图' -F Yellow;Write-Host ''}" 2>nul

echo  ------------------------------------------------
goto loop