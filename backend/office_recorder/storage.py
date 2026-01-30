from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .utils import ensure_dir


@dataclass(frozen=True)
class DayPaths:
    day_dir: Path
    audio_dir: Path
    transcripts_dir: Path
    summaries_dir: Path


class Storage:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = ensure_dir(base_dir)

    def get_day(self, date_str: str) -> DayPaths:
        day_dir = ensure_dir(self.base_dir / date_str)
        audio_dir = ensure_dir(day_dir / "audio")
        transcripts_dir = ensure_dir(day_dir / "transcripts")
        summaries_dir = ensure_dir(day_dir / "summaries")
        return DayPaths(
            day_dir=day_dir,
            audio_dir=audio_dir,
            transcripts_dir=transcripts_dir,
            summaries_dir=summaries_dir,
        )

    def list_days(self) -> list[str]:
        if not self.base_dir.exists():
            return []
        return sorted([p.name for p in self.base_dir.iterdir() if p.is_dir()])

    def list_audio_files(self, date_str: str) -> list[Path]:
        day = self.get_day(date_str)
        return sorted([p for p in day.audio_dir.iterdir() if p.is_file()])

    def list_transcript_files(self, date_str: str) -> list[Path]:
        day = self.get_day(date_str)
        return sorted([p for p in day.transcripts_dir.iterdir() if p.is_file()])

    def summary_path(self, date_str: str) -> Path:
        return self.get_day(date_str).summaries_dir / "summary.json"

    def summary_markdown_path(self, date_str: str) -> Path:
        return self.get_day(date_str).summaries_dir / "summary.md"

    def session_path(self, date_str: str) -> Path:
        return self.get_day(date_str).day_dir / "session.json"

    def recorder_state_path(self) -> Path:
        return self.base_dir / "recorder_state.json"
