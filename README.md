# 🤖 Arduino UNO Q Emoji Chat Bot
> **基于 OpenAI API 兼容大模型与 Arduino UNO Q 开发板的智能情绪表情聊天机器人**

[![Arduino](https://img.shields.io/badge/Hardware-Arduino%20UNO%20Q-00979D?logo=arduino&logoColor=white)](https://www.arduino.cc/)
[![Python](https://img.shields.io/badge/Language-Python%203-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![LLM](https://img.shields.io/badge/LLM-OpenAI%20Compatible-FF6B6B)](https://platform.openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

本项目是一款运行在 **Arduino UNO Q** 硬件平台上的智能 AI 聊天机器人。它不仅能够通过 **OpenAI API 兼容的 LLM 大模型** 与用户进行流畅的智能对话，还能根据 AI 回复中的情感色彩，在板载的 **8×13 LED 矩阵点阵屏** 上实时展现生动逼真的情绪表情（如微笑、大笑、撇嘴、戴墨镜等），实现“AI 情感具身化”的趣味交互。

---

## 🌟 核心特性 (Key Features)

- 🧠 **大模型驱动的情感分析 (LLM-driven Emotion Analysis)**：
  集成支持 **OpenAI API 规范的 LLM**，AI 会根据对话语境自动判断情感，并在回复中嵌入对应情绪标签。
- 🎭 **具身智能表情展示 (Embodied Emoji Display)**：
  在 Arduino UNO Q 的 **8×13 LED 矩阵屏** 上实时绘制高清晰度的动态像素表情（好 😊、一般 🙂、难受 😟、差 🙁、酷 😎、危险 ⚠️、未知 ❓）。
- 📂 **多会话管理与持久化 (Multi-Session & SQLite Persistence)**：
  支持在前端创建、切换、删除和管理多个独立的聊天会话。对话记录通过板载的 `arduino:dbstorage_sqlstore` 砖块（Brick）安全持久化保存在 **SQLite 数据库** 中，重启不丢失。
- 🖥️ **现代感深色毛玻璃 UI (Modern Glassmorphism WebUI)**：
  采用 Socket.IO 实现双向实时通信，提供精美、流畅、响应式的深色系毛玻璃风格聊天界面，并内置了 **LED 矩阵实时模拟器**，方便在无硬件时进行调试。
- 🔒 **安全配置与一键部署 (Secure Config & One-click Deployment)**：
  支持通过 `.env` 配置文件加载 LLM 密钥，避免 API Token 泄露；提供一键 `rsync` 部署脚本，秒级同步代码并重启应用。

---

## 📂 项目结构 (Project Structure)

```text
emoji-chat-bot/
├── app.yaml                    # App Lab 清单文件（声明依赖的 WebUI 和 SQLite 存储砖块）
├── deploy.sh                   # 一键部署脚本（自动同步代码并重启应用）
├── README.md                   # 项目说明文档
├── sketch/
│   ├── sketch.ino              # MCU 端代码：控制 LED 矩阵显示并提供 Bridge RPC 接口
│   └── sketch.yaml             # MCU 编译配置文件（声明 FQBN 和依赖 of Arduino 库）
├── python/
│   ├── main.py                 # MPU 端代码：LLM 调用、WebSocket 通信、SQLite 存储与业务逻辑
│   ├── .env                    # 本地环境变量配置文件（存放 API Key，已被 git 忽略）
│   └── requirements.txt        # Python 依赖声明
└── assets/
    └── index.html              # 网页聊天界面（集成 Socket.IO、LED 矩阵模拟器及多会话管理）
```

---

## 🛠️ 技术栈与关键字 (Tech Stack & Keywords)

为了方便开发者搜索和学习，本项目涵盖了以下核心技术点：

- **硬件/嵌入式 (Hardware & Embedded)**: `Arduino UNO Q`, `Zephyr RTOS`, `STM32U585`, `MPU (Qualcomm QRB2210)`, `Debian Linux`, `Bridge RPC`, `LED Matrix (8x13 点阵)`
- **人工智能/大模型 (AI & LLM)**: `OpenAI API 兼容 (OpenAI-compatible)`, `LLM 大语言模型`, `情感分析 (Sentiment Analysis)`, `Prompt Engineering (提示词工程)`
- **后端/通信 (Backend & Communication)**: `Python 3`, `WebSocket`, `Socket.IO`, `SQLite`, `MessagePack`, `arduino-app-cli`
- **前端/设计 (Frontend & UI)**: `HTML5`, `CSS Glassmorphism (毛玻璃)`, `Vanilla JS`, `LED Matrix Simulator (点阵模拟器)`

---

## 🚀 快速开始 (Quick Start)

### 1. 前置准备
- **Arduino UNO Q** 开发板已正常开机并连接到 WiFi。
- 已通过 App Lab 开启 SSH 访问，并获取了板子的 IP 地址（例如 `192.168.1.100`）。
- 拥有 **OpenAI 兼容 API** 的 API Key（如 OpenAI 官方、DeepSeek、智谱 AI 等）。

### 2. 配置环境变量
在 `emoji-chat-bot/python/` 目录下创建一个名为 `.env` 的文件，并填入您的 API Key 和配置：

```env
LLM_API_KEY=您的_API_KEY
LLM_BASE_URL=https://api.openai.com/v1  # 或其他 OpenAI 兼容的 API 端点
LLM_MODEL=gpt-4o                        # 调用的模型名称
```

> 💡 **提示**：`.env` 文件已被包含在 `.gitignore` 中，您的 API 密钥不会被提交到 Git 仓库，确保了凭证安全。

### 3. 一键部署
在您的本地 Mac/PC 终端中，赋予部署脚本执行权限并运行（将 `192.168.1.100` 替换为您板子的实际 IP）：

```bash
# 进入项目根目录
chmod +x emoji-chat-bot/deploy.sh

# 执行一键部署
./emoji-chat-bot/deploy.sh 192.168.1.100
```

**部署脚本会自动完成：**
1. 使用 `rsync` 排除无关文件，将代码极速同步到板子的 `~/ArduinoApps/emoji-chat-bot/` 目录。
2. 通过 SSH 登录板子，执行 `arduino-app-cli` 编译 MCU Sketch、安装 Python 依赖并启动应用。

### 4. 访问网页界面
部署完成后，在浏览器中打开：
```text
http://<您的_BOARD_IP>:7000
```
现在，您可以开始与您的 Arduino UNO Q 机器人聊天，并观察它在板载 LED 屏幕上展现出的生动表情了！

---

## 🔧 常用调试命令 (Debugging & CLI)

在开发和调试过程中，您可能需要 SSH 登录到板子（`ssh arduino@<BOARD_IP>`）并使用以下命令：

```bash
# 实时查看 Python 服务日志（最常用，用于观察大模型调用 and WebSocket 消息）
arduino-app-cli app logs ~/ArduinoApps/emoji-chat-bot --follow

# 查看 MCU sketch 的串口打印输出 (Serial Monitor)
arduino-app-cli monitor

# 查看板子上当前运行的应用列表
arduino-app-cli app list

# 停止应用
arduino-app-cli app stop ~/ArduinoApps/emoji-chat-bot
```

---

## 🗺️ 未来规划 (Roadmap / TODO)

我们计划在后续版本中引入以下激动人心的功能：

- [ ] 🔌 **支持 MCP (Model Context Protocol) 工具调用**：
  允许大模型通过 MCP 协议调用外部工具和 API，赋予机器人查天气、控制智能家居、检索网络信息等能力。
- [ ] 🎛️ **支持 Bridge IO 控制**：
  利用 Bridge 协议打通 MPU 与 MCU 的硬件外设（GPIO、ADC、I2C 等），使 AI 能够直接控制板子上的物理传感器或执行器。
- [ ] 🗣️ **语音交互支持 (TTS & STT)**：
  集成语音转文字与文字转语音服务，实现真正的无屏幕、纯语音情感具身交互。

---

## 📜 许可证 (License)

本项目基于 **MIT License** 开源。欢迎自由 Fork、修改和分享！
