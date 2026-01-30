from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any
import requests

from .batching import group_segments
from .config import AppConfig
from .storage import Storage
from .utils import read_json, safe_json_load, write_json


@dataclass
class LLMClient:
    base_url: str
    api_key: str | None
    model: str
    timeout_seconds: float

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int | None = None) -> str:
        url = self.base_url.rstrip("/") + "/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout_seconds)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _offset_from_stem(stem: str, segment_seconds: int) -> int:
    match = re.search(r"(\d+)$", stem)
    if not match:
        return 0
    return int(match.group(1)) * segment_seconds


def load_segments(storage: Storage, date_str: str, segment_seconds: int) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    for transcript_path in storage.list_transcript_files(date_str):
        payload = read_json(transcript_path)
        offset = _offset_from_stem(transcript_path.stem, segment_seconds)
        for segment in payload.get("segments", []):
            segments.append(
                {
                    "start": float(segment.get("start", 0.0)) + offset,
                    "end": float(segment.get("end", 0.0)) + offset,
                    "text": segment.get("text", "").strip(),
                    "source": transcript_path.name,
                }
            )
    return sorted(segments, key=lambda s: s.get("start", 0.0))


def _block_prompt(block_text: str) -> list[dict[str, str]]:
    system = (
        "You summarize office conversations. Return STRICT JSON only. "
        "Schema: {summary, topics, decisions, action_items, questions, risks, follow_ups}. "
        "topics is a list of short strings. decisions/action_items/questions/risks/follow_ups are lists. "
        "Each action item: {item, owner, due}. Use empty string when unknown. "
        "Do not invent facts; if unsure, leave fields empty."
    )
    user = f"Conversation transcript:\n{block_text}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _daily_prompt(block_summaries: list[dict[str, Any]]) -> list[dict[str, str]]:
    system = (
        "You produce a daily rollup from conversation summaries. Return STRICT JSON only. "
        "Schema: {overview, top_topics, decisions, action_items, questions, risks, follow_ups}. "
        "top_topics is a list of short strings. decisions/action_items/questions/risks/follow_ups are lists. "
        "Each action item: {item, owner, due}. Avoid duplication. Do not invent facts."
    )
    user = "Block summaries JSON:\n" + str(block_summaries)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def format_markdown(summary: dict[str, Any]) -> str:
    daily = summary.get("daily_summary", {})
    lines = ["# Daily Summary", "", f"Date: {summary.get('date', '')}", ""]

    if daily.get("overview"):
        lines += ["## Overview", daily.get("overview", ""), ""]

    def section(title: str, items: list[Any]) -> None:
        if not items:
            return
        lines.append(f"## {title}")
        for item in items:
            if isinstance(item, dict):
                text = item.get("item") or item.get("text") or str(item)
                owner = item.get("owner")
                due = item.get("due")
                suffix = ""
                if owner:
                    suffix += f" (owner: {owner})"
                if due:
                    suffix += f" (due: {due})"
                lines.append(f"- {text}{suffix}")
            else:
                lines.append(f"- {item}")
        lines.append("")

    section("Top Topics", daily.get("top_topics", []))
    section("Decisions", daily.get("decisions", []))
    section("Action Items", daily.get("action_items", []))
    section("Questions", daily.get("questions", []))
    section("Risks", daily.get("risks", []))
    section("Follow Ups", daily.get("follow_ups", []))

    blocks = summary.get("blocks", [])
    if blocks:
        lines.append("## Conversation Blocks")
        for idx, block in enumerate(blocks, start=1):
            lines.append(f"### Block {idx}")
            lines.append(block.get("summary", ""))
            topics = block.get("topics", [])
            if topics:
                lines.append("Topics: " + ", ".join(topics))
            lines.append("")

    return "\n".join(lines).strip() + "\n"


class Summarizer:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._llm = LLMClient(
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
            model=config.llm_model,
            timeout_seconds=config.llm_timeout_seconds,
        )

    def summarize_day(self, storage: Storage, date_str: str) -> dict[str, Any]:
        segments = load_segments(storage, date_str, self._config.segment_seconds)
        if not segments:
            return {"date": date_str, "blocks": [], "daily_summary": {"overview": "No speech detected."}}

        blocks = group_segments(
            segments,
            gap_seconds=self._config.conversation_gap_seconds,
            max_words=self._config.conversation_max_words,
        )

        block_summaries: list[dict[str, Any]] = []
        for block in blocks:
            content = self._llm.chat(_block_prompt(block.text), temperature=0.2)
            parsed = safe_json_load(content)
            parsed["start"] = block.start
            parsed["end"] = block.end
            block_summaries.append(parsed)

        daily_content = self._llm.chat(_daily_prompt(block_summaries), temperature=0.2)
        daily_summary = safe_json_load(daily_content)

        summary = {
            "date": date_str,
            "blocks": block_summaries,
            "daily_summary": daily_summary,
        }
        return summary


def summarize_day(storage: Storage, summarizer: Summarizer, date_str: str) -> dict[str, Any]:
    summary = summarizer.summarize_day(storage, date_str)
    summary_path = storage.summary_path(date_str)
    markdown_path = storage.summary_markdown_path(date_str)
    write_json(summary_path, summary)
    markdown_path.write_text(format_markdown(summary), encoding="utf-8")
    return summary
