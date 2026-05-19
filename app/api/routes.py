"""FastAPI Routes for CMFH
Handle voice, text, and camera inputs
"""

import io
import base64
import numpy as np
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
# OpenCV removed - all vision processing now uses pure MediaPipe + PIL

from .models import (
    TranscribeResponse, AnalyzeResponse, RewriteResponse,
    FeedbackResponse, ScoreResponse, HistoryResponse, SessionResponse,
    HealthResponse, AnalyzeRequest, RewriteRequest, FeedbackRequest
)

from ..core.registry import registry
from ..realtime.audio import transcribe_chunk_sync
from ..realtime.pipeline import run_final_analysis, save_session_result


router = APIRouter()


@router.post("/transcribe")
async def transcribe(
    text: str = Form(None),
    audio_file: UploadFile = File(None),
    audio_data: str = Form(None)
):
    """Transcribe audio or text to text"""
    try:
        if text and not audio_file and not audio_data:
            return TranscribeResponse(text=text, success=True)

        if audio_file:
            content = await audio_file.read()
            file_ext = audio_file.filename.split('.')[-1].lower() if audio_file.filename else 'wav'

            try:
                result = registry.whisper.transcribe_raw_audio(content, file_ext)

                if result.get("success") and result.get("text"):
                    return TranscribeResponse(
                        text=result["text"],
                        language=result.get("language"),
                        segments=result.get("segments", []),
                        success=True
                    )
                else:
                    return TranscribeResponse(
                        text="",
                        success=False,
                        error=result.get("error", "Transcription failed")
                    )
            except Exception as e:
                return TranscribeResponse(text="", success=False, error=str(e))

        if audio_data:
            try:
                audio_bytes = base64.b64decode(audio_data)
                result = registry.whisper.transcribe_wav_data(audio_bytes)
                return TranscribeResponse(
                    text=result.get("text", ""),
                    language=result.get("language"),
                    segments=result.get("segments", []),
                    success=result.get("success", False),
                    error=result.get("error")
                )
            except Exception as e:
                return TranscribeResponse(text="", success=False, error=str(e))

        raise HTTPException(status_code=400, detail="No input provided")

    except Exception as e:
        return TranscribeResponse(text="", success=False, error=str(e))


@router.post("/transcribe/chunk")
async def transcribe_chunk(request: dict):
    """Transcribe a real-time speech chunk from the client."""
    try:
        audio_data = request.get("audio_data", "")
        file_type = request.get("file_type", "webm")

        if not audio_data:
            raise HTTPException(status_code=400, detail="Audio data is required")

        audio_bytes = base64.b64decode(audio_data)
        result = transcribe_chunk_sync(audio_bytes, file_type)

        return TranscribeResponse(
            text=result.get("text", ""),
            language=result.get("language"),
            segments=result.get("segments", []),
            success=result.get("success", False),
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """Analyze text for NLP metrics"""
    try:
        analysis = registry.nlp.analyze(request.text)

        return AnalyzeResponse(
            text=analysis["text"],
            grammar=analysis.get("grammar", {}),
            filler=analysis.get("filler", {}),
            confidence=analysis.get("confidence", {}),
            vocabulary=analysis.get("vocabulary", {}),
            structure=analysis.get("structure", {}),
            overall_score=analysis.get("overall_score", 0)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/complete")
async def complete_analysis(request: dict):
    """Complete analysis: NLP + TEDX + Rewrite"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        return run_final_analysis(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewrite")
async def rewrite(request: RewriteRequest):
    """Rewrite text in professional TEDX style"""
    try:
        result = registry.rewriter.rewrite(request.text, request.style)

        return RewriteResponse(
            original=result["original"],
            rewritten=result["rewritten"],
            style=result["style"],
            success=result.get("success", False),
            source=result.get("source", "unknown")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def feedback(request: FeedbackRequest):
    """Generate comprehensive feedback"""
    try:
        analysis = registry.nlp.analyze(request.text)
        tedx_analysis = registry.tedx.analyze(request.text)

        scores = registry.scoring.calculate_overall_score(
            analysis.get("grammar", {}),
            analysis.get("filler", {}),
            analysis.get("confidence", {}),
            analysis.get("vocabulary", {}),
            tedx_analysis
        )

        feedback = registry.feedback.generate_feedback(analysis, tedx_analysis, scores)

        return FeedbackResponse(**feedback)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/tedx")
async def analyze_tedx(request: dict):
    """Comprehensive TEDX style analysis"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        result = registry.tedx.analyze(text)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/tedx/compare")
async def compare_tedx(request: dict):
    """Compare speech to TEDX standards"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        result = registry.tedx.compare_to_tedx_standards(text)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/analyze/pose")
async def analyze_pose(file: UploadFile = File(...)):
    """Analyze pose from uploaded image/video"""
    try:
        content = await file.read()
        # Convert to base64 to use unified processing pipeline
        base64_frame = base64.b64encode(content).decode('utf-8')
        result = registry.pose.analyze_frame(base64_frame)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/analyze/frame")
async def analyze_frame(request: dict):
    """Analyze pose from base64 frame - pure MediaPipe implementation, no OpenCV"""
    try:
        frame_data = request.get("frame", "")
        if not frame_data:
            raise HTTPException(status_code=400, detail="Frame data required")

        # Send base64 directly to pose analyzer - it handles all decoding internally
        result = registry.pose.analyze_frame(frame_data)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=HistoryResponse)
async def get_history(limit: int = 10):
    """Get session history"""
    try:
        sessions = registry.db.get_recent_sessions(limit)
        stats = registry.db.get_statistics()

        session_responses = [
            SessionResponse(
                id=s["id"],
                created_at=s["created_at"],
                original_text=s.get("original_text", "")[:100],
                overall_score=s.get("overall_score", 0),
                grade=s.get("grade", "N/A"),
                duration_seconds=s.get("duration_seconds", 0)
            )
            for s in sessions
        ]

        return HistoryResponse(
            sessions=session_responses,
            total=stats["total_sessions"],
            statistics=stats
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        whisper_model=registry.whisper.model_size,
        ollama_available=registry.rewriter.is_available(),
        database="connected"
    )


@router.post("/save_session")
async def save_session(data: dict):
    """Save a session"""
    try:
        session_id = registry.db.save_session(
            original_text=data.get("original_text", ""),
            rewritten_text=data.get("rewritten_text", ""),
            scores=data.get("scores", {}),
            feedback=data.get("feedback", {}),
            analysis=data.get("analysis", {}),
            duration=data.get("duration", 0)
        )
        return {"session_id": session_id, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/{metric}")
async def get_progress(metric: str):
    """Get progress data for a metric"""
    try:
        data = registry.db.get_progress_data(metric)
        return {"metric": metric, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))