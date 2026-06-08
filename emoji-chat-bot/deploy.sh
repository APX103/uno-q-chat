#!/bin/bash
# 部署脚本：同步代码到 Arduino UNO Q 并启动应用
# 用法: ./deploy.sh [board-ip]

set -e

BOARD_IP="${1:-}"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTE_DIR="~/ArduinoApps/emoji-chat-bot"

if [ -z "$BOARD_IP" ]; then
  echo "❌ 请指定板子 IP 地址"
  echo "用法: ./deploy.sh 192.168.1.100"
  exit 1
fi

echo "🚀 部署到 Arduino UNO Q ($BOARD_IP)..."
echo "   本地目录: $PROJECT_DIR"
echo "   远程目录: $REMOTE_DIR"
echo ""

# 同步文件（排除 .git 和 __pycache__）
rsync -avz \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='.cache' \
  "$PROJECT_DIR/" "arduino@$BOARD_IP:$REMOTE_DIR/"

echo ""
echo "🔄 重启应用..."
ssh arduino@$BOARD_IP "cd $REMOTE_DIR && arduino-app-cli app stop . 2>/dev/null; arduino-app-cli app start . -v"

echo ""
echo "✅ 部署完成！"
echo "🌐 网页界面: http://$BOARD_IP:7000"
echo "📋 查看日志: ssh arduino@$BOARD_IP 'arduino-app-cli app logs $REMOTE_DIR --follow'"
