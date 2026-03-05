"""
终端 UI 渲染模块
=================
使用 rich 库在终端中显示精美的天气表格和预报信息。

颜色策略：
- 温度 ≥ 35℃：红色加粗（高温警告）
- 温度 ≥ 30℃：橙色
- 温度 10~30℃：绿色（舒适）
- 温度 0~10℃：蓝色
- 温度 < 0℃：青色加粗（严寒）
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box

console = Console()


def _temp_style(temp: float) -> str:
    """根据温度返回 rich 样式字符串"""
    if temp >= 35:
        return "bold red"
    elif temp >= 30:
        return "dark_orange"
    elif temp >= 10:
        return "green"
    elif temp >= 0:
        return "blue"
    else:
        return "bold cyan"


def _format_temp(temp: float) -> Text:
    """将温度值格式化为带颜色的 Text 对象"""
    style = _temp_style(temp)
    return Text(f"{temp}℃", style=style)


def render_current_weather(weather_list: list[dict]):
    """
    渲染所有城市的实时天气表格。
    weather_list: get_current_weather() 返回的字典列表。
    """
    # 创建主表格
    table = Table(
        title="🌍 实时天气概览",
        box=box.DOUBLE_EDGE,
        title_style="bold white on blue",
        header_style="bold magenta",
        show_lines=True,
        padding=(0, 1),
    )

    # 定义列
    table.add_column("城市", style="bold white", justify="center", min_width=8)
    table.add_column("天气", justify="center", min_width=10)
    table.add_column("温度", justify="center", min_width=8)
    table.add_column("湿度", justify="center", min_width=8)
    table.add_column("风速 m/s", justify="center", min_width=8)
    table.add_column("气压 hPa", justify="center", min_width=9)
    table.add_column("更新时间", style="dim", justify="center", min_width=19)

    for w in weather_list:
        temp_text = _format_temp(w["temperature"])
        # 湿度过高时用黄色警示
        humidity_style = "yellow" if w["humidity"] > 80 else "white"
        # 大风警示
        wind_style = "bold red" if w["wind_speed"] > 8 else "white"

        table.add_row(
            w["city"],
            w["condition"],
            temp_text,
            Text(f"{w['humidity']}%", style=humidity_style),
            Text(f"{w['wind_speed']}", style=wind_style),
            str(w["pressure"]),
            w["timestamp"],
        )

    console.print()
    console.print(table)
    console.print()


def render_forecast(city: str, forecasts: list[dict]):
    """
    渲染指定城市的 24 小时预报表格。
    使用紧凑布局显示逐小时天气变化。
    """
    table = Table(
        title=f"📅 {city} · 未来 24 小时预报",
        box=box.ROUNDED,
        title_style="bold white on dark_green",
        header_style="bold cyan",
        show_lines=False,
    )

    table.add_column("时间", style="dim", justify="center")
    table.add_column("天气", justify="center")
    table.add_column("温度", justify="center")
    table.add_column("湿度", justify="center")
    table.add_column("风速 m/s", justify="center")

    for f in forecasts:
        table.add_row(
            f["time"],
            f["condition"],
            _format_temp(f["temperature"]),
            f"{f['humidity']}%",
            str(f["wind_speed"]),
        )

    console.print(table)
    console.print()


def render_history(records: list[dict]):
    """渲染最近的历史查询记录"""
    if not records:
        console.print("[dim]暂无历史记录[/dim]")
        return

    table = Table(
        title="📜 最近查询历史",
        box=box.SIMPLE_HEAVY,
        title_style="bold white on dark_red",
        header_style="bold yellow",
    )

    table.add_column("城市", justify="center")
    table.add_column("时间", style="dim", justify="center")
    table.add_column("天气", justify="center")
    table.add_column("温度", justify="center")
    table.add_column("湿度", justify="center")

    for r in records:
        table.add_row(
            r["city"],
            r["timestamp"],
            r["condition"],
            _format_temp(r["temperature"]),
            f"{r['humidity']}%",
        )

    console.print(table)
    console.print()
