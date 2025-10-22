# 贡献指南

感谢你考虑为截图助手项目做出贡献！

## 🤝 如何贡献

### 报告 Bug

如果你发现了 bug，请：

1. 在 [Issues](https://github.com/kk43994/screenshot-tool/issues) 中搜索是否已有相关问题
2. 如果没有，创建新 Issue，包含以下信息：
   - Bug 的详细描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 你的系统环境（Windows 版本、Python 版本等）
   - 截图或错误日志（如果有）

### 提出新功能

我们欢迎新功能建议！请：

1. 在 Issues 中创建一个 Feature Request
2. 清楚地描述这个功能的用途和场景
3. 如果可能，提供一些实现思路

### 提交代码

#### 准备工作

1. Fork 本仓库
2. 克隆你的 fork：
   ```bash
   git clone https://github.com/你的用户名/screenshot-tool.git
   cd screenshot-tool
   ```

3. 安装开发依赖：
   ```bash
   pip install -r requirements.txt
   ```

#### 开发流程

1. 创建新分支：
   ```bash
   git checkout -b feature/你的功能名称
   # 或
   git checkout -b fix/bug描述
   ```

2. 进行修改并测试

3. 提交更改：
   ```bash
   git add .
   git commit -m "描述你的更改"
   ```

4. 推送到你的 fork：
   ```bash
   git push origin feature/你的功能名称
   ```

5. 在 GitHub 上创建 Pull Request

#### 代码规范

- 使用 Python PEP 8 代码风格
- 添加适当的注释和文档字符串
- 确保代码在 Python 3.7+ 上运行
- 变量和函数名使用英文
- 用户界面文本使用中文

#### Commit 规范

推荐使用以下格式：

```
类型: 简短描述

详细描述（可选）
```

类型包括：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：
```
feat: 添加 OCR 文字识别功能

- 集成 Tesseract OCR 引擎
- 支持中英文混合识别
- 添加识别结果复制功能
```

## 🔍 代码审查

所有的 Pull Request 都会经过审查。请确保：

- 代码符合项目风格
- 没有引入新的 bug
- 功能按预期工作
- 有适当的错误处理
- 更新了相关文档

## 📝 文档

如果你的更改影响到用户使用，请同时更新：

- README.md
- CHANGELOG.md
- 相关的使用说明

## 🧪 测试

目前项目还没有自动化测试，但请确保：

- 手动测试你的更改
- 在不同场景下验证功能
- 检查是否影响现有功能

## ❓ 需要帮助？

如果你在贡献过程中遇到问题：

- 查看 [Issues](https://github.com/kk43994/screenshot-tool/issues)
- 在 [Discussions](https://github.com/kk43994/screenshot-tool/discussions) 中提问
- 联系项目维护者

## 📜 许可证

通过贡献代码，你同意你的贡献将在 MIT 许可证下发布。

---

再次感谢你的贡献！ 💖
