require('dotenv').config();

const { Telegraf } = require('telegraf');
const logger = require('./utils/logger');
const { loadConfig } = require('./utils/config');
const openclaw = require('./services/openclaw');

// ─── 加载配置 ───
const config = loadConfig();

// ─── 创建 Bot 实例 ───
const bot = new Telegraf(config.telegramToken);

// ─── 中间件：用户权限检查 ───
bot.use((ctx, next) => {
  if (config.allowedUserIds.length > 0) {
    const userId = ctx.from?.id;
    if (!config.allowedUserIds.includes(userId)) {
      logger.warn(`未授权用户: ${ctx.from?.first_name} (ID: ${userId})`);
      return ctx.reply('⛔ 你没有权限使用此 Bot。请联系管理员。');
    }
  }
  return next();
});

// ─── /start 命令 ───
bot.start((ctx) => {
  const user = ctx.from;
  logger.info(`/start from ${user.first_name} (ID: ${user.id})`);
  return ctx.reply(
    `👋 你好，${user.first_name}！\n\n` +
    `我是 OpenClaw AI 助手，直接发消息给我就能和 AI 对话。\n\n` +
    `支持的命令：\n` +
    `/start - 欢迎信息\n` +
    `/help  - 帮助菜单\n` +
    `/new   - 开始新对话（清除历史）\n` +
    `/ping  - 测试连接\n` +
    `/status - 检查 OpenClaw 状态`
  );
});

// ─── /help 命令 ───
bot.help((ctx) => {
  logger.info(`/help from ${ctx.from.first_name} (ID: ${ctx.from.id})`);
  return ctx.reply(
    `📖 使用帮助\n\n` +
    `直接发送任何文字，AI 会回复你。\n` +
    `支持多轮对话，AI 会记住上下文。\n\n` +
    `命令列表：\n` +
    `/new    - 清除对话历史，开始新话题\n` +
    `/ping   - 检测 Bot 是否在线\n` +
    `/status - 检查 OpenClaw Gateway 连接状态\n\n` +
    `提示：如果回复很慢，可能是 AI 模型正在思考，请耐心等待。`
  );
});

// ─── /new 命令：重置对话 ───
bot.command('new', (ctx) => {
  openclaw.clearSession(String(ctx.chat.id));
  logger.info(`/new from ${ctx.from.first_name} (ID: ${ctx.from.id})`);
  return ctx.reply('🔄 对话已重置，开始新对话吧！');
});

// ─── /ping 命令 ───
bot.command('ping', (ctx) => {
  logger.info(`/ping from ${ctx.from.first_name} (ID: ${ctx.from.id})`);
  return ctx.reply(`🏓 Pong! Bot 在线。`);
});

// ─── /status 命令：检查 OpenClaw 连通性 ───
bot.command('status', async (ctx) => {
  logger.info(`/status from ${ctx.from.first_name} (ID: ${ctx.from.id})`);
  await ctx.reply('⏳ 正在检查 OpenClaw Gateway...');

  const result = await openclaw.healthCheck(config);
  if (result.ok) {
    return ctx.reply(
      `✅ OpenClaw Gateway 正常\n` +
      `地址: ${config.openclawApiUrl}\n` +
      `HTTP ${result.status}`
    );
  }
  return ctx.reply(
    `❌ OpenClaw Gateway 不可达\n` +
    `地址: ${config.openclawApiUrl}\n` +
    `错误: ${result.error || `HTTP ${result.status}`}`
  );
});

// ─── 处理普通文本消息：核心桥接逻辑 ───
bot.on('text', async (ctx) => {
  const text = ctx.message.text;
  const chatId = String(ctx.chat.id);
  const user = ctx.from;

  logger.info(`消息 from ${user.first_name} (ID: ${user.id}): "${text.slice(0, 80)}"`);

  // 发送"正在输入"状态
  await ctx.sendChatAction('typing');

  // 对于长时间请求，持续发送 typing 状态
  const typingInterval = setInterval(() => {
    ctx.sendChatAction('typing').catch(() => {});
  }, 4000);

  try {
    const reply = await openclaw.chat(chatId, text, config);

    // 如果回复超过 Telegram 限制，分段发送
    const chunks = splitMessage(reply, config.maxReplyLength);
    for (const chunk of chunks) {
      await ctx.reply(chunk, { parse_mode: 'Markdown' }).catch(() => {
        // Markdown 解析失败时退回纯文本
        return ctx.reply(chunk);
      });
    }
  } catch (err) {
    logger.error(`OpenClaw 调用失败 (chatId=${chatId}):`, err.message);

    let userMsg = '❌ AI 回复失败，请稍后再试。';
    if (err.message.includes('abort')) {
      userMsg = '⏰ AI 回复超时，请稍后重试或发送 /new 开始新对话。';
    } else if (err.message.includes('ECONNREFUSED')) {
      userMsg = '🔌 无法连接到 OpenClaw Gateway，请检查服务是否启动。';
    }
    await ctx.reply(userMsg);
  } finally {
    clearInterval(typingInterval);
  }
});

/**
 * 将长文本分割为不超过 maxLen 的段落
 */
function splitMessage(text, maxLen) {
  if (text.length <= maxLen) return [text];

  const chunks = [];
  let remaining = text;
  while (remaining.length > 0) {
    if (remaining.length <= maxLen) {
      chunks.push(remaining);
      break;
    }
    // 在换行符处分割，如果没有就按最大长度硬切
    let splitAt = remaining.lastIndexOf('\n', maxLen);
    if (splitAt < maxLen * 0.3) {
      splitAt = maxLen;
    }
    chunks.push(remaining.slice(0, splitAt));
    remaining = remaining.slice(splitAt).replace(/^\n/, '');
  }
  return chunks;
}

// ─── 全局错误处理 ───
bot.catch((err, ctx) => {
  logger.error(`Bot 错误 [${ctx.updateType}]:`, err.message);
});

// ─── 优雅退出 ───
function shutdown(signal) {
  logger.info(`收到 ${signal}，正在停止...`);
  bot.stop(signal);
}
process.once('SIGINT', () => shutdown('SIGINT'));
process.once('SIGTERM', () => shutdown('SIGTERM'));

// ─── 启动 ───
bot.launch()
  .then(() => {
    logger.info('=== OpenClaw Telegram Bridge 启动成功 ===');
    logger.info(`Bot: @${bot.botInfo.username}`);
    logger.info(`OpenClaw: ${config.openclawApiUrl}`);
    logger.info(`用户白名单: ${config.allowedUserIds.length > 0 ? config.allowedUserIds.join(', ') : '全部放行'}`);
  })
  .catch((err) => {
    logger.error('启动失败:', err.message);
    process.exit(1);
  });
