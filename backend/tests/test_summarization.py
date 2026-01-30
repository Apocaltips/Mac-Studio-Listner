import json

from office_recorder.storage import Storage
from office_recorder.summarization import load_segments


def test_load_segments_applies_offsets(tmp_path):
    storage = Storage(tmp_path)
    day = storage.get_day("2026-01-30")

    transcript1 = day.transcripts_dir / "segment_00000.json"
    transcript2 = day.transcripts_dir / "segment_00001.json"

    transcript1.write_text(
        json.dumps({"segments": [{"start": 0, "end": 1, "text": "first"}]}),
        encoding="utf-8",
    )
    transcript2.write_text(
        json.dumps({"segments": [{"start": 0, "end": 1, "text": "second"}]}),
        encoding="utf-8",
    )

    segments = load_segments(storage, "2026-01-30", segment_seconds=300)
    assert len(segments) == 2
    assert segments[0]["text"] == "first"
    assert segments[1]["start"] == 300
    assert segments[1]["text"] == "second"
