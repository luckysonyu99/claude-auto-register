#!/bin/bash
# Claude Auto Register - 快速启动脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🤖 Claude Auto Register - 快速启动"
echo "=================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 未安装${NC}"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import playwright" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Playwright 未安装，正在安装...${NC}"
    pip install playwright
    playwright install chromium
fi

if ! python3 -c "import httpx" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  httpx 未安装，正在安装...${NC}"
    pip install httpx
fi

# 检查 LuckMail SDK
if [ ! -d "$HOME/codex-console/luckmail" ]; then
    echo -e "${RED}❌ LuckMail SDK 未找到${NC}"
    echo "   请将 LuckMail SDK 放置到: ~/codex-console/luckmail"
    exit 1
fi

echo -e "${GREEN}✅ 环境检查完成${NC}"
echo ""

# 检查 API Key
if [ -z "$LUCKMAIL_API_KEY" ]; then
    echo -e "${YELLOW}请输入 LuckMail API Key:${NC}"
    read -r API_KEY
else
    API_KEY=$LUCKMAIL_API_KEY
fi

if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ API Key 不能为空${NC}"
    exit 1
fi

# 询问注册数量
echo ""
echo -e "${YELLOW}请输入注册数量 (默认: 1):${NC}"
read -r COUNT
COUNT=${COUNT:-1}

# 询问是否使用无头模式
echo ""
echo -e "${YELLOW}是否使用无头模式? (y/N):${NC}"
read -r HEADLESS

HEADLESS_FLAG=""
if [[ "$HEADLESS" =~ ^[Yy]$ ]]; then
    HEADLESS_FLAG="--headless"
fi

# 运行脚本
echo ""
echo "🚀 开始注册 $COUNT 个账号..."
echo ""

python3 claude_auto_register.py \
    --key "$API_KEY" \
    --count "$COUNT" \
    $HEADLESS_FLAG

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 注册完成！${NC}"
    echo "📁 账号信息已保存到: claude_accounts.json"
else
    echo ""
    echo -e "${RED}❌ 注册失败，请查看日志${NC}"
fi
