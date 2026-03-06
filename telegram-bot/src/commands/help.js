const logger = require('../utils/logger');

/**
 * /help 命令 - 显示帮助信息
 */
function register(bot) {
  bot.help((ctx) => {
    logger.info(`/help from ${ctx.from.first_name} (ID: ${ctx.from.id})`);

    return ctx.reply(
      `📖 帮助菜单\n\n` +
      `可用命令：\n` +
      `/start - 查看欢迎信息\n` +
      `/help  - 查看帮助（你在这里）\n` +
      `/ping  - 测试 Bot 是否在线\n\n` +
      `如有问题，请联系管理员。`
    );
  });
}

module.exports = { register };
