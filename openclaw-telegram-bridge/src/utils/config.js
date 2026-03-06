/**
 * 配置模块 - 集中管理所有环境变量，启动时校验
 */

function loadConfig() {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  if (!token || token === 'your_bot_token_here') {
    console.error('[FATAL] 请在 .env 中设置 TELEGRAM_BOT_TOKEN');
    process.exit(1);
  }

  const apiUrl = process.env.OPENCLAW_API_URL;
  if (!apiUrl) {
    console.error('[FATAL] 请在 .env 中设置 OPENCLAW_API_URL');
    process.exit(1);
  }

  // 解析允许的用户 ID 白名单
  const allowedRaw = process.env.ALLOWED_USER_IDS || '';
  const allowedUserIds = allowedRaw
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
    .map(Number);

  return {
    telegramToken: token,
    openclawApiUrl: apiUrl.replace(/\/+$/, ''),  // 去掉尾部斜杠
    openclawApiKey: process.env.OPENCLAW_API_KEY || '',
    openclawModel: process.env.OPENCLAW_MODEL || '',
    systemPrompt: process.env.SYSTEM_PROMPT || '',
    maxReplyLength: parseInt(process.env.MAX_REPLY_LENGTH, 10) || 4000,
    apiTimeout: parseInt(process.env.API_TIMEOUT, 10) || 120000,
    allowedUserIds,  // 空数组 = 允许所有人
  };
}

module.exports = { loadConfig };
