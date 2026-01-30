from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import AppConfig
from .storage import Storage
from .diarization import Diarizer
from .utils import write_json


@dataclass
class TranscriptResult:
    audio_path: str
    language: str | None
    duration: float | None
    segments: list[dict[str, Any]]
    text: str


class Transcriber:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._model = None

    def _load_model(self) -> None:
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except ImportError as exc:
            raise RuntimeError("faster-whisper is not installed") from exc

        self._model = WhisperModel(
            self._config.transcribe_model,
            device=self._config.transcribe_device,
            compute_type=self._config.transcribe_compute,
        )

    def transcribe_file(self, audio_path: Path) -> TranscriptResult:
        self._load_model()
        assert self._model is not None

        segments_iter, info = self._model.transcribe(
            str(audio_path),
            vad_filter=self._config.vad_filter,
            language=self._config.language,
        )

        segments: list[dict[str, Any]] = []
        texts: list[str] = []
        for segment in segments_iter:
            text = segment.text.strip()
            segments.append(
                {
                    "start": float(segment.start),
                    "end": float(segment.end),
                    "text": text,
                }
            )
            texts.append(text)

        return TranscriptResult(
            audio_path=str(audio_path),
            language=getattr(info, "language", None),
            duration=getattr(info, "duration", None),
            segments=segments,
            text=" ".join(texts).strip(),
        )


def transcribe_day(
    storage: Storage,
    transcriber: Transcriber,
    date_str: str,
    diarizer: Diarizer | None = None,
) -> list[Path]:
    day = storage.get_day(date_str)
    audio_files = storage.list_audio_files(date_str)
    written: list[Path] = []

    for audio_file in audio_files:
        transcript_path = day.transcripts_dir / f"{audio_file.stem}.json"
        if transcript_path.exists():
            continue
        result = transcriber.transcribe_file(audio_file)
        diarization_meta: dict[str, Any] | None = None
        segments = result.segments
        if diarizer is not None:
            try:
                diarization = diarizer.diarize(str(audio_file), segments)
                segments = diarization.segments
                diarization_meta = diarization.meta
            except Exception as exc:
                diarization_meta = {
                    "enabled": True,
                    "status": "error",
                    "detail": str(exc),
                }
        payload = {
            "audio_path": result.audio_path,
            "language": result.language,
            "duration": result.duration,
            "segments": segments,
            "text": result.text,
        }
        if diarization_meta is not None:
            payload["diarization"] = diarization_meta
        write_json(transcript_path, payload)
        written.append(transcript_path)

    return written
