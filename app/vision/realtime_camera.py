"""Realtime Camera Access Module for CMFH

Provides a reusable browser-based camera access helper for image capture and frame encoding.
"""

import base64
from typing import Optional


class RealtimeCamera:
    """Browser camera helper module."""

    def get_camera_component_html(self) -> str:
        """Return a browser-friendly camera capture UI snippet."""
        return """
        <script>
        let cmfhCameraStream = null;
        let cmfhCameraTimer = null;

        async function startCmfhCamera() {
            try {
                cmfhCameraStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
                const video = document.getElementById('cmfhCameraVideo');
                if (video) {
                    video.srcObject = cmfhCameraStream;
                    await video.play();
                }
            } catch (err) {
                console.error('Camera access failed:', err);
            }
        }

        function stopCmfhCamera() {
            if (cmfhCameraTimer) {
                clearInterval(cmfhCameraTimer);
                cmfhCameraTimer = null;
            }
            if (cmfhCameraStream) {
                cmfhCameraStream.getTracks().forEach((track) => track.stop());
                cmfhCameraStream = null;
            }
            const video = document.getElementById('cmfhCameraVideo');
            if (video) {
                video.srcObject = null;
            }
        }

        async function captureCmfhFrame() {
            const video = document.getElementById('cmfhCameraVideo');
            const canvas = document.getElementById('cmfhCameraCanvas');
            if (!video || !canvas) return;
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const dataUrl = canvas.toDataURL('image/jpeg', 0.7);
            const b64 = dataUrl.split(',')[1];
            window.parent.postMessage({ type: 'camera_frame', data: b64 }, '*');
        }
        </script>

        <div style="padding: 15px; background: #f8fafc; border-radius: 12px;">
            <h4>📷 Real-time Camera</h4>
            <video id="cmfhCameraVideo" width="640" height="480" autoplay muted playsinline style="border-radius: 12px; width: 100%; height: auto; background: #000"></video>
            <canvas id="cmfhCameraCanvas" style="display:none"></canvas>
            <div style="margin-top: 12px; display:flex; gap:10px; flex-wrap:wrap;">
                <button onclick="startCmfhCamera()" style="padding: 10px 16px; background:#22c55e; color:#fff; border:none; border-radius:8px; cursor:pointer;">Start Camera</button>
                <button onclick="stopCmfhCamera()" style="padding: 10px 16px; background:#ef4444; color:#fff; border:none; border-radius:8px; cursor:pointer;">Stop Camera</button>
                <button onclick="captureCmfhFrame()" style="padding: 10px 16px; background:#3b82f6; color:#fff; border:none; border-radius:8px; cursor:pointer;">Capture Frame</button>
            </div>
        </div>
        """

    def encode_frame(self, image_bytes: bytes) -> str:
        """Encode raw frame bytes to a base64 string."""
        return base64.b64encode(image_bytes).decode("utf-8")

    def decode_frame(self, base64_string: str) -> Optional[bytes]:
        """Decode a base64 frame string back into bytes."""
        try:
            return base64.b64decode(base64_string)
        except Exception:
            return None
