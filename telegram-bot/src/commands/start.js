const logger = require('../utils/logger');

/**
 * /start 命令 - 用户首次启动 Bot 时触发
 */
function register(bot) {
  bot.start((ctx) => {
    const user = ctx.from;
    logger.info(`/start from ${user.first_name} (ID: ${user.id})`);

    return ctx.reply(
      `👋 你好，${user.first_name}！\n\n` +
      `我是一个 Telegram Bot，以下是我支持的命令：\n\n` +
      `/start - 查看欢迎信息\n` +
      `/help  - 查看帮助\n` +
      `/ping  - 测试 Bot 是否在线`
    );
  });
}

module.exports = { register };
