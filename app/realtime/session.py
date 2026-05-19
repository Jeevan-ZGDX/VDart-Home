"""Per-connection real-time session state."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Optional

from ..core.registry import registry
from .transcript_merge import is_duplicate_chunk, merge_transcript

MetricsCallback = Callable[[Dict[str, Any]], Awaitable[None]]


@dataclass
class RealtimeSession:
    """State for one WebSocket coaching session."""

    transcript: str = ""
    started_at: float = field(default_factory=time.monotonic)
    last_pose_at: float = 0.0
    pose_interval: float = 0.5
    nlp_debounce: float = 1.5
    nlp_task: Optional[asyncio.Task] = None
    audio_seq: int = 0
    frame_seq: int = 0
    last_chunk_text: str = ""

    def append_transcript(self, chunk_text: str) -> tuple[str, str]:
        """
        Merge chunk into transcript without repeating prior words.

        Returns:
            (full_transcript, delta) — delta is new text only (empty if duplicate).
        """
        chunk = (chunk_text or "").strip()
        if not chunk:
            return self.transcript, ""

        if is_duplicate_chunk(self.last_chunk_text, chunk):
            return self.transcript, ""

        full, delta = merge_transcript(self.transcript, chunk)
        if not delta and full == self.transcript:
            return self.transcript, ""

        self.transcript = full
        self.last_chunk_text = chunk
        return self.transcript, delta

    def should_process_pose(self) -> bool:
        now = time.monotonic()
        if now - self.last_pose_at < self.pose_interval:
            return False
        self.last_pose_at = now
        return True

    def duration_seconds(self) -> float:
        return time.monotonic() - self.started_at

    def schedule_nlp(self, on_metrics: MetricsCallback) -> None:
        if self.nlp_task and not self.nlp_task.done():
            self.nlp_task.cancel()
        self.nlp_task = asyncio.create_task(self._debounced_nlp(on_metrics))

    async def _debounced_nlp(self, on_metrics: MetricsCallback) -> None:
        try:
            await asyncio.sleep(self.nlp_debounce)
            text = self.transcript
            if len(text.strip()) < 3:
                return
            analysis = await asyncio.to_thread(registry.nlp.get_quick_analysis, text)
            await on_metrics(analysis)
        except asyncio.CancelledError:
            pass

    def cancel_tasks(self) -> None:
        if self.nlp_task and not self.nlp_task.done():
            self.nlp_task.cancel()
