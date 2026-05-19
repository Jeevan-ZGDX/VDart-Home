"""Audio Input Module for CMFH
Real-time microphone and file-based audio input
"""

import io
import base64
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
import numpy as np


class AudioInputHandler:
    """Handle audio input from microphone and files"""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self._is_recording = False

    async def process_audio_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Process uploaded audio file"""
        ext = Path(filename).suffix.lower()

        try:
            if ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
                return await self._decode_audio_file(file_data, ext)
            else:
                return {"error": f"Unsupported file format: {ext}", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def _decode_audio_file(self, file_data: bytes, ext: str) -> Dict[str, Any]:
        """Decode audio file to numpy array"""
        try:
            import wave
            with io.BytesIO(file_data) as f:
                with wave.open(f, 'rb') as wav:
                    if wav.getframerate() != self.sample_rate:
                        return {"error": "Sample rate mismatch, need 16kHz", "success": False}
                    frames = wav.readframes(wav.getnframes())
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                    audio_data = audio_data.astype(np.float32) / 32768.0
                    return {
                        "audio_data": audio_data.tobytes(),
                        "sample_rate": wav.getframerate(),
                        "channels": wav.getnchannels(),
                        "duration": len(audio_data) / wav.getframerate(),
                        "success": True
                    }
        except Exception as e:
            return {"error": f"Failed to decode audio: {str(e)}", "success": False}

    def get_audio_from_base64(self, audio_b64: str) -> Optional[np.ndarray]:
        """Convert base64 audio to numpy array"""
        try:
            audio_bytes = base64.b64decode(audio_b64)
            return np.frombuffer(audio_bytes, dtype=np.float32)
        except Exception:
            return None


class RealtimeRecorder:
    """Real-time audio recording (placeholder for sounddevice)"""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self._is_recording = False
        self._audio_chunks: List[np.ndarray] = []

    def start_recording(self) -> bool:
        """Start recording"""
        try:
            import sounddevice as sd
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                callback=self._audio_callback
            )
            self._stream.start()
            self._is_recording = True
            return True
        except Exception as e:
            print(f"Recording not available: {e}")
            self._is_recording = False
            return False

    def _audio_callback(self, indata, frames, time, status):
        """Audio callback"""
        if status:
            print(f"Audio status: {status}")
        if self._is_recording:
            self._audio_chunks.append(indata.copy())

    def stop_recording(self) -> Optional[np.ndarray]:
        """Stop recording and return audio"""
        self._is_recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()

        if self._audio_chunks:
            return np.concatenate(self._audio_chunks)
        return None

    @property
    def is_recording(self) -> bool:
        return self._is_recording


def process_audio_file_sync(file_data: bytes, filename: str) -> Dict[str, Any]:
    """Synchronous audio file processing"""
    handler = AudioInputHandler()
    return asyncio.get_event_loop().run_until_complete(
        handler.process_audio_file(file_data, filename)
    )