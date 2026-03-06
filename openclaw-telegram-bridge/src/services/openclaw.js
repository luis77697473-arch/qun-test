/**
 * OpenClaw API 客户端
 *
 * 通过 OpenClaw Gateway 暴露的 /v1/chat/completions 端点通信
 * 该端点兼容 OpenAI API 格式
 *
 * 消息流: Telegram → 本桥接服务 → OpenClaw Gateway → LLM → 原路返回
 */

const logger = require('../utils/logger');

// ─── 会话存储（内存，重启后清空） ───
// key: Telegram chatId, value: messages 数组
const sessions = new Map();

// 每个会话最多保留的历史轮数（一问一答 = 2 条）
const MAX_HISTORY = 40;

/**
 * 获取或创建会话
 */
function getSession(chatId) {
  if (!sessions.has(chatId)) {
    sessions.set(chatId, []);
  }
  return sessions.get(chatId);
}

/**
 * 清除指定会话
 */
function clearSession(chatId) {
  sessions.delete(chatId);
  logger.info(`会话已清除: chatId=${chatId}`);
}

/**
 * 向 OpenClaw 发送消息并获取回复
 *
 * @param {string} chatId - Telegram chat ID（用于会话隔离）
 * @param {string} userMessage - 用户发送的文本
 * @param {object} config - 应用配置
 * @returns {Promise<string>} AI 回复文本
 */
async function chat(chatId, userMessage, config) {
  const history = getSession(chatId);

  // 添加用户消息到历史
  history.push({ role: 'user', content: userMessage });

  // 裁剪过长的历史
  while (history.length > MAX_HISTORY) {
    history.shift();
  }

  // 构建请求 messages 数组
  const messages = [];
  if (config.systemPrompt) {
    messages.push({ role: 'system', content: config.systemPrompt });
  }
  messages.push(...history);

  // 构建请求体
  const body = { messages, stream: false };
  if (config.openclawModel) {
    body.model = config.openclawModel;
  }

  // 构建请求头
  const headers = { 'Content-Type': 'application/json' };
  if (config.openclawApiKey) {
    headers['Authorization'] = `Bearer ${config.openclawApiKey}`;
  }

  const url = `${config.openclawApiUrl}/v1/chat/completions`;
  logger.debug(`请求 OpenClaw: ${url}`, { chatId, msgCount: messages.length });

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), config.apiTimeout);

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => '');
      throw new Error(`OpenClaw API 返回 ${res.status}: ${errText.slice(0, 500)}`);
    }

    const data = await res.json();

    // OpenAI 兼容格式：data.choices[0].message.content
    const reply =
      data.choices?.[0]?.message?.content ||
      data.message?.content ||
      data.content ||
      '';

    if (!reply) {
      throw new Error('OpenClaw 返回了空回复');
    }

    // 存入历史
    history.push({ role: 'assistant', content: reply });

    logger.debug(`OpenClaw 回复: chatId=${chatId}, len=${reply.length}`);
    return reply;
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * 检测 OpenClaw Gateway 是否可达
 */
async function healthCheck(config) {
  try {
    const res = await fetch(`${config.openclawApiUrl}/v1/models`, {
      method: 'GET',
      headers: config.openclawApiKey
        ? { Authorization: `Bearer ${config.openclawApiKey}` }
        : {},
      signal: AbortSignal.timeout(5000),
    });
    return { ok: res.ok, status: res.status };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

module.exports = { chat, clearSession, healthCheck };
