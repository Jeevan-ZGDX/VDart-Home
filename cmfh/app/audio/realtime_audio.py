"""Real-time Audio Recording Module for CMFH
JavaScript-integrated real-time microphone recording
"""

import json
import base64
import numpy as np
from typing import Optional, List, Callable
import io


class RealtimeAudioRecorder:
    """Handle real-time audio recording via JavaScript"""

    def __init__(self):
        self.sample_rate = 16000
        self.is_recording = False

    def get_audio_component_html(self) -> str:
        """Get HTML component for audio recording"""
        return """
        <script>
        let mediaRecorder = null;
        let audioChunks = [];
        let audioContext = null;
        let analyser = null;
        let stream = null;

        async function startRecording() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContext.createMediaStreamSource(stream);
                analyser = audioContext.createAnalyser();
                source.connect(analyser);

                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const arrayBuffer = await audioBlob.arrayBuffer();
                    const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
                    window.parent.postMessage({
                        type: 'audio_data',
                        data: base64Audio,
                        format: 'webm'
                    }, '*');
                    stream.getTracks().forEach(track => track.stop());
                };

                mediaRecorder.start();
                document.getElementById('recording-status').innerHTML = '🎤 Recording... (Click Stop to finish)';
                document.getElementById('start-btn').disabled = true;
                document.getElementById('stop-btn').disabled = false;
            } catch (err) {
                document.getElementById('recording-status').innerHTML = '❌ Error: ' + err.message;
            }
        }

        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                document.getElementById('recording-status').innerHTML = '✅ Recording saved!';
                document.getElementById('start-btn').disabled = false;
                document.getElementById('stop-btn').disabled = true;
            }
        }

        window.addEventListener('message', function(event) {
            if (event.data.type === 'process_audio') {
                startRecording();
            }
        });
        </script>

        <div style="padding: 15px; background: #f0f0f0; border-radius: 10px;">
            <h4>🎤 Real-time Microphone Recording</h4>
            <button id="start-btn" onclick="startRecording()" style="padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">🎤 Start Recording</button>
            <button id="stop-btn" onclick="stopRecording()" disabled style="padding: 10px 20px; background: #f44336; color: white; border: none; border-radius: 5px; cursor: pointer;">⏹️ Stop</button>
            <p id="recording-status" style="margin-top: 10px; font-weight: bold;">Click Start to begin recording</p>
            <p style="font-size: 12px; color: #666;">Note: Audio will be transcribed when you click Complete Analysis</p>
        </div>
        """

    def process_audio_data(self, audio_b64: str) -> Optional[np.ndarray]:
        """Process base64 audio data to numpy array"""
        try:
            audio_bytes = base64.b64decode(audio_b64)
            return np.frombuffer(audio_bytes, dtype=np.float32)
        except Exception as e:
            print(f"Error processing audio: {e}")
            return None


def create_audio_recording_ui() -> str:
    """Create the complete audio recording UI"""
    return """
    <style>
    .audio-recorder {
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
    }
    .record-btn {
        padding: 15px 30px;
        font-size: 18px;
        border: none;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .record-btn:hover {
        transform: scale(1.05);
    }
    .recording {
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255,0,0,0.7); }
        70% { box-shadow: 0 0 0 20px rgba(255,0,0,0); }
        100% { box-shadow: 0 0 0 0 rgba(255,0,0,0); }
    }
    </style>

    <div class="audio-recorder">
        <h3>🎤 Real-time Voice Recording</h3>
        <p>Click the button below to start recording your voice</p>

        <button id="recordButton" class="record-btn" onclick="toggleRecording()" style="background: #ff4757;">
            🎤 Click to Record
        </button>

        <div id="recordingStatus" style="margin-top: 15px; font-size: 16px;"></div>
        <div id="audioWave" style="height: 50px; background: rgba(255,255,255,0.1); margin-top: 10px; border-radius: 5px;"></div>
    </div>

    <script>
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];

    async function toggleRecording() {
        const btn = document.getElementById('recordButton');
        const status = document.getElementById('recordingStatus');

        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64 = reader.result.split(',')[1];
                        window.parent.postMessage({
                            type: 'streamlit_audio',
                            data: base64
                        }, '*');
                    };
                    reader.readAsDataURL(audioBlob);

                    stream.getTracks().forEach(track => track.stop());
                };

                mediaRecorder.start();
                isRecording = true;
                btn.innerHTML = '⏹️ Stop Recording';
                btn.style.background = '#2ed573';
                status.innerHTML = '🔴 Recording in progress... Speak now!';

            } catch (err) {
                status.innerHTML = '❌ Microphone access denied: ' + err.message;
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            btn.innerHTML = '🎤 Click to Record';
            btn.style.background = '#ff4757';
            status.innerHTML = '✅ Recording saved! Processing...';
        }
    }

    window.addEventListener('message', function(event) {
        if (event.data.type === 'set_audio_data') {
            console.log('Audio data received');
        }
    });
    </script>
    """