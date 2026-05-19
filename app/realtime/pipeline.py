"""Final session analysis pipeline (heavy path)."""

import asyncio
from typing import Any, Dict, Optional

from ..core.registry import registry


def run_final_analysis(text: str) -> Dict[str, Any]:
    """Full NLP + TEDX + scores + rewrite + feedback."""
    if not text or len(text.strip()) < 3:
        return {"error": "Text too short for analysis", "text": text or ""}

    nlp_analysis = registry.nlp.analyze(text)
    tedx_analysis = registry.tedx.analyze(text)

    scores = registry.scoring.calculate_overall_score(
        nlp_analysis.get("grammar", {}),
        nlp_analysis.get("filler", {}),
        nlp_analysis.get("confidence", {}),
        nlp_analysis.get("vocabulary", {}),
        tedx_analysis,
    )

    rewrite_result = registry.rewriter.rewrite(text, "tedx")
    feedback = registry.feedback.generate_feedback(nlp_analysis, tedx_analysis, scores)

    return {
        "text": text,
        "original": text,
        "rewritten": rewrite_result.get("rewritten", text),
        "scores": scores,
        "nlp_analysis": {
            "filler": nlp_analysis.get("filler", {}),
            "confidence": nlp_analysis.get("confidence", {}),
            "vocabulary": nlp_analysis.get("vocabulary", {}),
            "grammar": nlp_analysis.get("grammar", {}),
        },
        "tedx_analysis": {
            "score": tedx_analysis.get("tedx_score", 0),
            "grade": tedx_analysis.get("grade", "N/A"),
            "strengths": tedx_analysis.get("strengths", []),
            "improvements": tedx_analysis.get("improvements", []),
            "story_score": tedx_analysis.get("story_score", 0),
            "persuasion_score": tedx_analysis.get("persuasion_score", 0),
            "rhythm_score": tedx_analysis.get("rhythm_score", 0),
            "structure_score": tedx_analysis.get("structure_score", 0),
        },
        "feedback": feedback,
    }


async def run_final_analysis_async(text: str) -> Dict[str, Any]:
    return await asyncio.to_thread(run_final_analysis, text)


def save_session_result(
    report: Dict[str, Any],
    duration: float = 0,
) -> Optional[int]:
    """Persist session to SQLite; returns session id."""
    scores = report.get("scores", {})
    return registry.db.save_session(
        original_text=report.get("original", report.get("text", "")),
        rewritten_text=report.get("rewritten", ""),
        scores=scores,
        feedback=report.get("feedback", {}),
        analysis={
            "nlp": report.get("nlp_analysis", {}),
            "tedx": report.get("tedx_analysis", {}),
        },
        duration=duration,
    )
