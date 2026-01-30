from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConversationBlock:
    start: float
    end: float
    text: str
    segments: list[dict[str, Any]]


def _segment_text(segment: dict[str, Any]) -> str:
    text = segment.get("text", "")
    return " ".join(text.split())


def group_segments(
    segments: list[dict[str, Any]],
    gap_seconds: int,
    max_words: int,
) -> list[ConversationBlock]:
    blocks: list[ConversationBlock] = []
    current_segments: list[dict[str, Any]] = []
    current_words = 0

    def flush() -> None:
        nonlocal current_segments, current_words
        if not current_segments:
            return
        start = float(current_segments[0].get("start", 0.0))
        end = float(current_segments[-1].get("end", start))
        text = " ".join(_segment_text(seg) for seg in current_segments).strip()
        blocks.append(ConversationBlock(start=start, end=end, text=text, segments=current_segments))
        current_segments = []
        current_words = 0

    last_end: float | None = None
    for segment in segments:
        start = float(segment.get("start", 0.0))
        end = float(segment.get("end", start))
        text = _segment_text(segment)
        word_count = len(text.split())

        if last_end is not None:
            gap = start - last_end
            if gap >= gap_seconds:
                flush()

        if current_words + word_count > max_words and current_segments:
            flush()

        current_segments.append({**segment, "text": text})
        current_words += word_count
        last_end = end

    flush()
    return blocks
