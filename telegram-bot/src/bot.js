require('dotenv').config();

const { Telegraf } = require('telegraf');
const logger = require('./utils/logger');

// ─── 检查环境变量 ───
const token = process.env.TELEGRAM_BOT_TOKEN;
if (!token || token === 'your_bot_token_here') {
  logger.error('请在 .env 文件中设置 TELEGRAM_BOT_TOKEN');
  process.exit(1);
}

// ─── 创建 Bot 实例 ───
const bot = new Telegraf(token);

// ─── 注册命令 ───
require('./commands/start').register(bot);
require('./commands/help').register(bot);
require('./commands/ping').register(bot);

// ─── 处理普通文本消息 ───
bot.on('text', (ctx) => {
  logger.debug(`收到消息: "${ctx.message.text}" from ${ctx.from.first_name}`);
  return ctx.reply('我暂时只支持命令操作，请输入 /help 查看支持的命令。');
});

// ─── 全局错误处理 ───
bot.catch((err, ctx) => {
  logger.error(`Bot 错误 [${ctx.updateType}]:`, err.message);
});

// ─── 优雅退出 ───
function shutdown(signal) {
  logger.info(`收到 ${signal}，正在停止 Bot...`);
  bot.stop(signal);
}
process.once('SIGINT', () => shutdown('SIGINT'));
process.once('SIGTERM', () => shutdown('SIGTERM'));

// ─── 启动 Bot ───
bot.launch()
  .then(() => {
    logger.info('Bot 启动成功！正在监听消息...');
    logger.info(`Bot 用户名: @${bot.botInfo.username}`);
  })
  .catch((err) => {
    logger.error('Bot 启动失败:', err.message);
    process.exit(1);
  });
