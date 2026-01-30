from office_recorder.storage import Storage


def test_storage_creates_day_dirs(tmp_path):
    storage = Storage(tmp_path)
    day = storage.get_day("2026-01-30")
    assert day.day_dir.exists()
    assert day.audio_dir.exists()
    assert day.transcripts_dir.exists()
    assert day.summaries_dir.exists()
