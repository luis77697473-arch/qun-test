const logger = require('../utils/logger');

/**
 * /ping 命令 - 检测 Bot 是否在线，返回延迟
 */
function register(bot) {
  bot.command('ping', (ctx) => {
    const start = Date.now();
    logger.info(`/ping from ${ctx.from.first_name} (ID: ${ctx.from.id})`);

    return ctx.reply(`🏓 Pong! 延迟: ${Date.now() - start}ms`);
  });
}

module.exports = { register };
