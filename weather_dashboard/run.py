"""
天气仪表盘 · 主程序
====================
一次运行即完成全部流程：
1. 检测并安装依赖（rich, jinja2）
2. 初始化数据库
3. 模拟获取所有城市的实时天气
4. 生成第一个城市的 24 小时预报
5. 将数据存入 SQLite 历史记录
6. 在终端渲染精美表格
7. 生成静态 HTML 仪表盘网页
"""

import subprocess
import sys


def ensure_dependencies():
    """自动检测并安装所需依赖包"""
    required = {"rich": "rich", "jinja2": "Jinja2"}
    for module_name, pip_name in required.items():
        try:
            __import__(module_name)
        except ImportError:
            print(f"[安装] 正在安装 {pip_name} ...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pip_name, "-q"]
            )
            print(f"[安装] {pip_name} 安装完成 ✓")


def main():
    # ——— 第一步：确保依赖就绪 ———
    ensure_dependencies()

    # 依赖安装后再导入（避免未安装时 import 报错）
    from rich.console import Console
    from rich.panel import Panel

    from weather_dashboard.mock_service import get_current_weather, get_forecast_24h, CITY_PROFILES
    from weather_dashboard.history_db import init_db, save_weather, get_latest_records
    from weather_dashboard.terminal_ui import render_current_weather, render_forecast, render_history
    from weather_dashboard.web_ui import generate_html

    console = Console()

    # ——— 第二步：初始化数据库 ———
    init_db()
    console.print("[bold green]✓[/bold green] 数据库初始化完成")

    # ——— 第三步：获取所有城市实时天气 ———
    cities = list(CITY_PROFILES.keys())
    current_weather_list = []

    for city in cities:
        weather = get_current_weather(city)
        current_weather_list.append(weather)
        # 存入数据库历史
        save_weather(weather)

    console.print(f"[bold green]✓[/bold green] 已获取 {len(cities)} 个城市的实时天气数据")

    # ——— 第四步：生成第一个城市的 24 小时预报 ———
    forecast_city = cities[0]
    forecast_data = get_forecast_24h(forecast_city)
    console.print(f"[bold green]✓[/bold green] 已生成 {forecast_city} 的 24 小时预报")

    # ——— 第五步：终端渲染 ———
    render_current_weather(current_weather_list)
    render_forecast(forecast_city, forecast_data)

    # 显示历史记录（取最新10条）
    history = get_latest_records(10)
    render_history(history)

    # ——— 第六步：生成 HTML 网页 ———
    html_path = generate_html(
        current_weather=current_weather_list,
        forecast_city=forecast_city,
        forecast=forecast_data,
        history=history,
    )
    console.print(
        Panel(
            f"[bold]网页仪表盘已生成！[/bold]\n\n"
            f"📁 文件路径: [cyan]{html_path}[/cyan]\n"
            f"🌐 在浏览器中打开即可查看",
            title="✅ 全部完成",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
