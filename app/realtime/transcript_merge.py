"""Merge streaming STT chunks without repeating prior words."""

import re
from difflib import SequenceMatcher


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _word_overlap_suffix_prefix(existing_words: list[str], new_words: list[str]) -> int:
    """Longest k where existing[-k:] == new[:k] (case-insensitive)."""
    max_k = min(len(existing_words), len(new_words), 24)
    for k in range(max_k, 0, -1):
        if [w.lower() for w in existing_words[-k:]] == [w.lower() for w in new_words[:k]]:
            return k
    return 0


def merge_transcript(existing: str, new_segment: str) -> tuple[str, str]:
    """
    Merge a new STT chunk into the running transcript.

    Returns:
        (full_transcript, delta) — delta is only the newly added text.
    """
    existing = _normalize(existing)
    new_segment = _normalize(new_segment)

    if not new_segment:
        return existing, ""

    if not existing:
        return new_segment, new_segment

    if existing.lower() == new_segment.lower():
        return existing, ""

    existing_lower = existing.lower()
    new_lower = new_segment.lower()

    # New chunk is a longer revision of the same utterance (common with overlapping audio).
    if new_lower.startswith(existing_lower):
        delta = new_segment[len(existing) :].strip()
        return new_segment, delta

    # New chunk fully contained in existing — duplicate / re-heard audio.
    if new_lower in existing_lower:
        return existing, ""

    # Existing fully contained in new — replace with expanded version.
    if existing_lower in new_lower:
        delta = new_segment[len(existing) :].strip() if new_segment.lower().startswith(existing_lower) else new_segment
        return new_segment, delta

    existing_words = existing.split()
    new_words = new_segment.split()
    overlap = _word_overlap_suffix_prefix(existing_words, new_words)

    if overlap > 0:
        merged_words = existing_words + new_words[overlap:]
        full = " ".join(merged_words)
        delta = " ".join(new_words[overlap:])
        return full, delta

    # Fuzzy: high similarity means Whisper re-sent nearly the same chunk.
    if SequenceMatcher(None, existing_lower, new_lower).ratio() > 0.92:
        return existing, ""

    # Genuinely new phrase after a pause.
    full = f"{existing} {new_segment}".strip()
    return full, new_segment


def is_duplicate_chunk(previous: str, new_segment: str, threshold: float = 0.9) -> bool:
    """Skip chunks that add no new information."""
    previous = _normalize(previous)
    new_segment = _normalize(new_segment)
    if not new_segment:
        return True
    if not previous:
        return False
    if previous.lower() == new_segment.lower():
        return True
    if new_segment.lower() in previous.lower():
        return True
    return SequenceMatcher(None, previous.lower(), new_segment.lower()).ratio() >= threshold
