"""
天气历史记录数据库
==================
使用 SQLite3 存储每次查询的天气数据，支持按城市和时间查询历史。
"""

import sqlite3
import json
import os

# 数据库文件存放在项目根目录
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_history.db")


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接，启用 WAL 模式以提高并发性能"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row  # 使查询结果可以按列名访问
    return conn


def init_db():
    """
    初始化数据库：创建 history 表和时间戳索引。
    如果表已存在则跳过（IF NOT EXISTS）。
    """
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL,
            humidity INTEGER,
            wind_speed REAL,
            pressure INTEGER,
            condition TEXT
        )
    """)
    # 为时间戳建索引，加速 ORDER BY timestamp DESC 查询
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_timestamp
        ON history (timestamp DESC)
    """)
    conn.commit()
    conn.close()


def save_weather(data: dict):
    """
    将一条天气数据写入历史表。
    data 应包含: city, timestamp, temperature, humidity, wind_speed, pressure, condition
    """
    conn = _get_connection()
    conn.execute("""
        INSERT INTO history (city, timestamp, temperature, humidity, wind_speed, pressure, condition)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["city"],
        data["timestamp"],
        data["temperature"],
        data["humidity"],
        data["wind_speed"],
        data["pressure"],
        data["condition"],
    ))
    conn.commit()
    conn.close()


def get_latest_records(limit: int = 10) -> list[dict]:
    """
    获取最新的 N 条历史记录（按时间倒序）。
    返回字典列表，方便模板渲染。
    """
    conn = _get_connection()
    cursor = conn.execute("""
        SELECT city, timestamp, temperature, humidity, wind_speed, pressure, condition
        FROM history
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_city_history(city: str, limit: int = 24) -> list[dict]:
    """获取指定城市的最新 N 条历史记录"""
    conn = _get_connection()
    cursor = conn.execute("""
        SELECT city, timestamp, temperature, humidity, wind_speed, pressure, condition
        FROM history
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall() if row["city"] == city]
    conn.close()
    return rows
