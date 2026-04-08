#!/usr/bin/env python3
"""
Claude 账号注册助手 - 简化版
使用 luckmail SDK 接码，手动完成 OAuth 流程
"""

import sys
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any

# 添加 luckmail SDK 路径
LUCKMAIL_PATH = Path.home() / "codex-console" / "luckmail"
if LUCKMAIL_PATH.exists():
    sys.path.insert(0, str(LUCKMAIL_PATH))

try:
    from luckmail import LuckMailClient
except ImportError:
    print("❌ 未找到 luckmail SDK")
    print(f"   请确保 {LUCKMAIL_PATH} 存在")
    sys.exit(1)


class ClaudeRegisterHelper:
    """Claude 注册助手"""

    def __init__(
        self,
        luckmail_api_key: str,
        luckmail_base_url: str = "https://mails.luckyous.com/",
        project_code: str = "kiro",
    ):
        self.client = LuckMailClient(
            base_url=luckmail_base_url,
            api_key=luckmail_api_key,
        )
        self.project_code = project_code
        self.email = None
        self.token = None
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
        }
        icon = icons.get(level, "•")
        print(f"[{timestamp}] {icon} {message}")

    def purchase_email(self) -> bool:
        """购买邮箱"""
        try:
            self.log(f"正在购买邮箱 (项目: {self.project_code})...", "EMAIL")

            result = self.client.user.purchase_emails(
                project_code=self.project_code,
                quantity=1,
                email_type="ms_graph",
            )

            # 提取邮箱信息
            if hasattr(result, 'purchases') and result.purchases:
                item = result.purchases[0]
            elif hasattr(result, 'list') and result.list:
                item = result.list[0]
            elif isinstance(result, list) and result:
                item = result[0]
            else:
                self.log("购买邮箱返回格式异常", "ERROR")
                return False

            self.email = getattr(item, 'email_address', None) or getattr(item, 'email', None)
            self.token = getattr(item, 'token', None)
            self.purchase_id = getattr(item, 'id', None) or getattr(item, 'purchase_id', None)

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
                result = self.client.user.get_token_code(self.token)

                has_mail = getattr(result, 'has_new_mail', False)
                code = getattr(result, 'verification_code', None)

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
                "token": self.token,
                "purchase_id": self.purchase_id,
                "project_code": self.project_code,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
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
        self.log("开始 Claude 账号注册流程", "INFO")
        print("=" * 70 + "\n")

        # 1. 购买邮箱
        if not self.purchase_email():
            return False

        print()

        # 2. 提示用户操作
        self.log("请按以下步骤操作:", "INFO")
        print()
        print("  1. 在浏览器中打开: http://localhost:62311")
        print("  2. 点击「添加账号」按钮")
        print("  3. 在弹出的授权页面中，使用以下邮箱登录:")
        print(f"     📧 {self.email}")
        print("  4. 等待验证码...")
        print()

        input("按 Enter 键继续，开始等待验证码...")
        print()

        # 3. 等待验证码
        code = self.wait_for_code(timeout=180)
        if not code:
            return False

        print()

        # 4. 提示用户输入验证码
        self.log("请在浏览器的授权页面中输入验证码:", "INFO")
        print(f"\n  🔑 验证码: {code}\n")

        # 5. 等待用户确认
        result = input("授权完成后，按 Enter 键继续 (输入 'n' 表示失败): ").strip().lower()

        if result == 'n':
            self.log("授权失败", "ERROR")
            return False

        # 6. 保存账号信息
        self.save_account_info()

        print()
        self.log("注册流程完成!", "SUCCESS")
        print("=" * 70 + "\n")

        return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude 账号注册助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --key YOUR_API_KEY
  %(prog)s --key YOUR_API_KEY --project kiro --count 3
        """
    )
    parser.add_argument("--key", required=True, help="LuckMail API Key")
    parser.add_argument("--url", default="https://mails.luckyous.com/", help="LuckMail API URL")
    parser.add_argument("--project", default="kiro", help="LuckMail 项目代码 (默认: kiro)")
    parser.add_argument("--count", type=int, default=1, help="注册数量 (默认: 1)")
    parser.add_argument("--output", default="claude_accounts.json", help="输出文件 (默认: claude_accounts.json)")

    args = parser.parse_args()

    success_count = 0
    failed_count = 0

    for i in range(args.count):
        if i > 0:
            print("\n" + "=" * 70)
            print(f"准备注册第 {i + 1}/{args.count} 个账号")
            print("=" * 70)
            time.sleep(2)

        helper = ClaudeRegisterHelper(
            luckmail_api_key=args.key,
            luckmail_base_url=args.url,
            project_code=args.project,
        )

        if helper.run():
            success_count += 1
        else:
            failed_count += 1

        if i < args.count - 1:
            print("\n⏳ 等待 5 秒后继续...")
            time.sleep(5)

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
