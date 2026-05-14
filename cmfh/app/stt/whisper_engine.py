"""Whisper STT Engine for CMFH
Enhanced CPU-optimized speech-to-text
"""

import io
import numpy as np
from typing import Optional, Dict, Any, List
import wave
import struct


class WhisperEngine:
    """Lightweight Whisper-based speech-to-text engine"""

    def __init__(
        self,
        model_size: str = "tiny",
        language: str = "en",
        compute_type: str = "int8",
        model_cache_dir: Optional[str] = None
    ):
        self.model_size = model_size
        self.language = language
        self.compute_type = compute_type
        self.model_cache_dir = model_cache_dir
        self._model = None

    def _load_model(self):
        """Lazy load the model"""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type=self.compute_type,
                    download_root=self.model_cache_dir
                )
            except Exception as e:
                print(f"Failed to load Whisper model: {e}")
                raise

    def transcribe(
        self,
        audio_data: np.ndarray,
        beam_size: int = 5,
        vad_filter: bool = True
    ) -> Dict[str, Any]:
        """Transcribe audio data to text"""
        self._load_model()

        try:
            segments, info = self._model.transcribe(
                audio_data,
                language=self.language,
                beam_size=beam_size,
                vad_filter=vad_filter,
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            text = " ".join([seg.text for seg in segments])
            return {
                "text": text.strip(),
                "language": info.language if info else "en",
                "language_probability": info.language_probability if info else 1.0,
                "segments": [{"text": s.text, "start": s.start, "end": s.end} for s in segments],
                "success": True
            }
        except Exception as e:
            return {
                "text": "",
                "error": str(e),
                "success": False
            }

    def transcribe_wav_data(self, wav_bytes: bytes) -> Dict[str, Any]:
        """Transcribe WAV audio bytes"""
        try:
            with io.BytesIO(wav_bytes) as f:
                with wave.open(f, 'rb') as wav:
                    if wav.getnchannels() != 1:
                        return {"text": "", "error": "Only mono audio supported", "success": False}

                    sample_width = wav.getsampwidth()
                    frames = wav.readframes(wav.getnframes())

                    if sample_width == 2:
                        audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                    elif sample_width == 4:
                        audio_data = np.frombuffer(frames, dtype=np.float32)
                    else:
                        audio_data = np.frombuffer(frames, dtype=np.uint8).astype(np.float32) / 255.0

                    return self.transcribe(audio_data)
        except Exception as e:
            return {"text": "", "error": f"WAV processing error: {str(e)}", "success": False}

    def transcribe_mp3_data(self, mp3_bytes: bytes) -> Dict[str, Any]:
        """Transcribe MP3 audio bytes"""
        try:
            import subprocess
            import tempfile

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(mp3_bytes)
                tmp_path = tmp.name

            try:
                result = subprocess.run(
                    ['ffmpeg', '-i', tmp_path, '-ar', '16000', '-ac', '1', '-y', tmp_path + '.wav'],
                    capture_output=True,
                    timeout=60
                )

                if result.returncode == 0:
                    with wave.open(tmp_path + '.wav', 'rb') as wav:
                        frames = wav.readframes(wav.getnframes())
                        audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                    return self.transcribe(audio_data)
                else:
                    return {"text": "", "error": "MP3 conversion failed", "success": False}
            finally:
                import os
                os.unlink(tmp_path)
                if os.path.exists(tmp_path + '.wav'):
                    os.unlink(tmp_path + '.wav')

        except FileNotFoundError:
            return {"text": "", "error": "ffmpeg not installed. Install with: apt install ffmpeg", "success": False}
        except Exception as e:
            return {"text": "", "error": f"MP3 processing error: {str(e)}", "success": False}

    def transcribe_raw_audio(self, audio_bytes: bytes, file_type: str = "wav") -> Dict[str, Any]:
        """Transcribe raw audio bytes"""
        if file_type.lower() in ['mp3', 'm4a', 'ogg', 'flac']:
            return self.transcribe_mp3_data(audio_bytes)
        else:
            return self.transcribe_wav_data(audio_bytes)

    def transcribe_file(self, file_path: str) -> Dict[str, Any]:
        """Transcribe an audio file"""
        self._load_model()
        try:
            segments, info = self._model.transcribe(
                file_path,
                language=self.language,
                beam_size=5
            )
            text = " ".join([seg.text for seg in segments])
            return {
                "text": text.strip(),
                "language": info.language if info else "en",
                "segments": [{"text": s.text, "start": s.start, "end": s.end} for s in segments],
                "success": True
            }
        except Exception as e:
            return {"text": "", "error": str(e), "success": False}

    def transcribe_chunk(self, audio_chunk: np.ndarray) -> str:
        """Quick transcription for audio chunk"""
        result = self.transcribe(audio_chunk)
        return result["text"]

    def unload_model(self):
        """Unload model from memory"""
        if self._model is not None:
            del self._model
            self._model = None


class ChunkedTranscriber:
    """Process audio in chunks for real-time transcription"""

    def __init__(self, engine: WhisperEngine, chunk_duration: float = 15.0):
        self.engine = engine
        self.chunk_duration = chunk_duration
        self.buffer: List[np.ndarray] = []
        self.sample_rate = 16000

    def add_chunk(self, audio_chunk: np.ndarray):
        """Add audio chunk to buffer"""
        self.buffer.append(audio_chunk)

    def transcribe_buffer(self) -> Dict[str, Any]:
        """Transcribe all buffered audio"""
        if not self.buffer:
            return {"text": "", "segments": []}

        combined_audio = np.concatenate(self.buffer)
        result = self.engine.transcribe(combined_audio)
        self.buffer = []
        return result

    def get_buffer_duration(self) -> float:
        """Get total buffer duration in seconds"""
        if not self.buffer:
            return 0.0
        total_samples = sum(chunk.shape[0] for chunk in self.buffer)
        return total_samples / self.sample_rate

    def clear(self):
        """Clear the buffer"""
        self.buffer = []