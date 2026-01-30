from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional
import threading

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

from .config import AppConfig
from .recording import RecorderManager


@dataclass(frozen=True)
class ScheduleStatus:
    enabled: bool
    active: bool
    start: str
    end: str
    days: list[int]
    timezone: str | None


def _parse_time(value: str, fallback: time) -> time:
    try:
        parts = value.strip().split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        return time(hour=hour, minute=minute)
    except Exception:
        return fallback


def _get_timezone(name: str | None) -> Optional[ZoneInfo]:
    if not name or ZoneInfo is None:
        return None
    try:
        return ZoneInfo(name)
    except Exception:
        return None


def is_schedule_active(config: AppConfig, now: datetime | None = None) -> bool:
    if not config.schedule_enabled:
        return False

    tz = _get_timezone(config.schedule_timezone)
    now = now or datetime.now(tz=tz)
    current_day = now.weekday()

    start_t = _parse_time(config.schedule_start, time(9, 0))
    end_t = _parse_time(config.schedule_end, time(18, 0))
    current_time = now.time()

    if start_t <= end_t:
        return current_day in config.schedule_days and start_t <= current_time <= end_t

    # Cross-midnight schedule (e.g., 22:00 -> 06:00)
    if current_time >= start_t:
        return current_day in config.schedule_days
    previous_day = (current_day - 1) % 7
    return previous_day in config.schedule_days and current_time <= end_t


class ScheduleRunner:
    def __init__(self, config: AppConfig, recorder: RecorderManager) -> None:
        self._config = config
        self._recorder = recorder
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not self._config.schedule_enabled:
            return
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def status(self) -> ScheduleStatus:
        return ScheduleStatus(
            enabled=self._config.schedule_enabled,
            active=is_schedule_active(self._config),
            start=self._config.schedule_start,
            end=self._config.schedule_end,
            days=self._config.schedule_days,
            timezone=self._config.schedule_timezone,
        )

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            active = is_schedule_active(self._config)
            if active:
                self._recorder.start()
            elif self._config.schedule_auto_stop:
                self._recorder.stop()
            self._stop_event.wait(30)
