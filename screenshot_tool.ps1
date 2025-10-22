# 截图助手 for Claude - 优化版
# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 设置截图保存路径
$screenshotDir = "C:\Users\zhouk\Desktop\截图助手\screenshots"

# 创建截图目录
if (-not (Test-Path $screenshotDir)) {
    New-Item -ItemType Directory -Path $screenshotDir | Out-Null
}

# 固定文件路径（总是覆盖同一个文件）
$fixedPath = "C:\Users\zhouk\Desktop\截图助手\current.png"

Clear-Host
Write-Host ""
Write-Host "  ╔════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║       截图助手 for Claude          ║" -ForegroundColor Yellow
Write-Host "  ╚════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  使用方法：" -ForegroundColor White
Write-Host "  1. " -NoNewline -ForegroundColor Cyan; Write-Host "Win+Shift+S " -NoNewline -ForegroundColor Yellow; Write-Host "截取屏幕"
Write-Host "  2. " -NoNewline -ForegroundColor Cyan; Write-Host "回到这里按 " -NoNewline; Write-Host "Enter " -NoNewline -ForegroundColor Yellow; Write-Host "保存"
Write-Host "  3. " -NoNewline -ForegroundColor Cyan; Write-Host "路径自动复制，粘贴给 Claude"
Write-Host ""
Write-Host "  [按 Ctrl+C 退出]" -ForegroundColor DarkGray
Write-Host "  ════════════════════════════════════" -ForegroundColor DarkCyan
Write-Host ""

$count = 0

while ($true) {
    Write-Host "  准备就绪 " -NoNewline -ForegroundColor Green
    Write-Host "→ 截图后按 Enter: " -NoNewline -ForegroundColor White

    $null = Read-Host

    $img = [System.Windows.Forms.Clipboard]::GetImage()

    if ($img) {
        $count++

        # 保存到固定位置（覆盖）
        $img.Save($fixedPath)

        # 同时保存一份带时间戳的备份
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = Join-Path $screenshotDir "screenshot_$timestamp.png"
        $img.Save($backupPath)

        # 复制固定路径到剪贴板
        Set-Clipboard -Value $fixedPath

        Write-Host ""
        Write-Host "  ✓ 截图已保存！(第 $count 张)" -ForegroundColor Green
        Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Write-Host "  路径: " -NoNewline -ForegroundColor Gray
        Write-Host $fixedPath -ForegroundColor Yellow
        Write-Host "  备份: " -NoNewline -ForegroundColor Gray
        Write-Host "$backupPath" -ForegroundColor DarkGray
        Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Write-Host "  " -NoNewline
        Write-Host "→ 路径已复制！直接粘贴给 Claude" -ForegroundColor Cyan -BackgroundColor DarkBlue
        Write-Host ""
        Write-Host "  可以继续截图，或按 Ctrl+C 退出" -ForegroundColor DarkGray
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "  ✗ 剪贴板中没有图片！" -ForegroundColor Red
        Write-Host "  请先用 " -NoNewline -ForegroundColor Yellow
        Write-Host "Win+Shift+S" -NoNewline -ForegroundColor Cyan
        Write-Host " 截图" -ForegroundColor Yellow
        Write-Host ""
    }
}