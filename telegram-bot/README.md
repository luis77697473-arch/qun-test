# Telegram Bot (Node.js + Telegraf)

一个最小可用的自部署 Telegram Bot，支持 `/start` `/help` `/ping` 命令。

---

## 1. 技术栈

| 组件 | 选择 | 理由 |
|------|------|------|
| 运行时 | Node.js 18+ | 生态成熟，异步 I/O 天然适合 Bot |
| 框架 | Telegraf 4.x | Telegram Bot 最流行的 Node.js 框架，API 简洁 |
| 配置管理 | dotenv | 业界标准，安全管理敏感信息 |
| 进程守护 | PM2 / systemd | 崩溃自动重启，开机自启 |

---

## 2. 项目结构

```
telegram-bot/
├── src/
│   ├── bot.js              # 入口文件：创建 Bot、注册命令、启动
│   ├── commands/
│   │   ├── start.js        # /start 命令
│   │   ├── help.js         # /help 命令
│   │   └── ping.js         # /ping 命令
│   └── utils/
│       └── logger.js       # 日志模块
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略规则
├── ecosystem.config.js     # PM2 配置
├── telegram-bot.service    # systemd 服务文件
├── package.json            # 项目依赖
└── README.md               # 本文件
```

---

## 3. 前置准备：创建 Telegram Bot

1. 打开 Telegram，搜索 `@BotFather`
2. 发送 `/newbot`
3. 按提示输入 Bot 名称和用户名
4. 获得 Token（格式类似 `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）
5. 保存好这个 Token

---

## 4. 本地测试

### 4.1 克隆并安装依赖

```bash
cd telegram-bot
npm install
```

### 4.2 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，把 `your_bot_token_here` 替换为你的真实 Token：

```bash
nano .env
```

内容：

```
TELEGRAM_BOT_TOKEN=你的真实Token
LOG_LEVEL=info
```

### 4.3 启动 Bot

```bash
npm start
```

看到以下输出说明启动成功：

```
[2026-03-06T12:00:00.000Z] [INFO] Bot 启动成功！正在监听消息...
[2026-03-06T12:00:00.000Z] [INFO] Bot 用户名: @your_bot_username
```

### 4.4 测试命令

打开 Telegram，找到你的 Bot，依次发送：

- `/start` → 应回复欢迎信息
- `/help` → 应回复帮助菜单
- `/ping` → 应回复 Pong 和延迟

按 `Ctrl+C` 停止 Bot。

---

## 5. 服务器部署（Ubuntu 22.04）

### 5.1 安装 Node.js 18

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

验证：

```bash
node -v
npm -v
```

### 5.2 上传项目到服务器

方式一：通过 Git 克隆

```bash
cd /home/ubuntu
git clone 你的仓库地址 telegram-bot
cd telegram-bot
```

方式二：通过 scp 上传

```bash
# 在本地执行
scp -r telegram-bot/ ubuntu@你的服务器IP:/home/ubuntu/
```

### 5.3 安装依赖并配置

```bash
cd /home/ubuntu/telegram-bot
npm install --production
cp .env.example .env
nano .env
```

填入你的 `TELEGRAM_BOT_TOKEN`。

### 5.4 测试运行

```bash
node src/bot.js
```

确认输出正常后 `Ctrl+C` 停止，然后选择 PM2 或 systemd 方案长期运行。

---

## 6. 方案 A：PM2 部署（推荐新手使用）

### 6.1 安装 PM2

```bash
sudo npm install -g pm2
```

### 6.2 启动 Bot

```bash
cd /home/ubuntu/telegram-bot
pm2 start ecosystem.config.js
```

### 6.3 设置开机自启

```bash
pm2 startup
# 按照输出提示复制并执行那条 sudo 命令
pm2 save
```

### 6.4 常用命令

```bash
# 查看状态
pm2 status

# 查看日志（实时）
pm2 logs telegram-bot

# 查看最近 100 行日志
pm2 logs telegram-bot --lines 100

# 重启
pm2 restart telegram-bot

# 停止
pm2 stop telegram-bot

# 删除进程
pm2 delete telegram-bot
```

---

## 7. 方案 B：systemd 部署

### 7.1 复制服务文件

```bash
sudo cp /home/ubuntu/telegram-bot/telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
```

> 注意：如果你的用户名不是 `ubuntu`，或项目路径不同，需编辑 service 文件修改 `User` 和 `WorkingDirectory`。

### 7.2 启动服务

```bash
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot
```

### 7.3 常用命令

```bash
# 查看状态
sudo systemctl status telegram-bot

# 查看日志（实时跟踪）
sudo journalctl -u telegram-bot -f

# 查看最近 50 行日志
sudo journalctl -u telegram-bot -n 50

# 重启
sudo systemctl restart telegram-bot

# 停止
sudo systemctl stop telegram-bot
```

---

## 8. 上线验证清单

部署完成后，逐项检查：

| 检查项 | 命令 / 操作 | 预期结果 |
|--------|------------|----------|
| 进程在运行 | `pm2 status` 或 `systemctl status telegram-bot` | 状态为 online / active |
| /start 命令 | Telegram 中发送 `/start` | 收到欢迎信息 |
| /help 命令 | Telegram 中发送 `/help` | 收到帮助菜单 |
| /ping 命令 | Telegram 中发送 `/ping` | 收到 Pong 和延迟 |
| 日志正常 | `pm2 logs` 或 `journalctl -u telegram-bot -f` | 有命令处理记录 |
| 崩溃恢复 | `pm2 restart` 或 `systemctl restart` | Bot 自动恢复在线 |

---

## 9. 常见问题排查

### 问题 1：启动报错 "请在 .env 文件中设置 TELEGRAM_BOT_TOKEN"

**原因**：没有创建 `.env` 文件，或 Token 没填。

```bash
# 确认 .env 存在
ls -la .env

# 确认 Token 已填写（不会输出 Token 内容，只检查文件非空）
wc -l .env
```

### 问题 2：启动报错 "409: Conflict"

**原因**：同一个 Token 有多个 Bot 实例在运行。

```bash
# 检查是否有重复进程
ps aux | grep bot.js

# 杀掉多余进程
pm2 delete all
# 或
sudo systemctl stop telegram-bot
```

只保留一个实例。

### 问题 3：Bot 不回复消息

**排查步骤**：

```bash
# 1. 确认进程在运行
pm2 status

# 2. 查看日志有无报错
pm2 logs telegram-bot --lines 50

# 3. 测试网络连通性（服务器能否访问 Telegram API）
curl -s https://api.telegram.org/bot你的Token/getMe
```

如果 curl 无返回，说明服务器网络无法访问 Telegram API，需要配置代理。

### 问题 4：服务器重启后 Bot 没有自动启动

**PM2 方案**：

```bash
pm2 startup
# 执行输出的 sudo 命令
pm2 save
```

**systemd 方案**：

```bash
sudo systemctl enable telegram-bot
```

### 问题 5：内存不断增长

```bash
# 查看内存使用
pm2 monit

# PM2 已配置 max_memory_restart: 200M，超过会自动重启
```
