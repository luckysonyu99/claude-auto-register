# 故障排查指南

本文档帮助你解决使用过程中可能遇到的问题。

## 📚 目录

- [环境问题](#环境问题)
- [LuckMail 相关](#luckmail-相关)
- [浏览器自动化问题](#浏览器自动化问题)
- [注册流程问题](#注册流程问题)
- [其他问题](#其他问题)

## 环境问题

### ❌ Python 版本过低

**错误信息：**
```
SyntaxError: invalid syntax
```

**解决方案：**
```bash
# 检查 Python 版本
python3 --version

# 需要 Python 3.8 或更高版本
# macOS 安装最新版本
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11
```

### ❌ Playwright 未安装

**错误信息：**
```
ModuleNotFoundError: No module named 'playwright'
```

**解决方案：**
```bash
# 安装 Playwright
pip install playwright

# 安装浏览器驱动
playwright install chromium

# 如果遇到权限问题
pip install --user playwright
playwright install chromium
```

### ❌ 浏览器驱动安装失败

**错误信息：**
```
Executable doesn't exist at /path/to/chromium
```

**解决方案：**
```bash
# 重新安装浏览器驱动
playwright install --force chromium

# 或者安装所有浏览器
playwright install

# 检查安装路径
playwright install --help
```

## LuckMail 相关

### ❌ LuckMail SDK 未找到

**错误信息：**
```
❌ 未找到 luckmail SDK
   请将 luckmail SDK 放置到以下任一位置：
   1. /path/to/claude-auto-register/luckmail (推荐)
   2. /Users/xxx/luckmail
   3. 或设置环境变量: export LUCKMAIL_SDK_PATH=/path/to/luckmail
```

**解决方案：**

**方式一：放到项目目录（推荐）**
```bash
# 进入项目目录
cd /path/to/claude-auto-register

# 复制 SDK
cp -r /path/to/luckmail ./

# 验证
ls luckmail/__init__.py
```

**方式二：放到用户目录**
```bash
# 复制到用户目录
cp -r /path/to/luckmail ~/luckmail

# 验证
ls ~/luckmail/__init__.py
```

**方式三：使用环境变量**
```bash
# 临时设置（当前会话有效）
export LUCKMAIL_SDK_PATH=/path/to/luckmail

# 永久设置（添加到 ~/.zshrc 或 ~/.bashrc）
echo 'export LUCKMAIL_SDK_PATH=/path/to/luckmail' >> ~/.zshrc
source ~/.zshrc
```

### ❌ API Key 无效

**错误信息：**
```
AuthError: API Key 无效或已过期
```

**解决方案：**
1. 登录 LuckMail 平台检查 API Key 是否正确
2. 检查 API Key 是否过期
3. 重新生成 API Key
4. 确认 API Key 没有多余的空格或换行符

### ❌ 余额不足

**错误信息：**
```
APIError: 余额不足
```

**解决方案：**
1. 登录 LuckMail 平台充值
2. 检查当前余额：
```bash
python3 -c "
from luckmail import LuckMailClient
client = LuckMailClient(base_url='https://mails.luckyous.com/', api_key='YOUR_API_KEY')
print(f'余额: {client.user.get_balance()}')
"
```

### ❌ 购买邮箱失败

**错误信息：**
```
❌ 购买邮箱失败: ...
```

**可能原因：**
1. LuckMail 服务暂时不可用
2. 项目代码错误（检查 `--project` 参数）
3. 邮箱类型不支持
4. 网络连接问题

**解决方案：**
```bash
# 1. 检查 LuckMail 服务状态
curl https://mails.luckyous.com/

# 2. 测试 API 连接
python3 -c "
from luckmail import LuckMailClient
client = LuckMailClient(base_url='https://mails.luckyous.com/', api_key='YOUR_API_KEY')
info = client.user.get_user_info()
print(f'用户: {info.username}, 余额: {info.balance}')
"

# 3. 查看可用项目
python3 -c "
from luckmail import LuckMailClient
client = LuckMailClient(base_url='https://mails.luckyous.com/', api_key='YOUR_API_KEY')
projects = client.user.get_projects()
for p in projects.list:
    print(f'{p.code}: {p.name}')
"
```

### ❌ 验证码超时

**错误信息：**
```
❌ 等待验证码超时
```

**解决方案：**
1. 增加超时时间（修改脚本中的 `timeout=180` 为更大的值）
2. 检查邮箱是否正常接收邮件
3. 手动登录邮箱查看是否收到验证码
4. 联系 LuckMail 客服检查邮箱状态

## 浏览器自动化问题

### ❌ 无法打开浏览器

**错误信息：**
```
playwright._impl._api_types.Error: Browser closed
```

**解决方案：**
```bash
# 1. 检查浏览器是否正确安装
playwright install chromium

# 2. 尝试使用其他浏览器
# 修改脚本中的 browser = p.chromium.launch() 为:
# browser = p.firefox.launch()

# 3. 检查系统资源
# 确保有足够的内存和 CPU
```

### ❌ 页面加载超时

**错误信息：**
```
TimeoutError: page.goto: Timeout 30000ms exceeded
```

**解决方案：**
```bash
# 1. 检查网络连接
ping claude.moreyu.eu.org

# 2. 增加超时时间
# 在脚本中修改: page.goto(url, timeout=60000)

# 3. 检查 Claude Server 是否运行
curl http://localhost:62311
```

### ❌ 元素未找到

**错误信息：**
```
playwright._impl._api_types.Error: Locator.click: Timeout 30000ms exceeded
```

**解决方案：**
1. 使用非无头模式运行，观察页面：
```bash
python3 claude_auto_register.py --key YOUR_API_KEY
```

2. 检查页面是否正确加载
3. 页面结构可能已变化，需要更新选择器
4. 增加等待时间（修改 `slow_mo` 参数）

## 注册流程问题

### ❌ 未找到"添加账号"按钮

**可能原因：**
1. Claude Server 未运行
2. 页面未完全加载
3. 页面结构已变化

**解决方案：**
```bash
# 1. 检查 Claude Server
curl http://localhost:62311

# 2. 手动访问页面确认按钮存在
open http://localhost:62311

# 3. 增加等待时间
# 修改脚本中的 time.sleep(2) 为更大的值
```

### ❌ 未找到 AWS 认证链接

**可能原因：**
1. 弹窗未正确处理
2. 链接生成失败
3. 页面结构变化

**解决方案：**
1. 使用非无头模式观察
2. 手动点击"添加账号"查看链接格式
3. 更新脚本中的选择器

### ❌ 表单填写失败

**错误信息：**
```
未检测到更多表单，可能已完成注册
```

**解决方案：**
1. 检查日志，查看已填写的表单数量
2. 使用非无头模式观察哪个步骤失败
3. 可能是页面加载慢，增加 `--slow-mo` 参数：
```bash
python3 claude_auto_register.py --key YOUR_API_KEY --slow-mo 1000
```

### ❌ 密码设置失败

**可能原因：**
1. 密码不符合要求（太短、缺少特殊字符等）
2. 确认密码框未找到

**解决方案：**
修改脚本中的 `generate_password` 方法，确保密码符合要求。

## 其他问题

### ❌ 权限被拒绝

**错误信息：**
```
PermissionError: [Errno 13] Permission denied
```

**解决方案：**
```bash
# 添加执行权限
chmod +x claude_auto_register.py
chmod +x start.sh

# 或使用 python3 运行
python3 claude_auto_register.py --key YOUR_API_KEY
```

### ❌ 文件未找到

**错误信息：**
```
FileNotFoundError: [Errno 2] No such file or directory
```

**解决方案：**
```bash
# 确保在正确的目录
cd /path/to/claude-auto-register

# 检查文件是否存在
ls -la
```

### ❌ JSON 解析错误

**错误信息：**
```
json.decoder.JSONDecodeError: Expecting value
```

**解决方案：**
```bash
# 1. 检查 claude_accounts.json 是否损坏
cat claude_accounts.json

# 2. 如果损坏，从备份恢复
cp claude_accounts.json.bak claude_accounts.json

# 3. 或者删除重新开始
rm claude_accounts.json
```

## 调试技巧

### 1. 启用详细日志

修改脚本，添加更多日志输出：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 截图调试

在关键步骤添加截图：
```python
auth_page.screenshot(path=f"debug_{int(time.time())}.png")
```

### 3. 暂停执行

在需要检查的地方添加：
```python
input("按 Enter 继续...")
```

### 4. 使用浏览器开发者工具

非无头模式下，可以手动打开开发者工具查看页面元素。

## 获取帮助

如果以上方法都无法解决问题：

1. **查看日志文件**
```bash
tail -f /tmp/claude_register.log
tail -f /tmp/claude_register_error.log
```

2. **提交 Issue**
   - 访问：https://github.com/luckysonyu99/claude-auto-register/issues
   - 提供详细的错误信息和日志
   - 说明你的环境（操作系统、Python 版本等）

3. **检查更新**
```bash
git pull origin main
```

## 常见错误代码

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| 401 | API Key 无效 | 检查 API Key |
| 403 | 权限不足 | 检查账号权限 |
| 429 | 请求过于频繁 | 降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |
| 503 | 服务不可用 | 检查服务状态 |

## 性能优化建议

1. **网络优化**
   - 使用稳定的网络连接
   - 避免使用 VPN（可能导致超时）

2. **资源优化**
   - 关闭不必要的程序
   - 确保有足够的内存（建议 4GB+）

3. **参数调优**
   - 根据网络情况调整 `--slow-mo`
   - 合理设置批量数量（建议不超过 10）

## 预防措施

1. **定期备份**
```bash
cp claude_accounts.json claude_accounts_$(date +%Y%m%d).json
```

2. **监控余额**
```bash
# 创建监控脚本
python3 -c "
from luckmail import LuckMailClient
client = LuckMailClient(base_url='https://mails.luckyous.com/', api_key='YOUR_API_KEY')
balance = float(client.user.get_balance())
if balance < 10:
    print('⚠️  余额不足 10 元，请及时充值')
"
```

3. **日志轮转**
```bash
# 定期清理日志
find /tmp -name "claude_register*.log" -mtime +7 -delete
```
