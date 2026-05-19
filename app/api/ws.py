"""WebSocket routes for real-time CMFH sessions."""

import asyncio
import base64
import json
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core.registry import registry
from ..realtime.audio import transcribe_chunk_async
from ..realtime.pipeline import run_final_analysis_async, save_session_result
from ..realtime.session import RealtimeSession

router = APIRouter()


async def _send(ws: WebSocket, payload: Dict[str, Any]) -> None:
    await ws.send_json(payload)


@router.websocket("/ws/session")
async def session_websocket(websocket: WebSocket):
    await websocket.accept()
    session = RealtimeSession()
    ending = False

    async def emit_metrics(analysis: Dict[str, Any]) -> None:
        await _send(
            websocket,
            {
                "type": "metrics",
                "filler": analysis.get("filler", {}),
                "confidence": analysis.get("confidence", {}),
                "vocabulary": analysis.get("vocabulary", {}),
                "quick_score": analysis.get("quick_score", 0),
            },
        )

    async def handle_end_session() -> None:
        nonlocal ending
        if ending:
            return
        ending = True
        session.cancel_tasks()
        text = session.transcript.strip()
        if len(text) < 3:
            await _send(
                websocket,
                {
                    "type": "final_report",
                    "error": "No speech captured",
                    "text": text,
                },
            )
            return

        try:
            report = await run_final_analysis_async(text)
            session_id = save_session_result(report, session.duration_seconds())
            await _send(
                websocket,
                {
                    "type": "final_report",
                    **report,
                    "session_id": session_id,
                },
            )
        except Exception as e:
            await _send(websocket, {"type": "error", "message": str(e)})

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await _send(websocket, {"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = msg.get("type")

            if msg_type == "ping":
                await _send(websocket, {"type": "pong"})
                continue

            if msg_type == "audio_chunk":
                data_b64 = msg.get("data", "")
                mime = msg.get("mime", "audio/webm")
                seq = msg.get("seq", session.audio_seq)
                session.audio_seq += 1

                if not data_b64:
                    await _send(websocket, {"type": "error", "message": "Missing audio data"})
                    continue

                try:
                    audio_bytes = base64.b64decode(data_b64)
                except Exception as e:
                    await _send(websocket, {"type": "error", "message": f"Decode failed: {e}"})
                    continue

                result = await transcribe_chunk_async(audio_bytes, mime)
                chunk_text = (result.get("text") or "").strip()

                if chunk_text:
                    full_text, delta = session.append_transcript(chunk_text)
                    if delta:
                        await _send(
                            websocket,
                            {
                                "type": "partial_transcript",
                                "text": delta,
                                "full_text": full_text,
                                "seq": seq,
                            },
                        )
                        session.schedule_nlp(emit_metrics)
                elif result.get("error"):
                    await _send(
                        websocket,
                        {"type": "error", "message": result.get("error"), "seq": seq},
                    )
                continue

            if msg_type == "video_frame":
                frame_data = msg.get("data", "")
                seq = msg.get("seq", session.frame_seq)
                session.frame_seq += 1

                if not frame_data or not session.should_process_pose():
                    continue

                try:
                    pose_result = await asyncio.to_thread(
                        registry.pose.analyze_frame, frame_data
                    )
                    await _send(websocket, {"type": "pose", **pose_result, "seq": seq})
                except Exception as e:
                    await _send(websocket, {"type": "error", "message": str(e)})
                continue

            if msg_type == "end_session":
                await handle_end_session()
                break

            await _send(websocket, {"type": "error", "message": f"Unknown type: {msg_type}"})

    except WebSocketDisconnect:
        pass
    finally:
        session.cancel_tasks()
