"""配置读写。配置保存在 data/config.json，由网页端编辑。"""

from __future__ import annotations

import json
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_PATH = DATA_DIR / "config.json"

DEFAULT_CONFIG = {
    "schedule_time": "21:00",   # 每天发送时间 HH:MM（服务器时区 Asia/Shanghai）
    "jitter_minutes": 30,       # 时间抖动窗口：实际在 [schedule_time, schedule_time+30min] 内随机开始
    "send_gap_min": 6,          # 相邻两个好友之间的最小间隔（秒）
    "send_gap_max": 12,         # 相邻两个好友之间的最大间隔（秒）
    "max_friends_per_run": 20,  # 每次最多发送的好友数（0 表示不限制）
    "friends": [],              # 好友列表：聊天列表里显示的备注 / 昵称 / 抖音号
    "messages": ["🔥 续火花", "晚安，明天见", "今天也要开心哦"],
}

_lock = threading.Lock()


def load_config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            pass
    return cfg


def save_config(cfg: dict | None) -> dict:
    merged = dict(DEFAULT_CONFIG)
    if cfg:
        merged.update(cfg)

    merged["friends"] = [str(x).strip() for x in merged.get("friends", []) if str(x).strip()]
    merged["messages"] = [str(x) for x in merged.get("messages", []) if str(x).strip()]
    if not merged["messages"]:
        merged["messages"] = ["🔥"]

    schedule = str(merged.get("schedule_time", "21:00"))
    try:
        hh, mm = schedule.split(":")
        if not (0 <= int(hh) <= 23 and 0 <= int(mm) <= 59):
            raise ValueError
        merged["schedule_time"] = f"{int(hh):02d}:{int(mm):02d}"
    except Exception:
        raise ValueError("schedule_time 必须是 HH:MM 格式")

    for key in ("jitter_minutes", "send_gap_min", "send_gap_max", "max_friends_per_run"):
        try:
            merged[key] = max(0, int(merged.get(key, DEFAULT_CONFIG[key])))
        except (TypeError, ValueError):
            raise ValueError(f"{key} 必须是整数")
    if merged["send_gap_max"] < merged["send_gap_min"]:
        merged["send_gap_max"] = merged["send_gap_min"]

    with _lock:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    return merged
