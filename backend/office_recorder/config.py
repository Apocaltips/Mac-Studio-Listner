from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import platform

from dotenv import load_dotenv

load_dotenv()

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_days(value: str) -> list[int]:
    if not value:
        return []
    mapping = {
        "mon": 0,
        "monday": 0,
        "tue": 1,
        "tues": 1,
        "tuesday": 1,
        "wed": 2,
        "wednesday": 2,
        "thu": 3,
        "thurs": 3,
        "thursday": 3,
        "fri": 4,
        "friday": 4,
        "sat": 5,
        "saturday": 5,
        "sun": 6,
        "sunday": 6,
    }
    days: list[int] = []
    for raw in value.split(","):
        token = raw.strip().lower()
        if not token:
            continue
        if token.isdigit():
            day = int(token)
            if 0 <= day <= 6:
                days.append(day)
            continue
        if token in mapping:
            days.append(mapping[token])
    return sorted(set(days))


@dataclass(frozen=True)
class AppConfig:
    data_dir: Path
    host: str
    port: int

    ffmpeg_bin: str
    audio_backend: str
    audio_input: str
    audio_format: str
    sample_rate: int
    channels: int
    segment_seconds: int

    transcribe_model: str
    transcribe_device: str
    transcribe_compute: str
    vad_filter: bool
    language: str | None

    conversation_gap_seconds: int
    conversation_max_words: int

    llm_base_url: str
    llm_api_key: str | None
    llm_model: str
    llm_timeout_seconds: float

    schedule_enabled: bool
    schedule_start: str
    schedule_end: str
    schedule_days: list[int]
    schedule_timezone: str | None
    schedule_auto_stop: bool

    diarization_enabled: bool
    diarization_backend: str
    diarization_device: str
    diarization_model: str
    diarization_hf_token: str | None

    openclaw_hook_url: str | None
    openclaw_hook_token: str | None
    openclaw_hook_to: str | None


def _default_audio_backend() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "avfoundation"
    if system == "windows":
        return "dshow"
    return "alsa"


def load_config() -> AppConfig:
    data_dir = Path(os.getenv("OFFICE_RECORDER_DATA_DIR", str(Path.home() / "OfficeRecorder")))
    host = os.getenv("OFFICE_RECORDER_HOST", "127.0.0.1")
    port = _env_int("OFFICE_RECORDER_PORT", 8787)

    ffmpeg_bin = os.getenv("OFFICE_RECORDER_FFMPEG_BIN", "ffmpeg")
    audio_backend = os.getenv("OFFICE_RECORDER_AUDIO_BACKEND", _default_audio_backend())
    audio_input = os.getenv("OFFICE_RECORDER_AUDIO_INPUT", ":0")
    audio_format = os.getenv("OFFICE_RECORDER_AUDIO_FORMAT", "wav")
    sample_rate = _env_int("OFFICE_RECORDER_SAMPLE_RATE", 16000)
    channels = _env_int("OFFICE_RECORDER_CHANNELS", 1)
    segment_seconds = _env_int("OFFICE_RECORDER_SEGMENT_SECONDS", 300)

    transcribe_model = os.getenv("OFFICE_RECORDER_TRANSCRIBE_MODEL", "small")
    transcribe_device = os.getenv("OFFICE_RECORDER_TRANSCRIBE_DEVICE", "auto")
    transcribe_compute = os.getenv("OFFICE_RECORDER_TRANSCRIBE_COMPUTE", "int8")
    vad_filter = _env_bool("OFFICE_RECORDER_VAD_FILTER", True)
    language = os.getenv("OFFICE_RECORDER_LANGUAGE")
    if language == "":
        language = None

    conversation_gap_seconds = _env_int("OFFICE_RECORDER_CONVERSATION_GAP", 420)
    conversation_max_words = _env_int("OFFICE_RECORDER_CONVERSATION_MAX_WORDS", 1200)

    llm_base_url = os.getenv("OFFICE_RECORDER_LLM_BASE_URL", "http://localhost:11434")
    llm_api_key = os.getenv("OFFICE_RECORDER_LLM_API_KEY")
    if llm_api_key == "":
        llm_api_key = None
    llm_model = os.getenv("OFFICE_RECORDER_LLM_MODEL", "llama3.1:70b")
    llm_timeout_seconds = _env_float("OFFICE_RECORDER_LLM_TIMEOUT", 120.0)

    schedule_enabled = _env_bool("OFFICE_RECORDER_SCHEDULE_ENABLED", False)
    schedule_start = os.getenv("OFFICE_RECORDER_SCHEDULE_START", "09:00")
    schedule_end = os.getenv("OFFICE_RECORDER_SCHEDULE_END", "18:00")
    schedule_days = _parse_days(os.getenv("OFFICE_RECORDER_SCHEDULE_DAYS", "mon,tue,wed,thu,fri"))
    schedule_timezone = os.getenv("OFFICE_RECORDER_SCHEDULE_TZ")
    if schedule_timezone in (None, "", "local"):
        schedule_timezone = None
    schedule_auto_stop = _env_bool("OFFICE_RECORDER_SCHEDULE_AUTO_STOP", True)

    diarization_enabled = _env_bool("OFFICE_RECORDER_DIARIZATION_ENABLED", False)
    diarization_backend = os.getenv("OFFICE_RECORDER_DIARIZATION_BACKEND", "whisperx")
    diarization_device = os.getenv("OFFICE_RECORDER_DIARIZATION_DEVICE", "auto")
    diarization_model = os.getenv("OFFICE_RECORDER_DIARIZATION_MODEL", "pyannote/speaker-diarization")
    diarization_hf_token = os.getenv("OFFICE_RECORDER_DIARIZATION_HF_TOKEN")
    if diarization_hf_token == "":
        diarization_hf_token = None

    openclaw_hook_url = os.getenv("OPENCLAW_HOOK_URL")
    if openclaw_hook_url == "":
        openclaw_hook_url = None
    openclaw_hook_token = os.getenv("OPENCLAW_HOOK_TOKEN")
    if openclaw_hook_token == "":
        openclaw_hook_token = None
    openclaw_hook_to = os.getenv("OPENCLAW_HOOK_TO")
    if openclaw_hook_to == "":
        openclaw_hook_to = None

    return AppConfig(
        data_dir=data_dir,
        host=host,
        port=port,
        ffmpeg_bin=ffmpeg_bin,
        audio_backend=audio_backend,
        audio_input=audio_input,
        audio_format=audio_format,
        sample_rate=sample_rate,
        channels=channels,
        segment_seconds=segment_seconds,
        transcribe_model=transcribe_model,
        transcribe_device=transcribe_device,
        transcribe_compute=transcribe_compute,
        vad_filter=vad_filter,
        language=language,
        conversation_gap_seconds=conversation_gap_seconds,
        conversation_max_words=conversation_max_words,
        llm_base_url=llm_base_url,
        llm_api_key=llm_api_key,
        llm_model=llm_model,
        llm_timeout_seconds=llm_timeout_seconds,
        schedule_enabled=schedule_enabled,
        schedule_start=schedule_start,
        schedule_end=schedule_end,
        schedule_days=schedule_days,
        schedule_timezone=schedule_timezone,
        schedule_auto_stop=schedule_auto_stop,
        diarization_enabled=diarization_enabled,
        diarization_backend=diarization_backend,
        diarization_device=diarization_device,
        diarization_model=diarization_model,
        diarization_hf_token=diarization_hf_token,
        openclaw_hook_url=openclaw_hook_url,
        openclaw_hook_token=openclaw_hook_token,
        openclaw_hook_to=openclaw_hook_to,
    )
