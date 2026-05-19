"""Audio Recorder Module for CMFH
Real-time microphone capture with chunk-based processing
"""

import asyncio
import queue
import threading
from typing import Optional, Callable, List
import numpy as np


class AudioRecorder:
    """Real-time audio recorder with chunk-based processing"""

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_duration: float = 10.0,
        channels: int = 1,
        dtype: str = "float32"
    ):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.channels = channels
        self.dtype = dtype
        self.chunk_size = int(sample_rate * chunk_duration)

        self._is_recording = False
        self._audio_queue: queue.Queue = queue.Queue()
        self._stream: Optional[Any] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        """Start recording audio"""
        try:
            import sounddevice as sd
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            )
            self._stream.start()
            self._is_recording = True
            return True
        except Exception as e:
            print(f"Error starting audio recorder: {e}")
            return False

    def stop(self) -> List[np.ndarray]:
        """Stop recording and return collected audio chunks"""
        self._is_recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        chunks = []
        while not self._audio_queue.empty():
            try:
                chunk = self._audio_queue.get_nowait()
                chunks.append(chunk)
            except queue.Empty:
                break
        return chunks

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if status:
            print(f"Audio callback status: {status}")
        if self._is_recording:
            self._audio_queue.put(indata.copy())

    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """Get next audio chunk from queue"""
        try:
            return self._audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    @property
    def is_recording(self) -> bool:
        return self._is_recording


class AsyncAudioRecorder:
    """Async wrapper for audio recording"""

    def __init__(self, sample_rate: int = 16000, chunk_duration: float = 10.0):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self._recorder = AudioRecorder(sample_rate, chunk_duration)
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start async recording"""
        self._recorder.start()
        self._task = asyncio.create_task(self._record_loop())

    async def _record_loop(self):
        """Internal recording loop"""
        while self._recorder.is_recording:
            chunk = self._recorder.get_audio_chunk(timeout=1.0)
            if chunk is not None:
                yield chunk
            await asyncio.sleep(0.1)

    async def stop(self) -> List[np.ndarray]:
        """Stop recording"""
        if self._task:
            self._task.cancel()
        return self._recorder.stop()