from office_recorder.batching import group_segments


def test_grouping_by_gap():
    segments = [
        {"start": 0.0, "end": 10.0, "text": "hello"},
        {"start": 20.0, "end": 30.0, "text": "world"},
        {"start": 400.0, "end": 410.0, "text": "new topic"},
    ]

    blocks = group_segments(segments, gap_seconds=300, max_words=200)
    assert len(blocks) == 2
    assert "hello world" in blocks[0].text
    assert "new topic" in blocks[1].text


def test_grouping_by_max_words():
    segments = [
        {"start": 0.0, "end": 2.0, "text": "one two three"},
        {"start": 3.0, "end": 4.0, "text": "four five six"},
    ]

    blocks = group_segments(segments, gap_seconds=300, max_words=3)
    assert len(blocks) == 2
