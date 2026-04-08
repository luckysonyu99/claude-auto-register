# 使用示例

本文档提供了详细的使用示例和常见场景。

## 📚 目录

- [基础使用](#基础使用)
- [批量注册](#批量注册)
- [定时任务](#定时任务)
- [高级配置](#高级配置)
- [常见问题](#常见问题)

## 基础使用

### 1. 快速开始（推荐）

使用提供的启动脚本：

```bash
./start.sh
```

脚本会自动：
- 检查依赖是否安装
- 提示输入 API Key
- 询问注册数量
- 询问是否使用无头模式

### 2. 单个账号注册（带界面）

```bash
python3 claude_auto_register.py --key YOUR_API_KEY
```

**适用场景：**
- 首次使用，需要观察流程
- 调试和排查问题
- 验证配置是否正确

### 3. 单个账号注册（无头模式）

```bash
python3 claude_auto_register.py --key YOUR_API_KEY --headless
```

**适用场景：**
- 后台运行
- 服务器环境
- 定时任务

## 批量注册

### 1. 批量注册 3 个账号

```bash
python3 claude_auto_register.py --key YOUR_API_KEY --count 3
```

### 2. 批量注册 10 个账号（无头模式）

```bash
python3 claude_auto_register.py \
    --key YOUR_API_KEY \
    --count 10 \
    --headless
```

### 3. 快速批量注册（减少延迟）

```bash
python3 claude_auto_register.py \
    --key YOUR_API_KEY \
    --count 5 \
    --headless \
    --slow-mo 200
```

**参数说明：**
- `--slow-mo 200` - 将操作延迟从默认的 500ms 减少到 200ms
- 适合网络良好、页面加载快的情况

## 定时任务

### 1. 每天定时注册（cron）

编辑 crontab：
```bash
crontab -e
```

添加以下内容：

```bash
# 每天上午 10 点注册 3 个账号
0 10 * * * cd /path/to/claude-auto-register && python3 claude_auto_register.py --key YOUR_API_KEY --count 3 --headless >> /tmp/claude_register.log 2>&1

# 每天上午 10 点和下午 3 点各注册 2 个账号
0 10,15 * * * cd /path/to/claude-auto-register && python3 claude_auto_register.py --key YOUR_API_KEY --count 2 --headless >> /tmp/claude_register.log 2>&1

# 每周一上午 9 点注册 5 个账号
0 9 * * 1 cd /path/to/claude-auto-register && python3 claude_auto_register.py --key YOUR_API_KEY --count 5 --headless >> /tmp/claude_register.log 2>&1
```

### 2. 使用 launchd（macOS 推荐）

创建配置文件 `~/Library/LaunchAgents/com.claude.autoregister.plist`：

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
        <string>/Users/YOUR_USERNAME/claude-auto-register/claude_auto_register.py</string>
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

查看状态：
```bash
launchctl list | grep claude
```

停止定时任务：
```bash
launchctl unload ~/Library/LaunchAgents/com.claude.autoregister.plist
```

### 3. 使用环境变量

创建 `.env` 文件：
```bash
cp .env.example .env
nano .env
```

填入你的配置：
```bash
LUCKMAIL_API_KEY=your_real_api_key_here
LUCKMAIL_API_URL=https://mails.luckyous.com/
LUCKMAIL_PROJECT=kiro
CLAUDE_SERVER_URL=http://localhost:62311
```

创建启动脚本 `run.sh`：
```bash
#!/bin/bash
source .env
python3 claude_auto_register.py --key $LUCKMAIL_API_KEY --count 3 --headless
```

## 高级配置

### 1. 自定义 Claude Server 地址

```bash
python3 claude_auto_register.py \
    --key YOUR_API_KEY \
    --claude-url http://192.168.1.100:62311
```

### 2. 自定义 LuckMail 项目

```bash
python3 claude_auto_register.py \
    --key YOUR_API_KEY \
    --project custom_project
```

### 3. 自定义输出文件

```bash
python3 claude_auto_register.py \
    --key YOUR_API_KEY \
    --output /path/to/accounts.json
```

### 4. 组合使用

```bash
python3 claude_auto_register.py \
    --key YOUR_API_KEY \
    --count 5 \
    --project kiro \
    --claude-url http://localhost:62311 \
    --output accounts_$(date +%Y%m%d).json \
    --headless \
    --slow-mo 300
```

## 常见问题

### Q1: 如何查看注册的账号信息？

```bash
cat claude_accounts.json | python3 -m json.tool
```

或者使用 `jq`：
```bash
cat claude_accounts.json | jq '.'
```

### Q2: 如何统计注册成功的账号数量？

```bash
cat claude_accounts.json | jq 'length'
```

### Q3: 如何导出特定日期的账号？

```bash
cat claude_accounts.json | jq '.[] | select(.created_at | startswith("2026-04-08"))'
```

### Q4: 如何批量测试账号是否可用？

创建测试脚本 `test_accounts.py`：

```python
import json

with open('claude_accounts.json', 'r') as f:
    accounts = json.load(f)

print(f"共 {len(accounts)} 个账号")
for i, acc in enumerate(accounts, 1):
    print(f"{i}. {acc['email']} - {acc['created_at']}")
```

### Q5: 如何清理失败的注册记录？

```bash
# 备份原文件
cp claude_accounts.json claude_accounts.json.bak

# 只保留成功的记录（假设成功的记录有 password 字段）
cat claude_accounts.json | jq '[.[] | select(.password != null)]' > claude_accounts_clean.json
mv claude_accounts_clean.json claude_accounts.json
```

### Q6: 如何监控定时任务的执行情况？

```bash
# 查看日志
tail -f /tmp/claude_register.log

# 查看错误日志
tail -f /tmp/claude_register_error.log

# 统计今天注册的账号数
cat claude_accounts.json | jq --arg date "$(date +%Y-%m-%d)" '[.[] | select(.created_at | startswith($date))] | length'
```

## 性能优化

### 1. 并行注册（不推荐）

虽然脚本支持批量注册，但建议串行执行以避免：
- 触发风控
- 资源占用过高
- LuckMail API 限流

### 2. 合理设置延迟

根据网络情况调整 `--slow-mo` 参数：
- 网络良好：200-300ms
- 网络一般：500ms（默认）
- 网络较差：800-1000ms

### 3. 错误重试

创建带重试的脚本 `register_with_retry.sh`：

```bash
#!/bin/bash

MAX_RETRIES=3
COUNT=0

while [ $COUNT -lt $MAX_RETRIES ]; do
    python3 claude_auto_register.py --key YOUR_API_KEY --count 1 --headless

    if [ $? -eq 0 ]; then
        echo "注册成功"
        break
    else
        COUNT=$((COUNT + 1))
        echo "注册失败，重试 $COUNT/$MAX_RETRIES"
        sleep 10
    fi
done
```

## 安全建议

1. **不要在公共环境运行**
2. **定期更换 API Key**
3. **不要将 `claude_accounts.json` 提交到 Git**
4. **使用环境变量管理敏感信息**
5. **定期备份账号信息**

## 更多帮助

查看完整参数列表：
```bash
python3 claude_auto_register.py --help
```

查看版本信息：
```bash
python3 claude_auto_register.py --version
```
