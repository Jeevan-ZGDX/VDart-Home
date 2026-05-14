"""Pydantic Models for CMFH API"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TranscribeRequest(BaseModel):
    audio_data: Optional[str] = None
    file_path: Optional[str] = None
    text: Optional[str] = None


class TranscribeResponse(BaseModel):
    text: str
    language: Optional[str] = None
    segments: List[Dict[str, Any]] = []
    success: bool = True


class AnalyzeRequest(BaseModel):
    text: str
    include_grammar: bool = True


class AnalyzeResponse(BaseModel):
    text: str
    grammar: Dict[str, Any]
    filler: Dict[str, Any]
    confidence: Dict[str, Any]
    vocabulary: Dict[str, Any]
    structure: Dict[str, Any]
    overall_score: float


class RewriteRequest(BaseModel):
    text: str
    style: str = "professional"


class RewriteResponse(BaseModel):
    original: str
    rewritten: str
    style: str
    success: bool
    source: str


class FeedbackRequest(BaseModel):
    text: str


class FeedbackResponse(BaseModel):
    summary: str
    strengths: List[str]
    areas_for_improvement: List[str]
    specific_tips: Dict[str, List[str]]
    action_items: List[str]
    encouragement: str


class ScoreResponse(BaseModel):
    overall_score: float
    grammar_score: float
    filler_score: float
    confidence_score: float
    vocabulary_score: float
    tedx_score: float
    grade: str
    breakdown: Dict[str, str]


class SessionResponse(BaseModel):
    id: int
    created_at: str
    original_text: str
    overall_score: float
    grade: str
    duration_seconds: float


class HistoryResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int
    statistics: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    whisper_model: str
    ollama_available: bool
    database: str