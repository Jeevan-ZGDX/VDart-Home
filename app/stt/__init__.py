"""Speech-to-text module for CMFH"""
from .whisper_engine import WhisperEngine, ChunkedTranscriber

__all__ = ["WhisperEngine", "ChunkedTranscriber"]