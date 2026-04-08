#!/usr/bin/env python3
"""
Claude 账号全自动注册机 v2
使用 luckmail SDK 接码 + Playwright 浏览器自动化
"""

import sys
import os
import time
import json
import random
import string
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# 添加 luckmail SDK 路径
# 优先级：环境变量 > 当前目录 > 默认路径
LUCKMAIL_PATHS = [
    Path(os.environ.get("LUCKMAIL_SDK_PATH", "")),  # 环境变量
    Path(__file__).parent / "luckmail",              # 当前目录
    Path.home() / "luckmail",                        # 用户目录
    Path.home() / "codex-console" / "luckmail",      # 兼容旧路径
]

LUCKMAIL_PATH = None
for path in LUCKMAIL_PATHS:
    if path.exists() and (path / "__init__.py").exists():
        LUCKMAIL_PATH = path
        sys.path.insert(0, str(path.parent))
        break

try:
    from luckmail import LuckMailClient
except ImportError:
    print("❌ 未找到 luckmail SDK")
    print("   请将 luckmail SDK 放置到以下任一位置：")
    print(f"   1. {Path(__file__).parent / 'luckmail'} (推荐)")
    print(f"   2. {Path.home() / 'luckmail'}")
    print(f"   3. 或设置环境变量: export LUCKMAIL_SDK_PATH=/path/to/luckmail")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
except ImportError:
    print("❌ 未找到 playwright")
    print("   请运行: pip install playwright && playwright install chromium")
    sys.exit(1)


class ClaudeAutoRegister:
    """Claude 全自动注册器"""

    def __init__(
        self,
        claude_server_url: str = "http://localhost:62311",
        luckmail_base_url: str = "https://mails.luckyous.com/",
        luckmail_api_key: str = "",
        luckmail_project: str = "kiro",
        headless: bool = False,
        slow_mo: int = 500,
    ):
        self.claude_url = claude_server_url
        self.luckmail_client = LuckMailClient(
            base_url=luckmail_base_url,
            api_key=luckmail_api_key,
        )
        self.project_code = luckmail_project
        self.headless = headless
        self.slow_mo = slow_mo

        # 注册信息
        self.email = None
        self.token = None
        self.password = None
        self.purchase_id = None

    def log(self, message: str, level: str = "INFO"):
        """打印日志"""
        timestamp = time.strftime("%H:%M:%S")
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WAIT": "⏳",
            "EMAIL": "📧",
            "CODE": "🔑",
            "LINK": "🔗",
            "BROWSER": "🌐",
        }
        icon = icons.get(level, "•")
        print(f"[{timestamp}] {icon} {message}")

    def generate_password(self, length: int = 16) -> str:
        """生成随机密码"""
        # 确保包含大小写字母、数字和特殊字符
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(length))
        return password

    def generate_name(self) -> str:
        """生成随机姓名"""
        first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emma", "Chris", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def purchase_email(self) -> bool:
        """购买邮箱"""
        try:
            self.log(f"正在购买邮箱 (项目: {self.project_code})...", "EMAIL")

            result = self.luckmail_client.user.purchase_emails(
                project_code=self.project_code,
                quantity=1,
                email_type="ms_graph",
            )

            # 提取邮箱信息
            purchases = result.get("purchases", [])
            if not purchases:
                self.log("购买邮箱返回为空", "ERROR")
                return False

            item = purchases[0]
            self.email = item.get("email_address") or item.get("email")
            self.token = item.get("token")
            self.purchase_id = item.get("id") or item.get("purchase_id")

            if not self.email or not self.token:
                self.log("邮箱信息不完整", "ERROR")
                return False

            self.log(f"成功购买邮箱: {self.email}", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"购买邮箱失败: {e}", "ERROR")
            return False

    def wait_for_code(self, timeout: int = 180) -> Optional[str]:
        """等待验证码"""
        self.log(f"等待验证码 (超时: {timeout}秒)...", "WAIT")

        deadline = time.time() + timeout
        poll_interval = 3
        last_log_time = 0

        while time.time() < deadline:
            try:
                result = self.luckmail_client.user.get_token_code(self.token)

                has_mail = result.has_new_mail if hasattr(result, 'has_new_mail') else False
                code = result.verification_code if hasattr(result, 'verification_code') else None

                if has_mail and code:
                    self.log(f"收到验证码: {code}", "CODE")
                    return code

                # 每 15 秒打印一次剩余时间
                now = time.time()
                if now - last_log_time >= 15:
                    remaining = int(deadline - now)
                    if remaining > 0:
                        self.log(f"等待中... (剩余 {remaining}秒)", "WAIT")
                        last_log_time = now

                time.sleep(poll_interval)

            except Exception as e:
                self.log(f"查询验证码失败: {e}", "ERROR")
                time.sleep(poll_interval)

        self.log("等待验证码超时", "ERROR")
        return None

    def detect_and_fill_form(self, auth_page: Page) -> bool:
        """智能检测页面并填写表单"""
        try:
            # 等待页面加载
            time.sleep(2)

            # 检测页面类型并填写
            page_content = auth_page.content().lower()

            # 1. 检测是否是姓名页面
            name_selectors = [
                'input[name="name"]',
                'input[name="fullName"]',
                'input[name="displayName"]',
                'input[placeholder*="name"]',
                'input[placeholder*="姓名"]',
                'input[placeholder*="Name"]',
            ]

            for selector in name_selectors:
                try:
                    name_input = auth_page.locator(selector).first
                    if name_input.is_visible(timeout=1000):
                        name = self.generate_name()
                        self.log(f"检测到姓名输入框，填写: {name}", "INFO")
                        name_input.fill(name)
                        time.sleep(1)
                        return True
                except:
                    continue

            # 2. 检测是否是验证码页面
            code_selectors = [
                'input[name="code"]',
                'input[name="verificationCode"]',
                'input[name="otp"]',
                'input[placeholder*="code"]',
                'input[placeholder*="验证码"]',
                'input[placeholder*="Code"]',
                'input[type="text"][maxlength="6"]',
                'input[type="text"][maxlength="8"]',
            ]

            for selector in code_selectors:
                try:
                    code_input = auth_page.locator(selector).first
                    if code_input.is_visible(timeout=1000):
                        self.log("检测到验证码输入框，等待验证码", "CODE")
                        code = self.wait_for_code(timeout=180)
                        if not code:
                            return False
                        self.log(f"填入验证码: {code}", "CODE")
                        code_input.fill(code)
                        time.sleep(1)
                        return True
                except:
                    continue

            # 3. 检测是否是密码设置页面
            password_inputs = auth_page.locator('input[type="password"]')
            password_count = password_inputs.count()

            if password_count >= 1:
                self.password = self.generate_password()
                self.log(f"检测到密码输入框，设置密码: {self.password}", "INFO")

                # 填写第一个密码框
                password_inputs.nth(0).fill(self.password)
                time.sleep(1)

                # 如果有第二个密码框（确认密码）
                if password_count >= 2:
                    password_inputs.nth(1).fill(self.password)
                    time.sleep(1)

                return True

            # 4. 检测是否是授权页面
            auth_button_selectors = [
                'button:has-text("Allow")',
                'button:has-text("Authorize")',
                'button:has-text("Accept")',
                'button:has-text("授权")',
                'button:has-text("允许")',
                'button:has-text("同意")',
                'button:has-text("Approve")',
            ]

            for selector in auth_button_selectors:
                try:
                    auth_button = auth_page.locator(selector).first
                    if auth_button.is_visible(timeout=1000):
                        self.log("检测到授权按钮，点击授权", "BROWSER")
                        auth_button.click()
                        time.sleep(3)
                        return True
                except:
                    continue

            return False

        except Exception as e:
            self.log(f"检测表单失败: {e}", "ERROR")
            return False

    def automate_registration(self, page: Page) -> bool:
        """自动化注册流程"""
        try:
            # 1. 访问 Claude Server
            self.log(f"访问 Claude Server: {self.claude_url}", "BROWSER")
            page.goto(self.claude_url, wait_until="networkidle")
            time.sleep(2)

            # 2. 点击"添加账号"按钮
            self.log("点击「添加账号」按钮", "BROWSER")
            add_button = page.locator('button:has-text("添加账号")')
            if not add_button.is_visible():
                self.log("未找到「添加账号」按钮", "ERROR")
                return False
            add_button.click()
            time.sleep(2)

            # 3. 点击"我已知晓"确认弹窗
            self.log("点击「我已知晓」确认", "BROWSER")
            confirm_button = page.locator('button:has-text("我已知晓")')
            if confirm_button.is_visible():
                confirm_button.click()
                time.sleep(2)

            # 4. 获取 AWS 认证链接
            self.log("获取 AWS 认证链接", "LINK")
            # 尝试多种可能的选择器
            auth_link = None
            selectors = [
                'a[href*="awsapps.com"]',
                'a[href*="view.awsapps.com"]',
                'text=/https:\/\/view\.awsapps\.com/',
            ]

            for selector in selectors:
                try:
                    link_element = page.locator(selector).first
                    if link_element.is_visible():
                        auth_link = link_element.get_attribute("href") or link_element.inner_text()
                        break
                except:
                    continue

            if not auth_link:
                self.log("未找到 AWS 认证链接", "ERROR")
                return False

            self.log(f"获取到认证链接: {auth_link}", "LINK")

            # 5. 在新标签页打开认证链接
            self.log("打开 AWS 认证页面", "BROWSER")
            auth_page = page.context.new_page()
            auth_page.goto(auth_link, wait_until="networkidle")
            time.sleep(2)

            # 6. 填入邮箱地址
            self.log(f"填入邮箱: {self.email}", "EMAIL")
            email_input = auth_page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first
            email_input.fill(self.email)
            time.sleep(1)

            # 点击下一步/继续按钮
            next_button = auth_page.locator('button[type="submit"], button:has-text("Next"), button:has-text("Continue"), button:has-text("下一步"), button:has-text("继续")').first
            next_button.click()
            time.sleep(3)

            # 7-10. 智能检测并填写后续表单（最多尝试 10 次）
            self.log("开始智能表单填写流程", "BROWSER")
            max_attempts = 10
            filled_count = 0

            for attempt in range(max_attempts):
                self.log(f"尝试检测表单 ({attempt + 1}/{max_attempts})", "INFO")

                # 检测并填写表单
                if self.detect_and_fill_form(auth_page):
                    filled_count += 1
                    self.log(f"成功填写表单 (已完成 {filled_count} 个)", "SUCCESS")

                    # 尝试点击下一步按钮
                    try:
                        next_button = auth_page.locator('button[type="submit"], button:has-text("Next"), button:has-text("Continue"), button:has-text("Submit"), button:has-text("下一步"), button:has-text("继续"), button:has-text("提交")').first
                        if next_button.is_visible(timeout=2000):
                            next_button.click()
                            time.sleep(3)
                    except:
                        pass
                else:
                    # 如果没有检测到表单，可能已经完成
                    self.log("未检测到更多表单，可能已完成注册", "INFO")
                    break

                # 检查是否已经完成注册
                current_url = auth_page.url.lower()
                if "success" in current_url or "complete" in current_url or "done" in current_url:
                    self.log("检测到成功页面", "SUCCESS")
                    break

                # 检查是否回到了 Claude Server
                if self.claude_url in auth_page.url:
                    self.log("已返回 Claude Server", "SUCCESS")
                    break

            # 11. 检查是否注册成功
            time.sleep(3)

            if filled_count >= 3:  # 至少填写了 3 个表单（姓名、验证码、密码等）
                self.log("注册流程已完成", "SUCCESS")
                auth_page.close()
                return True
            else:
                self.log(f"注册流程可能未完成（仅填写了 {filled_count} 个表单）", "ERROR")
                auth_page.close()
                return False

        except Exception as e:
            self.log(f"自动化注册失败: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    def save_account_info(self, output_file: str = "claude_accounts.json"):
        """保存账号信息到文件"""
        try:
            output_path = Path(output_file)

            # 读取现有数据
            accounts = []
            if output_path.exists():
                with open(output_path, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)

            # 添加新账号
            account_info = {
                "email": self.email,
                "password": self.password,
                "token": self.token,
                "purchase_id": self.purchase_id,
                "project_code": self.project_code,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            accounts.append(account_info)

            # 保存
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)

            self.log(f"账号信息已保存到: {output_path}", "SUCCESS")

        except Exception as e:
            self.log(f"保存账号信息失败: {e}", "ERROR")

    def run(self) -> bool:
        """执行注册流程"""
        print("\n" + "=" * 70)
        self.log("开始 Claude 账号自动注册流程", "INFO")
        print("=" * 70 + "\n")

        # 1. 购买邮箱
        if not self.purchase_email():
            return False

        print()

        # 2. 启动浏览器自动化
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()

            try:
                success = self.automate_registration(page)

                if success:
                    # 3. 保存账号信息
                    self.save_account_info()

                    print()
                    self.log("注册流程完成!", "SUCCESS")
                    print("=" * 70 + "\n")
                    return True
                else:
                    self.log("注册流程失败", "ERROR")
                    return False

            finally:
                browser.close()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude 账号全自动注册机",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --key YOUR_API_KEY
  %(prog)s --key YOUR_API_KEY --count 3 --headless
  %(prog)s --key YOUR_API_KEY --project kiro --no-headless
        """
    )
    parser.add_argument("--key", required=True, help="LuckMail API Key")
    parser.add_argument("--url", default="https://mails.luckyous.com/", help="LuckMail API URL")
    parser.add_argument("--project", default="kiro", help="LuckMail 项目代码 (默认: kiro)")
    parser.add_argument("--claude-url", default="http://localhost:62311", help="Claude Server URL")
    parser.add_argument("--count", type=int, default=1, help="注册数量 (默认: 1)")
    parser.add_argument("--output", default="claude_accounts.json", help="输出文件 (默认: claude_accounts.json)")
    parser.add_argument("--headless", action="store_true", help="无头模式运行浏览器")
    parser.add_argument("--slow-mo", type=int, default=500, help="浏览器操作延迟(毫秒，默认: 500)")

    args = parser.parse_args()

    success_count = 0
    failed_count = 0

    for i in range(args.count):
        if i > 0:
            print("\n" + "=" * 70)
            print(f"准备注册第 {i + 1}/{args.count} 个账号")
            print("=" * 70)
            time.sleep(5)

        register = ClaudeAutoRegister(
            claude_server_url=args.claude_url,
            luckmail_base_url=args.url,
            luckmail_api_key=args.key,
            luckmail_project=args.project,
            headless=args.headless,
            slow_mo=args.slow_mo,
        )

        if register.run():
            success_count += 1
        else:
            failed_count += 1

        if i < args.count - 1:
            print("\n⏳ 等待 10 秒后继续...")
            time.sleep(10)

    # 总结
    print("\n" + "=" * 70)
    print("📊 注册统计")
    print("=" * 70)
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {failed_count}")
    print(f"  📁 输出文件: {args.output}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
