# OpenClaw Telegram Bridge

将 Telegram Bot 接入 OpenClaw AI Gateway 的桥接服务。

**消息流：** 用户 Telegram 消息 → 本桥接服务 → OpenClaw `/v1/chat/completions` → AI 回复 → Telegram

---

## 目录

1. [方案分析：为什么需要桥接服务](#1-方案分析)
2. [项目结构](#2-项目结构)
3. [前置准备](#3-前置准备)
4. [本地测试](#4-本地测试)
5. [服务器部署](#5-服务器部署)
6. [PM2 守护方案](#6-pm2-守护方案)
7. [systemd 守护方案](#7-systemd-守护方案)
8. [上线验证](#8-上线验证)
9. [调试与排查](#9-调试与排查)

---

## 1. 方案分析

### OpenClaw 内置 Telegram Channel

OpenClaw 原生支持 Telegram，配置方式：

```json5
// ~/.openclaw/openclaw.config.json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "你的Token",
      dmPolicy: "open",
      allowFrom: ["*"]
    }
  }
}
```

如果你看到 **"Channel config schema unavailable"**，通常有三个原因：

| 原因 | 排查命令 | 解决方法 |
|------|---------|---------|
| OpenClaw 版本过旧 | `openclaw --version` | `npm update -g openclaw@latest` |
| 配置文件格式错误 | `openclaw doctor` | 检查 JSON5 语法 |
| Telegram channel 模块未加载 | `openclaw channels status` | 重新安装或升级 |

### 为什么用桥接服务

当内置 channel 不可用时，桥接服务是最稳的替代方案：

- **解耦**：Bot 和 OpenClaw 独立运行，互不影响
- **灵活**：可以自定义消息处理逻辑、过滤、限流
- **兼容**：通过 OpenAI 兼容的 `/v1/chat/completions` API，适配任何版本的 OpenClaw
- **简单**：纯 Node.js，不需要改 OpenClaw 任何源码

---

## 2. 项目结构

```
openclaw-telegram-bridge/
├── src/
│   ├── bot.js                  # 入口：Telegram Bot + 桥接逻辑
│   ├── services/
│   │   └── openclaw.js         # OpenClaw API 客户端 + 会话管理
│   └── utils/
│       ├── config.js           # 配置加载与校验
│       └── logger.js           # 日志模块
├── .env.example                # 环境变量模板
├── .gitignore
├── ecosystem.config.js         # PM2 配置
├── openclaw-tg-bridge.service  # systemd 服务文件
├── package.json
└── README.md
```

---

## 3. 前置准备

### 3.1 创建 Telegram Bot

1. Telegram 搜索 `@BotFather`，发送 `/newbot`
2. 按提示设置名称和用户名
3. 获得 Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 3.2 确认 OpenClaw 正在运行

```bash
# 检查 OpenClaw 版本
openclaw --version

# 检查 Gateway 是否启动
curl -s http://127.0.0.1:18789/v1/models
```

如果 OpenClaw 还没安装：

```bash
# 需要 Node.js >= 22
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

安装完成后，打开 `http://127.0.0.1:18789/` 确认 Control UI 可访问。

---

## 4. 本地测试

### 4.1 安装依赖

```bash
cd openclaw-telegram-bridge
npm install
```

### 4.2 配置环境变量

```bash
cp .env.example .env
nano .env
```

最少需要填两个值：

```
TELEGRAM_BOT_TOKEN=你从BotFather获取的Token
OPENCLAW_API_URL=http://127.0.0.1:18789
```

### 4.3 启动

```bash
npm start
```

正常输出：

```
[...] [INFO] === OpenClaw Telegram Bridge 启动成功 ===
[...] [INFO] Bot: @your_bot_username
[...] [INFO] OpenClaw: http://127.0.0.1:18789
[...] [INFO] 用户白名单: 全部放行
```

### 4.4 测试

在 Telegram 中找到你的 Bot：

1. 发送 `/start` → 看到欢迎信息
2. 发送 `/status` → 显示 OpenClaw 连接状态
3. 发送 `你好` → 收到 AI 回复
4. 发送 `/new` → 清除对话历史

`Ctrl+C` 停止。

---

## 5. 服务器部署（Ubuntu 22.04）

### 5.1 安装 Node.js

桥接服务只需 Node.js 18+：

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
node -v
```

如果还要在同一台机器上运行 OpenClaw，则需要 Node.js 22+：

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 5.2 上传项目

```bash
# 方式一：Git
cd /home/ubuntu
git clone 你的仓库 openclaw-telegram-bridge
cd openclaw-telegram-bridge

# 方式二：scp（从本地）
scp -r openclaw-telegram-bridge/ ubuntu@服务器IP:/home/ubuntu/
```

### 5.3 安装并配置

```bash
cd /home/ubuntu/openclaw-telegram-bridge
npm install --production
cp .env.example .env
nano .env
```

### 5.4 确认 OpenClaw Gateway 在运行

```bash
curl -s http://127.0.0.1:18789/v1/models
```

如果返回 JSON 数据，说明 OpenClaw Gateway 正常。

### 5.5 测试启动

```bash
node src/bot.js
```

确认正常后 `Ctrl+C`，然后选择 PM2 或 systemd 方案。

---

## 6. PM2 守护方案

### 6.1 安装 PM2

```bash
sudo npm install -g pm2
```

### 6.2 启动

```bash
cd /home/ubuntu/openclaw-telegram-bridge
mkdir -p logs
pm2 start ecosystem.config.js
```

### 6.3 开机自启

```bash
pm2 startup
# 复制并执行输出的 sudo 命令
pm2 save
```

### 6.4 常用命令速查

```bash
pm2 status                              # 查看状态
pm2 logs openclaw-tg-bridge             # 实时日志
pm2 logs openclaw-tg-bridge --lines 100 # 最近100行
pm2 restart openclaw-tg-bridge          # 重启
pm2 stop openclaw-tg-bridge             # 停止
pm2 delete openclaw-tg-bridge           # 删除进程
pm2 monit                               # 实时监控面板
```

---

## 7. systemd 守护方案

### 7.1 安装服务

```bash
sudo cp /home/ubuntu/openclaw-telegram-bridge/openclaw-tg-bridge.service /etc/systemd/system/
sudo systemctl daemon-reload
```

> 如果用户名不是 `ubuntu`，编辑 service 文件修改 `User` 和路径。

### 7.2 启动

```bash
sudo systemctl start openclaw-tg-bridge
sudo systemctl enable openclaw-tg-bridge
```

### 7.3 常用命令速查

```bash
sudo systemctl status openclaw-tg-bridge      # 查看状态
sudo journalctl -u openclaw-tg-bridge -f       # 实时日志
sudo journalctl -u openclaw-tg-bridge -n 50    # 最近50行
sudo systemctl restart openclaw-tg-bridge      # 重启
sudo systemctl stop openclaw-tg-bridge         # 停止
```

---

## 8. 上线验证

| 检查项 | 操作 | 预期 |
|--------|------|------|
| 进程存活 | `pm2 status` | online |
| Bot 在线 | Telegram 发 `/ping` | 🏓 Pong |
| OpenClaw 连通 | Telegram 发 `/status` | ✅ 正常 |
| AI 对话 | Telegram 发 "你好" | 收到 AI 回复 |
| 多轮对话 | 连续发 2-3 条消息 | AI 记住上下文 |
| 重置对话 | Telegram 发 `/new` | 🔄 已重置 |
| 日志正常 | `pm2 logs` | 有请求/回复记录 |
| 崩溃恢复 | `pm2 restart` | Bot 自动恢复 |

---

## 9. 调试与排查

### 开启 Debug 日志

编辑 `.env`：

```
LOG_LEVEL=debug
```

重启后日志会显示 OpenClaw API 请求/响应细节。

### 问题 1：Bot 不回复，日志无报错

```bash
# 确认进程在运行
pm2 status

# 确认 Telegram API 可达
curl -s https://api.telegram.org/bot你的Token/getMe
```

如果 curl 无返回，服务器无法访问 Telegram API，需配置代理或换服务器。

### 问题 2："无法连接到 OpenClaw Gateway"

```bash
# 确认 OpenClaw 在运行
curl -s http://127.0.0.1:18789/v1/models

# 如果失败，检查 OpenClaw 状态
openclaw status
openclaw channels status
```

### 问题 3："OpenClaw API 返回 401"

在 `.env` 中设置 `OPENCLAW_API_KEY`，值为 OpenClaw 配置的 API 密钥。

### 问题 4：AI 回复超时

```bash
# 增大超时时间（毫秒）
# .env
API_TIMEOUT=180000
```

### 问题 5：409 Conflict（Telegram）

同一 Token 有多个 Bot 实例运行：

```bash
ps aux | grep bot.js
pm2 delete all
# 只保留一个实例
pm2 start ecosystem.config.js
```

### 问题 6：想试试 OpenClaw 内置 Telegram Channel

如果你升级了 OpenClaw 并且想切回内置方案：

```bash
# 1. 停掉桥接服务
pm2 stop openclaw-tg-bridge

# 2. 配置 OpenClaw 内置 Telegram channel
openclaw config set channels.telegram.enabled true
openclaw config set channels.telegram.botToken "你的Token"
openclaw config set channels.telegram.dmPolicy "open"
openclaw config set 'channels.telegram.allowFrom' '["*"]'

# 3. 重启 OpenClaw
openclaw restart

# 4. 检查 channel 状态
openclaw channels status
```

如果 `openclaw channels status` 显示 Telegram 为 `connected`，说明内置方案恢复正常，可以删除桥接服务。
