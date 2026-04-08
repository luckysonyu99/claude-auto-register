# 贡献指南

感谢你考虑为 Claude Auto Register 做出贡献！

## 🤝 如何贡献

### 报告 Bug

如果你发现了 bug，请：

1. 检查 [Issues](https://github.com/luckysonyu99/claude-auto-register/issues) 是否已有相同问题
2. 如果没有，创建新的 Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 环境信息（操作系统、Python 版本等）
   - 相关日志或截图

### 提出新功能

如果你有新功能建议：

1. 先创建 Issue 讨论
2. 说明功能的用途和价值
3. 如果可能，提供实现思路

### 提交代码

1. **Fork 仓库**
```bash
# 在 GitHub 上点击 Fork 按钮
```

2. **克隆你的 Fork**
```bash
git clone https://github.com/YOUR_USERNAME/claude-auto-register.git
cd claude-auto-register
```

3. **创建分支**
```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

4. **进行修改**
   - 遵循现有代码风格
   - 添加必要的注释
   - 更新相关文档

5. **测试你的修改**
```bash
# 确保脚本能正常运行
python3 claude_auto_register.py --key YOUR_API_KEY
```

6. **提交修改**
```bash
git add .
git commit -m "feat: 添加新功能描述"
# 或
git commit -m "fix: 修复 bug 描述"
```

7. **推送到你的 Fork**
```bash
git push origin feature/your-feature-name
```

8. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 填写 PR 模板
   - 等待 Review

## 📝 代码规范

### Python 代码风格

遵循 [PEP 8](https://pep8.org/) 规范：

```python
# 好的示例
def purchase_email(self) -> bool:
    """购买邮箱"""
    try:
        self.log(f"正在购买邮箱 (项目: {self.project_code})...", "EMAIL")
        # ...
        return True
    except Exception as e:
        self.log(f"购买邮箱失败: {e}", "ERROR")
        return False

# 避免
def purchaseEmail(self):
    try:
        print("buying email")
        return True
    except:
        return False
```

### 命名规范

- **函数/方法**: `snake_case`
- **类**: `PascalCase`
- **常量**: `UPPER_CASE`
- **私有方法**: `_leading_underscore`

### 注释规范

```python
def wait_for_code(self, timeout: int = 180) -> Optional[str]:
    """
    等待验证码

    Args:
        timeout: 超时时间（秒）

    Returns:
        验证码字符串，失败返回 None
    """
    pass
```

### 日志规范

使用统一的日志格式：

```python
self.log("操作描述", "INFO")    # 普通信息
self.log("成功信息", "SUCCESS") # 成功
self.log("错误信息", "ERROR")   # 错误
self.log("等待中...", "WAIT")   # 等待
```

## 🧪 测试

### 手动测试

在提交 PR 前，请确保：

1. ✅ 脚本能正常运行
2. ✅ 所有功能正常工作
3. ✅ 没有引入新的 bug
4. ✅ 文档已更新

### 测试清单

- [ ] 单个账号注册
- [ ] 批量注册
- [ ] 无头模式
- [ ] 错误处理
- [ ] 日志输出

## 📚 文档

如果你的修改涉及：

- 新功能 → 更新 `README.md` 和 `EXAMPLES.md`
- Bug 修复 → 更新 `TROUBLESHOOTING.md`
- API 变更 → 更新所有相关文档

## 🎯 优先级

我们特别欢迎以下方面的贡献：

### 高优先级
- 🐛 Bug 修复
- 📝 文档改进
- 🔒 安全性增强
- ⚡ 性能优化

### 中优先级
- ✨ 新功能
- 🎨 代码重构
- 🧪 测试覆盖

### 低优先级
- 💄 UI/UX 改进
- 📦 依赖更新

## 🚫 不接受的贡献

- 与项目目标不符的功能
- 未经讨论的大型重构
- 违反法律法规的功能
- 恶意代码或后门

## 📋 Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```bash
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

示例：
```bash
git commit -m "feat: 添加智能表单检测功能"
git commit -m "fix: 修复验证码超时问题"
git commit -m "docs: 更新安装说明"
```

## 🔄 Pull Request 流程

1. **创建 PR** - 填写 PR 模板
2. **自动检查** - 等待 CI 通过
3. **代码审查** - 响应 Review 意见
4. **修改完善** - 根据反馈修改
5. **合并** - 通过后合并到主分支

## 💬 交流

- **Issues**: 报告问题和讨论
- **Pull Requests**: 代码贡献
- **Discussions**: 一般性讨论

## 🎖️ 贡献者

感谢所有贡献者！你的名字将出现在这里。

## 📄 许可证

通过贡献代码，你同意你的贡献将在 MIT 许可证下发布。

## ❓ 问题？

如有任何问题，欢迎：
- 创建 Issue
- 发起 Discussion
- 查看现有文档

---

再次感谢你的贡献！🎉
