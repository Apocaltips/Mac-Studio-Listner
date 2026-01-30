from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .config import AppConfig


@dataclass
class DiarizationResult:
    segments: list[dict[str, Any]]
    meta: dict[str, Any]


class Diarizer:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._pipeline = None
        self._whisperx = None

    def _load_pipeline(self) -> None:
        if not self._config.diarization_enabled:
            return
        if self._pipeline is not None:
            return
        if self._config.diarization_backend != "whisperx":
            raise RuntimeError(f"Unsupported diarization backend: {self._config.diarization_backend}")
        try:
            import whisperx  # type: ignore
        except ImportError as exc:
            raise RuntimeError("whisperx is not installed") from exc

        self._whisperx = whisperx
        self._pipeline = whisperx.DiarizationPipeline(
            use_auth_token=self._config.diarization_hf_token,
            device=self._config.diarization_device,
        )

    def diarize(self, audio_path: str, segments: list[dict[str, Any]]) -> DiarizationResult:
        if not self._config.diarization_enabled:
            return DiarizationResult(segments=segments, meta={"enabled": False})

        self._load_pipeline()
        if self._pipeline is None or self._whisperx is None:
            return DiarizationResult(segments=segments, meta={"enabled": False})

        audio = self._whisperx.load_audio(audio_path)
        diarization = self._pipeline(audio)

        diarization_segments = _normalize_diarization(diarization)
        labeled = _assign_speakers(segments, diarization_segments)

        meta = {
            "enabled": True,
            "backend": self._config.diarization_backend,
            "segments": len(diarization_segments),
        }
        return DiarizationResult(segments=labeled, meta=meta)


def _normalize_diarization(diarization: Any) -> list[dict[str, Any]]:
    if diarization is None:
        return []
    if hasattr(diarization, "to_dict"):
        return diarization.to_dict("records")
    if isinstance(diarization, list):
        return diarization
    return []


def _assign_speakers(
    segments: list[dict[str, Any]],
    diarization_segments: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    labeled: list[dict[str, Any]] = []
    diarization_list = list(diarization_segments)

    for segment in segments:
        start = float(segment.get("start", 0.0))
        end = float(segment.get("end", start))
        best_speaker = "unknown"
        best_overlap = 0.0

        for diar in diarization_list:
            d_start = float(diar.get("start", 0.0))
            d_end = float(diar.get("end", d_start))
            overlap = max(0.0, min(end, d_end) - max(start, d_start))
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = diar.get("speaker", "unknown")

        labeled.append({**segment, "speaker": best_speaker})

    return labeled
