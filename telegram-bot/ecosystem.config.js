/**
 * PM2 配置文件
 * 启动命令: pm2 start ecosystem.config.js
 */
module.exports = {
  apps: [
    {
      name: 'telegram-bot',
      script: 'src/bot.js',
      instances: 1,              // Telegram Bot 只能单实例运行
      autorestart: true,          // 崩溃后自动重启
      watch: false,               // 生产环境不要开 watch
      max_memory_restart: '200M', // 内存超过 200MB 自动重启
      env: {
        NODE_ENV: 'production',
      },
      // 日志配置
      error_file: 'logs/error.log',
      out_file: 'logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
    },
  ],
};
