"""
网页仪表盘生成模块
===================
使用 Jinja2 模板引擎将天气数据渲染为精美的单文件 HTML 页面。
页面使用 Tailwind CSS CDN，实现自适应响应式布局。
"""

import os
from jinja2 import Template
from datetime import datetime

# HTML 模板 —— 单文件包含所有样式和脚本
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>天气仪表盘 | Weather Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* 自定义渐变背景 */
        body {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
            min-height: 100vh;
        }
        /* 卡片玻璃拟态效果 */
        .glass-card {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.12);
        }
        /* 温度颜色 */
        .temp-hot { color: #ef4444; }
        .temp-warm { color: #f97316; }
        .temp-mild { color: #22c55e; }
        .temp-cool { color: #3b82f6; }
        .temp-cold { color: #06b6d4; font-weight: bold; }
        /* 表格行悬停效果 */
        .hover-row:hover { background: rgba(255,255,255,0.06); }
    </style>
</head>
<body class="text-gray-200 font-sans">

    <!-- 顶部标题栏 -->
    <header class="py-8 text-center">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            🌤️ 天气仪表盘
        </h1>
        <p class="mt-2 text-gray-400">生成时间：{{ generated_at }}</p>
    </header>

    <main class="max-w-7xl mx-auto px-4 pb-12">

        <!-- 实时天气卡片网格 -->
        <section class="mb-10">
            <h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">
                <span class="text-3xl">🌍</span> 实时天气
            </h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {% for w in current_weather %}
                <div class="glass-card rounded-2xl p-6 transition-transform hover:scale-[1.02]">
                    <div class="flex justify-between items-start mb-3">
                        <h3 class="text-xl font-bold text-white">{{ w.city }}</h3>
                        <span class="text-2xl">{{ w.condition.split(' ')[0] }}</span>
                    </div>
                    <div class="text-5xl font-bold mb-2 {{ 'temp-hot' if w.temperature >= 35 else 'temp-warm' if w.temperature >= 30 else 'temp-mild' if w.temperature >= 10 else 'temp-cool' if w.temperature >= 0 else 'temp-cold' }}">
                        {{ w.temperature }}°C
                    </div>
                    <p class="text-gray-400 text-sm mb-4">{{ w.condition }}</p>
                    <div class="grid grid-cols-3 gap-2 text-center text-sm">
                        <div class="bg-white/5 rounded-lg p-2">
                            <div class="text-gray-400">湿度</div>
                            <div class="font-semibold {{ 'text-yellow-400' if w.humidity > 80 else 'text-white' }}">{{ w.humidity }}%</div>
                        </div>
                        <div class="bg-white/5 rounded-lg p-2">
                            <div class="text-gray-400">风速</div>
                            <div class="font-semibold {{ 'text-red-400' if w.wind_speed > 8 else 'text-white' }}">{{ w.wind_speed }} m/s</div>
                        </div>
                        <div class="bg-white/5 rounded-lg p-2">
                            <div class="text-gray-400">气压</div>
                            <div class="font-semibold text-white">{{ w.pressure }} hPa</div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- 24小时预报 -->
        <section class="mb-10">
            <h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">
                <span class="text-3xl">📅</span> 24 小时预报（{{ forecast_city }}）
            </h2>
            <div class="glass-card rounded-2xl overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b border-white/10 text-gray-400">
                                <th class="py-3 px-4 text-left">时间</th>
                                <th class="py-3 px-4 text-center">天气</th>
                                <th class="py-3 px-4 text-center">温度</th>
                                <th class="py-3 px-4 text-center">湿度</th>
                                <th class="py-3 px-4 text-center">风速</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for f in forecast %}
                            <tr class="border-b border-white/5 hover-row">
                                <td class="py-2 px-4 text-gray-300">{{ f.time }}</td>
                                <td class="py-2 px-4 text-center">{{ f.condition }}</td>
                                <td class="py-2 px-4 text-center {{ 'temp-hot' if f.temperature >= 35 else 'temp-warm' if f.temperature >= 30 else 'temp-mild' if f.temperature >= 10 else 'temp-cool' if f.temperature >= 0 else 'temp-cold' }}">
                                    {{ f.temperature }}°C
                                </td>
                                <td class="py-2 px-4 text-center">{{ f.humidity }}%</td>
                                <td class="py-2 px-4 text-center">{{ f.wind_speed }} m/s</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- 历史记录 -->
        <section>
            <h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">
                <span class="text-3xl">📜</span> 最近查询历史
            </h2>
            <div class="glass-card rounded-2xl overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b border-white/10 text-gray-400">
                                <th class="py-3 px-4 text-left">城市</th>
                                <th class="py-3 px-4 text-center">时间</th>
                                <th class="py-3 px-4 text-center">天气</th>
                                <th class="py-3 px-4 text-center">温度</th>
                                <th class="py-3 px-4 text-center">湿度</th>
                                <th class="py-3 px-4 text-center">风速</th>
                                <th class="py-3 px-4 text-center">气压</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for r in history %}
                            <tr class="border-b border-white/5 hover-row">
                                <td class="py-2 px-4 font-medium text-white">{{ r.city }}</td>
                                <td class="py-2 px-4 text-center text-gray-400">{{ r.timestamp }}</td>
                                <td class="py-2 px-4 text-center">{{ r.condition }}</td>
                                <td class="py-2 px-4 text-center {{ 'temp-hot' if r.temperature >= 35 else 'temp-warm' if r.temperature >= 30 else 'temp-mild' if r.temperature >= 10 else 'temp-cool' if r.temperature >= 0 else 'temp-cold' }}">
                                    {{ r.temperature }}°C
                                </td>
                                <td class="py-2 px-4 text-center">{{ r.humidity }}%</td>
                                <td class="py-2 px-4 text-center">{{ r.wind_speed }} m/s</td>
                                <td class="py-2 px-4 text-center">{{ r.pressure }} hPa</td>
                            </tr>
                            {% endfor %}
                            {% if not history %}
                            <tr><td colspan="7" class="py-8 text-center text-gray-500">暂无历史记录</td></tr>
                            {% endif %}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

    </main>

    <!-- 页脚 -->
    <footer class="text-center py-6 text-gray-500 text-sm">
        Weather Dashboard · 模拟数据，仅供演示
    </footer>

</body>
</html>"""


def generate_html(
    current_weather: list[dict],
    forecast_city: str,
    forecast: list[dict],
    history: list[dict],
    output_path: str = None,
) -> str:
    """
    生成天气仪表盘 HTML 文件。

    参数:
        current_weather: 各城市实时天气列表
        forecast_city:   预报展示的城市名
        forecast:        24小时预报数据
        history:         最近历史查询记录
        output_path:     输出文件路径，默认为当前目录下的 weather_dashboard.html

    返回:
        生成的 HTML 文件的绝对路径
    """
    if output_path is None:
        # 输出到项目根目录（weather_dashboard 的上层）
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "weather_dashboard.html"
        )

    # 渲染模板
    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        current_weather=current_weather,
        forecast_city=forecast_city,
        forecast=forecast,
        history=history,
    )

    # 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return os.path.abspath(output_path)
