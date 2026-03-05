"""
模拟天气数据引擎
================
通过正弦曲线 + 随机扰动生成逼真的天气数据，无需任何 API Key。

设计思路：
- 每个城市有一个基准温度（模拟纬度差异）
- 温度随小时呈正弦波动（白天高、夜晚低）
- 湿度与天气状况联动（雨天湿度更高）
- 风力在晴天较低、暴风雨时较高
"""

import math
import random
from datetime import datetime, timedelta

# 城市基准配置：(基准温度℃, 基准湿度%, 城市中文名)
CITY_PROFILES = {
    "北京": {"base_temp": 12, "base_humidity": 40, "lat_factor": 0.9},
    "上海": {"base_temp": 18, "base_humidity": 60, "lat_factor": 0.85},
    "广州": {"base_temp": 24, "base_humidity": 70, "lat_factor": 0.7},
    "哈尔滨": {"base_temp": 2, "base_humidity": 35, "lat_factor": 1.0},
    "成都": {"base_temp": 17, "base_humidity": 65, "lat_factor": 0.75},
    "拉萨": {"base_temp": 8, "base_humidity": 25, "lat_factor": 1.1},
}

# 天气状况及其对湿度和风力的影响系数
WEATHER_CONDITIONS = [
    {"desc": "☀️ 晴", "humidity_mod": -15, "wind_mod": -1, "weight": 30},
    {"desc": "⛅ 多云", "humidity_mod": 0, "wind_mod": 0, "weight": 25},
    {"desc": "🌥️ 阴", "humidity_mod": 10, "wind_mod": 1, "weight": 20},
    {"desc": "🌧️ 小雨", "humidity_mod": 25, "wind_mod": 2, "weight": 12},
    {"desc": "⛈️ 雷阵雨", "humidity_mod": 35, "wind_mod": 4, "weight": 6},
    {"desc": "🌨️ 小雪", "humidity_mod": 20, "wind_mod": 2, "weight": 4},
    {"desc": "🌫️ 雾", "humidity_mod": 30, "wind_mod": -2, "weight": 3},
]


def _pick_weather_condition():
    """按权重随机选取天气状况"""
    conditions = WEATHER_CONDITIONS
    weights = [c["weight"] for c in conditions]
    return random.choices(conditions, weights=weights, k=1)[0]


def _simulate_temperature(base_temp: float, hour: int, lat_factor: float) -> float:
    """
    用正弦曲线模拟昼夜温差：
    - 14:00 左右最高温，05:00 左右最低温
    - lat_factor 越大，昼夜温差越大（高纬度昼夜温差更明显）
    """
    # 正弦曲线：以14点为峰值，振幅为 8 * lat_factor
    amplitude = 8 * lat_factor
    phase_shift = 14  # 峰值在14点
    temp = base_temp + amplitude * math.sin(math.pi * (hour - phase_shift + 6) / 12)
    # 加入随机扰动 ±2℃
    temp += random.uniform(-2, 2)
    return round(temp, 1)


def _simulate_pressure() -> int:
    """模拟大气压，正常范围 995~1025 hPa"""
    return random.randint(995, 1025)


def get_current_weather(city: str) -> dict:
    """
    获取指定城市的「当前」模拟天气数据。
    返回字典包含：城市、时间戳、温度、湿度、风力、气压、天气描述。
    """
    if city not in CITY_PROFILES:
        raise ValueError(f"不支持的城市: {city}，可选: {list(CITY_PROFILES.keys())}")

    profile = CITY_PROFILES[city]
    now = datetime.now()
    hour = now.hour

    # 模拟各项指标
    condition = _pick_weather_condition()
    temp = _simulate_temperature(profile["base_temp"], hour, profile["lat_factor"])
    humidity = max(5, min(99, profile["base_humidity"] + condition["humidity_mod"] + random.randint(-5, 5)))
    wind_speed = max(0, round(random.uniform(1, 5) + condition["wind_mod"], 1))
    pressure = _simulate_pressure()

    # 低温时如果选到小雨，自动切换为小雪
    if temp < 2 and "雨" in condition["desc"]:
        condition = WEATHER_CONDITIONS[5]  # 小雪

    return {
        "city": city,
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": temp,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "pressure": pressure,
        "condition": condition["desc"],
    }


def get_forecast_24h(city: str) -> list[dict]:
    """
    生成未来 24 小时的逐小时预报数据。
    每小时一条记录，温度沿正弦曲线平滑变化。
    """
    if city not in CITY_PROFILES:
        raise ValueError(f"不支持的城市: {city}")

    profile = CITY_PROFILES[city]
    now = datetime.now()
    forecasts = []

    for i in range(1, 25):
        future_time = now + timedelta(hours=i)
        hour = future_time.hour
        condition = _pick_weather_condition()
        temp = _simulate_temperature(profile["base_temp"], hour, profile["lat_factor"])

        # 低温自动切换雨→雪
        if temp < 2 and "雨" in condition["desc"]:
            condition = WEATHER_CONDITIONS[5]

        humidity = max(5, min(99, profile["base_humidity"] + condition["humidity_mod"] + random.randint(-5, 5)))
        wind_speed = max(0, round(random.uniform(1, 5) + condition["wind_mod"], 1))

        forecasts.append({
            "time": future_time.strftime("%m-%d %H:00"),
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "condition": condition["desc"],
        })

    return forecasts
