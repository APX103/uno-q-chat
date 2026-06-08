# Arduino UNO Q 表情聊天机器人

AI 聊天机器人，使用板载 8×13 LED 矩阵展示 LLM 的情绪表情。

## 项目结构

```
emoji-chat-bot/
├── app.yaml                    # App Lab 清单（WebUI + SQLite bricks）
├── sketch/
│   ├── sketch.ino              # MCU: LED 矩阵 + Bridge RPC
│   └── sketch.yaml             # MCU 构建配置
├── python/
│   ├── main.py                 # MPU: 智谱GLM + SQLite + WebSocket
│   └── requirements.txt        # Python 依赖
├── assets/
│   └── index.html              # 网页聊天界面（深色主题 + LED 矩阵模拟）
├── deploy.sh                   # 一键部署脚本
└── README.md
```

## 前置条件

- Arduino UNO Q 已开机并连接到 WiFi
- 已设置 SSH 访问（首次通过 App Lab GUI 设置用户名/密码）
- Mac 已安装 `rsync`（系统自带）和 `ssh`（系统自带）

## 部署步骤

### 1. 查找板子 IP

在 App Lab 设置页面查看板子的 IP 地址，或在板子上执行：

```bash
ssh arduino@<UNO_Q_IP>
ip addr show wlan0 | grep inet
```

### 2. 修改 LLM 配置（可选）

`python/main.py` 顶部有 LLM 配置，默认已填好智谱 BigModel：

```python
LLM_API_KEY = "你的 API Key"
LLM_BASE_URL = "https://open.bigmodel.cn/api/coding/paas/v4"
LLM_MODEL = "glm-5-turbo"
```

如需换成其他 OpenAI 兼容 API，改 `LLM_BASE_URL` 和 `LLM_MODEL` 即可。

### 3. 一键部署

```bash
# 在项目根目录执行
chmod +x deploy.sh
./deploy.sh <UNO_Q_IP>

# 示例
./deploy.sh 192.168.1.100
```

脚本会自动完成：
1. `rsync` 同步所有文件到板子 `~/ArduinoApps/emoji-chat-bot/`
2. SSH 到板子执行 `arduino-app-cli app stop . && arduino-app-cli app start . -v`

### 4. 打开网页

浏览器访问：

```
http://<UNO_Q_IP>:7000
```

## 手动部署（不习惯用脚本）

```bash
# ── 本地 Mac ──
rsync -avz --exclude='.git' --exclude='__pycache__' \
  ./emoji-chat-bot/ arduino@<UNO_Q_IP>:~/ArduinoApps/emoji-chat-bot/

# ── SSH 到板子 ──
ssh arduino@<UNO_Q_IP>

# 进入项目目录
cd ~/ArduinoApps/emoji-chat-bot

# 首次部署（会编译 sketch + 安装依赖，较慢）
arduino-app-cli app start . -v

# 后续修改代码后只需重新部署
arduino-app-cli app stop .
arduino-app-cli app start . -v
```

## 调试

```bash
# 实时查看 Python 日志（最常用）
ssh arduino@<UNO_Q_IP>
arduino-app-cli app logs ~/ArduinoApps/emoji-chat-bot --follow

# 查看 MCU sketch 串口输出
arduino-app-cli monitor

# 查看应用列表
arduino-app-cli app list

# 停止应用
arduino-app-cli app stop ~/ArduinoApps/emoji-chat-bot
```

## 设置开机自启（可选）

```bash
ssh arduino@<UNO_Q_IP>
arduino-app-cli properties set default ~/ArduinoApps/emoji-chat-bot
```

## 注意事项

- `arduino-app-cli` 运行在 **板子的 Debian 系统上**，不在 Mac 上
- 首次启动会编译 MCU sketch + 安装 Python 依赖，需要 1-3 分钟
- 对话记录保存在板子 SQLite 数据库 `/app/data/chat_history.db`，重启不丢失
- 如果修改了 `app.yaml` 的 bricks 列表，需要重新部署才能生效

## 技术栈

| 层 | 技术 |
|----|------|
| MCU | Arduino C++ / Zephyr RTOS / STM32U585 |
| MPU | Python / Debian Linux / Qualcomm QRB2210 |
| LLM | 智谱 BigModel GLM-5-Turbo（OpenAI 兼容 API） |
| 通信 | Bridge RPC（MessagePack over UART） |
| 存储 | SQLite via `arduino:dbstorage_sqlstore` brick |
| 前端 | Socket.IO + 原生 JS，深色毛玻璃 UI |

## License

MIT
