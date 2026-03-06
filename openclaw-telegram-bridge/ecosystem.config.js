/**
 * PM2 配置文件
 * 启动: pm2 start ecosystem.config.js
 */
module.exports = {
  apps: [
    {
      name: 'openclaw-tg-bridge',
      script: 'src/bot.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'production',
      },
      error_file: 'logs/error.log',
      out_file: 'logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
    },
  ],
};
