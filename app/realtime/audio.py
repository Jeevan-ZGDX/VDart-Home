"""Audio chunk decode and transcription helpers."""

import asyncio
from typing import Any, Dict

from ..core.registry import registry


def mime_to_file_type(mime: str) -> str:
    """Map browser MIME type to whisper file_type."""
    m = (mime or "").lower()
    if "webm" in m:
        return "webm"
    if "mp4" in m or "m4a" in m:
        return "mp4"
    if "ogg" in m:
        return "ogg"
    if "mp3" in m:
        return "mp3"
    if "wav" in m:
        return "wav"
    return m.split("/")[-1] if "/" in m else "webm"


def transcribe_chunk_sync(audio_bytes: bytes, mime: str) -> Dict[str, Any]:
    """Synchronous transcription for a single live audio chunk."""
    file_type = mime_to_file_type(mime)
    return registry.whisper.transcribe_raw_audio(audio_bytes, file_type, chunk_mode=True)


async def transcribe_chunk_async(audio_bytes: bytes, mime: str) -> Dict[str, Any]:
    """Run transcription off the event loop."""
    return await asyncio.to_thread(transcribe_chunk_sync, audio_bytes, mime)
