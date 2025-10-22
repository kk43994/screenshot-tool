# 📸 截图助手 for Claude

一个专为 Claude AI 设计的 Windows 截图工具，快速截图并自动复制路径，让你与 Claude 的交互更加高效。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://www.microsoft.com/windows)
[![Language: Python](https://img.shields.io/badge/Language-Python-green.svg)](https://www.python.org/)
[![Version: 2.5](https://img.shields.io/badge/Version-2.5-brightgreen.svg)](https://github.com/kk43994/screenshot-tool)

## 🎉 v2.5 玻璃拟态版 - 全新发布！

采用2025最流行的玻璃拟态(Glassmorphism)设计，真正的毛玻璃效果，UI极致美观！

**强烈推荐**：`启动玻璃拟态版.bat` ⭐⭐⭐⭐⭐

## ✨ 特性

### 🎯 核心功能
- **固定路径保存**：截图始终保存为 `current.png`，方便快速引用
- **自动备份**：同时在 `screenshots` 文件夹保存带时间戳的备份
- **一键复制**：截图后自动复制路径到剪贴板
- **多版本选择**：提供命令行、图形界面、玻璃拟态等多个版本

### 💎 v2.5 玻璃拟态版（强烈推荐！）
- 🌫️ **真正的玻璃拟态设计**：采用Glassmorphism设计语言
- 💫 **背景模糊效果**：Windows 11 Acrylic毛玻璃效果
- ⚪ **半透明质感**：半透明背景+细白边框
- 🌟 **柔和阴影**：多层渐变阴影，立体感十足
- 🔮 **脉冲动画**：流畅的呼吸动画效果
- 🎨 **现代化配色**：iOS风格配色方案
- 📱 **精致悬浮窗**：圆形玻璃悬浮窗，带徽章计数
- 🖱️ **右键菜单**：快速访问所有功能
- 📌 **系统托盘**：后台运行，随时唤出

### 🎨 精致版（备选）
- 🎨 现代化扁平设计
- 💫 流畅过渡动画
- 🌟 卡片式布局
- 🎯 清晰视觉层次

### 🌟 现代版（经典）
- 🎨 2025年设计趋势
- 🔄 圆形现代化悬浮窗
- ✨ 平滑呼吸动画
- 📱 Segoe UI字体

### 🖥️ 命令行版本
- 轻量级 PowerShell 脚本
- 简单高效，占用资源少
- 适合喜欢命令行的用户

## 🚀 快速开始

### 环境要求
- Windows 10/11
- Python 3.7+ (仅图形界面版本需要)
- PowerShell (命令行版本)

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/kk43994/screenshot-tool.git
   cd screenshot-tool
   ```

2. **安装依赖** (图形界面版本)

   双击运行 `安装依赖.bat` 或手动安装：
   ```bash
   pip install pillow pywin32 keyboard
   ```

### 使用方法

#### ⭐ 推荐：玻璃拟态版

1. 双击运行 `启动玻璃拟态版.bat`
2. 圆形玻璃悬浮窗出现在屏幕右上角
3. 使用全局快捷键快速截图：
   - `Ctrl+Alt+A`：普通截图
   - `Shift+Win+S`：截图并复制路径（推荐用于Claude）
   - `Ctrl+Alt+F`：切换悬浮窗/完整界面
4. 左键点击悬浮窗打开完整界面
5. 右键悬浮窗快速访问功能菜单
6. 悬浮窗可自由拖动到任意位置

**设计亮点**：
- 💎 真正的玻璃拟态效果，半透明+背景模糊
- 🎯 圆形徽章显示截图计数
- 💫 平滑的脉冲呼吸动画
- 🌟 多层柔和阴影，立体感强

#### 方法二：精致版（备选）

1. 双击运行 `启动精致版.bat`
2. 现代化扁平设计，卡片式布局
3. 功能和快捷键与玻璃拟态版相同

#### 方法三：现代版（经典）

1. 双击运行 `启动截图助手(最新版).bat`
2. 经典现代化设计
3. 功能完整，性能稳定

#### 方法四：命令行版本（轻量级）

1. 双击运行 `启动截图助手.bat`
2. 按 `Win + Shift + S` 进行截图
3. 回到命令行窗口按 `Enter` 键
4. 路径自动复制到剪贴板

## ⌨️ 快捷键说明

### 悬浮窗版本热键（全局）

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl + Alt + A` | 正常截图 | 保存截图但保留图片在剪贴板，不复制路径 |
| `Shift + Win + S` | 截图并复制路径 | 保存截图并自动复制路径到剪贴板（推荐用于 Claude） |
| `Ctrl + Alt + F` | 切换界面 | 在悬浮窗和完整界面之间切换 |

### 悬浮窗状态颜色

| 颜色 | 状态 | 说明 |
|------|------|------|
| 🟢 绿色 | 就绪 | 程序准备就绪，可以截图 |
| 🟠 橙色 | 截图中 | 正在等待用户截图 |
| 🔵 蓝色 | 监听中 | 自动监听模式已开启 |

### 图形界面版本热键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl + Alt + A` | 正常截图 | 保存截图但保留图片在剪贴板，不复制路径 |
| `Shift + Win + S` | 截图并复制路径 | 保存截图并自动复制路径到剪贴板（推荐用于 Claude） |

### Windows 系统截图

| 快捷键 | 功能 |
|--------|------|
| `Win + Shift + S` | Windows 截图工具 |
| `PrtScn` | 全屏截图 |

## 📁 文件结构

```
screenshot-tool/
├── 截图助手UI.pyw              # Python 图形界面主程序
├── screenshot_tool.ps1        # PowerShell 命令行脚本
├── 启动UI版.bat               # 启动图形界面
├── 启动截图助手.bat           # 启动命令行版本
├── 安装依赖.bat               # 自动安装 Python 依赖
├── 使用说明.txt               # 简易使用说明
├── current.png                # 当前截图（固定文件名）
├── screenshots/               # 历史截图备份文件夹
│   └── screenshot_YYYYMMDD_HHMMSS.png
├── README.md                  # 项目说明文档
├── CHANGELOG.md               # 开发日志
└── LICENSE                    # MIT 许可证
```

## 💡 使用场景

### 与 Claude 交互
1. 截图后自动获得固定路径：`C:\Users\[用户名]\Desktop\截图助手\current.png`
2. 直接粘贴给 Claude，让 AI 分析图片内容
3. 需要新截图时，重复操作即可覆盖 `current.png`

### 日常截图管理
- 所有截图都会在 `screenshots` 文件夹保存带时间戳的备份
- 方便后续查找和管理历史截图
- 不用担心覆盖丢失重要截图

## 🛠️ 技术栈

- **Python 3.x**：主要开发语言
- **Tkinter**：图形界面框架
- **Pillow (PIL)**：图像处理库
- **pywin32**：Windows 剪贴板操作
- **keyboard**：全局热键监听
- **PowerShell**：命令行脚本

## 🔧 高级配置

### 修改保存路径

编辑 `截图助手UI.pyw` 第 52 行：
```python
self.base_dir = Path(r"C:\Users\zhouk\Desktop\截图助手")
```

编辑 `screenshot_tool.ps1` 第 9 行：
```powershell
$screenshotDir = "C:\Users\zhouk\Desktop\截图助手\screenshots"
```

### 自定义热键

编辑 `截图助手UI.pyw` 第 81-86 行修改热键绑定。

## 🐛 常见问题

### 问题：热键无法使用
**解决方案**：以管理员身份运行程序

### 问题：依赖安装失败
**解决方案**：
```bash
python -m pip install --upgrade pip
pip install pillow pywin32 keyboard
```

### 问题：截图保存失败
**解决方案**：检查目标文件夹是否有写入权限

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建新的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 开发路线图

- [x] 命令行版本
- [x] 图形界面版本
- [x] 全局热键支持
- [x] 自动监听剪贴板
- [ ] 图片编辑功能（标注、裁剪）
- [ ] OCR 文字识别
- [ ] 云同步支持
- [ ] 多显示器支持优化
- [ ] 支持更多图片格式

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

- GitHub: [@kk43994](https://github.com/kk43994)

## 🙏 致谢

- 感谢 Claude AI 提供的开发协助
- 感谢所有使用和反馈的用户

## 📮 联系方式

如有问题或建议，欢迎：
- 提交 [Issue](https://github.com/kk43994/screenshot-tool/issues)
- 发起 [Discussion](https://github.com/kk43994/screenshot-tool/discussions)

---

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！
