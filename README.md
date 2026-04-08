# Claude Auto Register

🤖 Claude 账号全自动注册工具 - 基于 LuckMail 接码 + Playwright 浏览器自动化

## ✨ 特性

- 🚀 **全自动注册** - 从购买邮箱到完成注册，全程自动化
- 🧠 **智能表单检测** - 自动识别页面类型并填写相应内容
- 🔐 **随机密码生成** - 自动生成强密码并保存
- 📦 **批量注册** - 支持一次注册多个账号
- 👻 **无头模式** - 支持后台运行，不显示浏览器
- 📝 **完整日志** - 详细的操作日志，方便调试
- 💾 **自动保存** - 账号信息自动保存到 JSON 文件

## 📋 功能对比

| 功能 | 全自动版本 | 半自动版本 |
|------|-----------|-----------|
| 购买邮箱 | ✅ | ✅ |
| 接收验证码 | ✅ | ✅ |
| 浏览器自动化 | ✅ | ❌ |
| 自动填写表单 | ✅ | ❌ |
| 批量注册 | ✅ | ✅ |
| 无头模式 | ✅ | ❌ |

## 🔧 环境要求

- Python 3.8+
- LuckMail SDK
- Playwright

## 📦 安装

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/claude-auto-register.git
cd claude-auto-register
```

### 2. 安装依赖

```bash
# 安装 Python 依赖
pip install playwright httpx

# 安装浏览器驱动
playwright install chromium
```

### 3. 安装 LuckMail SDK

将 LuckMail SDK 放置到 `~/codex-console/luckmail` 目录：

```bash
mkdir -p ~/codex-console
cp -r /path/to/luckmail ~/codex-console/
```

## 🚀 快速开始

### 全自动注册（推荐）

```bash
# 单个账号注册（带界面，方便调试）
python3 claude_auto_register.py --key YOUR_LUCKMAIL_API_KEY

# 批量注册 3 个账号
python3 claude_auto_register.py --key YOUR_API_KEY --count 3

# 无头模式运行（后台运行）
python3 claude_auto_register.py --key YOUR_API_KEY --count 5 --headless

# 加快速度（减少延迟）
python3 claude_auto_register.py --key YOUR_API_KEY --slow-mo 200
```

### 半自动注册

```bash
# 单个账号
python3 claude_register_simple.py --key YOUR_API_KEY

# 批量注册
python3 claude_register_simple.py --key YOUR_API_KEY --count 3
```

## 📖 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--key` | LuckMail API Key（必填） | - |
| `--url` | LuckMail API 地址 | https://mails.luckyous.com/ |
| `--project` | LuckMail 项目代码 | kiro |
| `--claude-url` | Claude Server 地址 | http://localhost:62311 |
| `--count` | 注册数量 | 1 |
| `--output` | 输出文件路径 | claude_accounts.json |
| `--headless` | 无头模式（不显示浏览器） | false |
| `--slow-mo` | 操作延迟（毫秒） | 500 |

## 🔄 注册流程

### 全自动版本流程

1. ✅ 使用 LuckMail SDK 购买 Outlook 邮箱
2. ✅ 打开 Claude API Server 管理页面
3. ✅ 点击"添加账号"按钮
4. ✅ 确认"我已知晓"弹窗
5. ✅ 获取 AWS 认证链接
6. ✅ 在新页面填入邮箱地址
7. ✅ **智能检测表单类型**：
   - 自动识别姓名输入框并填写
   - 自动识别验证码输入框并填写
   - 自动识别密码输入框并设置
   - 自动识别授权按钮并点击
8. ✅ 保存账号信息到 JSON 文件

### 智能表单检测

脚本会自动循环检测页面（最多 10 次），每次自动判断当前需要填写什么：

- **姓名页面** - 检测到姓名输入框 → 自动生成并填写随机姓名
- **验证码页面** - 检测到验证码输入框 → 等待并自动填入验证码
- **密码页面** - 检测到密码输入框 → 自动生成并填写强密码
- **授权页面** - 检测到授权按钮 → 自动点击授权

**不依赖固定顺序**，无论页面如何变化都能正确处理！

## 📄 输出文件格式

`claude_accounts.json`:

```json
[
  {
    "email": "user@outlook.com",
    "password": "RandomPassword123!@#",
    "token": "tok_abc123def456",
    "purchase_id": 12345,
    "project_code": "kiro",
    "created_at": "2026-04-08 17:30:00"
  }
]
```

## ⏰ 定时任务

### 使用 cron（Linux/macOS）

```bash
# 编辑 crontab
crontab -e

# 每天上午 10 点注册 3 个账号
0 10 * * * cd /path/to/claude-auto-register && python3 claude_auto_register.py --key YOUR_API_KEY --count 3 --headless >> /tmp/claude_register.log 2>&1
```

### 使用 launchd（macOS 推荐）

创建 `~/Library/LaunchAgents/com.claude.autoregister.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claude.autoregister</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/claude-auto-register/claude_auto_register.py</string>
        <string>--key</string>
        <string>YOUR_API_KEY</string>
        <string>--count</string>
        <string>3</string>
        <string>--headless</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>10</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/claude_register.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/claude_register_error.log</string>
</dict>
</plist>
```

加载定时任务：
```bash
launchctl load ~/Library/LaunchAgents/com.claude.autoregister.plist
```

## 🐛 故障排查

### 1. LuckMail SDK 未找到

```bash
# 检查路径
ls ~/codex-console/luckmail

# 如果不存在，复制 SDK
cp -r /path/to/luckmail ~/codex-console/
```

### 2. Playwright 浏览器未安装

```bash
playwright install chromium
```

### 3. 验证码超时

- 检查 LuckMail 服务是否正常
- 增加超时时间（修改脚本中的 `timeout=180` 参数）

### 4. 页面元素未找到

- 使用非无头模式运行，观察浏览器操作：
  ```bash
  python3 claude_auto_register.py --key YOUR_API_KEY
  ```
- AWS 认证页面可能有变化，需要更新选择器

## ⚠️ 注意事项

1. **首次运行建议不使用 `--headless`**，观察浏览器自动化过程
2. **确保 LuckMail 服务正常**，否则无法购买邮箱
3. **保管好 `claude_accounts.json` 文件**，包含账号密码
4. **合理设置注册频率**，避免触发风控
5. **定期检查日志**，确保定时任务正常运行
6. **Claude API Server 需要在本地运行**（默认 http://localhost:62311）

## 🔐 安全建议

- 不要将 API Key 硬编码到脚本中
- 不要将 `claude_accounts.json` 提交到 Git
- 定期更换 API Key
- 使用环境变量或配置文件管理敏感信息

## 📝 更新日志

### v2.0 (2026-04-08)

- ✨ 全自动浏览器操作
- ✨ 智能表单检测（不依赖固定顺序）
- ✨ 自动生成随机密码和姓名
- ✨ 支持批量注册
- ✨ 支持无头模式
- ✨ 完整的错误处理和日志

### v1.0 (2026-04-08)

- 半自动版本
- 手动浏览器操作
- 基础接码功能

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚡ 技术栈

- **Python 3.8+** - 主要编程语言
- **Playwright** - 浏览器自动化
- **LuckMail SDK** - 邮箱购买和接码
- **httpx** - HTTP 客户端

## 📧 联系方式

如有问题或建议，欢迎提交 Issue。

---

**免责声明**：本工具仅供学习和研究使用，请遵守相关服务条款和法律法规。
