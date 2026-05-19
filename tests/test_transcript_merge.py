"""Tests for streaming transcript merge."""

from app.realtime.transcript_merge import merge_transcript


def test_extension_replaces_prefix():
    full, delta = merge_transcript("hi this is", "hi this is surya")
    assert full == "hi this is surya"
    assert delta == "surya"


def test_no_duplicate_append():
    full, delta = merge_transcript(
        "hi this is surya",
        "hi this is surya his my audio",
    )
    assert full == "hi this is surya his my audio"
    assert "hi this is surya hi this is" not in full


def test_word_overlap_boundary():
    full, _ = merge_transcript("my name is surya", "surya i'm from trichy")
    assert full == "my name is surya i'm from trichy"


def test_subset_ignored():
    full, delta = merge_transcript(
        "hi this is surya his my audio is audible",
        "hi this is surya",
    )
    assert full == "hi this is surya his my audio is audible"
    assert delta == ""
