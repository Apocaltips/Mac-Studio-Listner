from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import os
import platform
import signal
import subprocess
from pathlib import Path
from typing import Any

from .config import AppConfig
from .storage import Storage
from .utils import now_local, today_str, write_json, read_json


@dataclass
class RecorderState:
    pid: int
    started_at: str
    date: str
    audio_dir: str
    command: list[str]
    format: str


class RecorderManager:
    def __init__(self, config: AppConfig, storage: Storage) -> None:
        self._config = config
        self._storage = storage
        self._process: subprocess.Popen[str] | None = None

    def _pid_is_running(self, pid: int) -> bool:
        if pid <= 0:
            return False
        if platform.system().lower() == "windows":
            try:
                import psutil  # type: ignore

                return psutil.pid_exists(pid)
            except Exception:
                return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    def _load_state(self) -> RecorderState | None:
        path = self._storage.recorder_state_path()
        if not path.exists():
            return None
        try:
            payload = read_json(path)
            return RecorderState(**payload)
        except Exception:
            return None

    def _save_state(self, state: RecorderState) -> None:
        write_json(self._storage.recorder_state_path(), state.__dict__)

    def _clear_state(self) -> None:
        path = self._storage.recorder_state_path()
        if path.exists():
            path.unlink()

    def _build_ffmpeg_command(self, output_pattern: Path) -> list[str]:
        cfg = self._config
        cmd = [
            cfg.ffmpeg_bin,
            "-y",
            "-f",
            cfg.audio_backend,
            "-i",
            cfg.audio_input,
            "-ac",
            str(cfg.channels),
            "-ar",
            str(cfg.sample_rate),
        ]

        if cfg.audio_format.lower() == "flac":
            cmd += ["-c:a", "flac"]
        else:
            cmd += ["-c:a", "pcm_s16le"]

        cmd += [
            "-f",
            "segment",
            "-segment_time",
            str(cfg.segment_seconds),
            "-reset_timestamps",
            "1",
            str(output_pattern),
        ]
        return cmd

    def start(self, date_str: str | None = None) -> RecorderState:
        current = self._load_state()
        if current and self._pid_is_running(current.pid):
            return current

        date_str = date_str or today_str()
        day = self._storage.get_day(date_str)
        output_pattern = day.audio_dir / f"segment_%05d.{self._config.audio_format}"
        log_path = day.day_dir / "recording.log"
        log_file = log_path.open("a", encoding="utf-8")

        cmd = self._build_ffmpeg_command(output_pattern)
        process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=log_file,
            text=True,
        )
        self._process = process

        state = RecorderState(
            pid=process.pid,
            started_at=now_local().isoformat(),
            date=date_str,
            audio_dir=str(day.audio_dir),
            command=cmd,
            format=self._config.audio_format,
        )
        self._save_state(state)

        session_payload: dict[str, Any] = {
            "date": date_str,
            "started_at": state.started_at,
            "audio_backend": self._config.audio_backend,
            "audio_input": self._config.audio_input,
            "sample_rate": self._config.sample_rate,
            "channels": self._config.channels,
            "segment_seconds": self._config.segment_seconds,
            "format": self._config.audio_format,
        }
        write_json(self._storage.session_path(date_str), session_payload)
        return state

    def stop(self) -> dict[str, Any]:
        state = self._load_state()
        if not state:
            return {"stopped": False, "reason": "not_running"}

        stopped = False
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
                stopped = True
            except subprocess.TimeoutExpired:
                self._process.kill()
                stopped = True
        else:
            if self._pid_is_running(state.pid):
                try:
                    os.kill(state.pid, signal.SIGTERM)
                    stopped = True
                except Exception:
                    stopped = False

        self._clear_state()
        return {"stopped": stopped}

    def status(self) -> dict[str, Any]:
        state = self._load_state()
        if not state:
            return {"running": False}

        running = self._pid_is_running(state.pid)
        if not running:
            self._clear_state()
            return {"running": False}

        audio_dir = Path(state.audio_dir)
        file_count = len(list(audio_dir.glob("*"))) if audio_dir.exists() else 0
        return {
            "running": True,
            "pid": state.pid,
            "started_at": state.started_at,
            "date": state.date,
            "audio_dir": state.audio_dir,
            "format": state.format,
            "file_count": file_count,
            "command": state.command,
        }
