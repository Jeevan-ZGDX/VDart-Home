"""Scoring Engine Module for CMFH
Calculate overall speaking scores
"""

from typing import Dict, Any, List


class ScoringEngine:
    """Calculate comprehensive speaking scores"""

    WEIGHTS = {
        "grammar": 0.15,
        "filler": 0.20,
        "confidence": 0.25,
        "vocabulary": 0.20,
        "tedx": 0.20
    }

    def __init__(self):
        pass

    def calculate_overall_score(
        self,
        grammar_analysis: Dict[str, Any],
        filler_analysis: Dict[str, Any],
        confidence_analysis: Dict[str, Any],
        vocabulary_analysis: Dict[str, Any],
        tedx_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive speaking score"""
        grammar_score = self._score_grammar(grammar_analysis)
        filler_score = self._score_filler(filler_analysis)
        confidence_score = confidence_analysis.get("confidence_score", 50)
        vocabulary_score = vocabulary_analysis.get("vocabulary_score", 50)
        tedx_score = tedx_analysis.get("tedx_score", 30)

        overall = (
            grammar_score * self.WEIGHTS["grammar"] +
            filler_score * self.WEIGHTS["filler"] +
            confidence_score * self.WEIGHTS["confidence"] +
            vocabulary_score * self.WEIGHTS["vocabulary"] +
            tedx_score * self.WEIGHTS["tedx"]
        )

        return {
            "overall_score": round(overall, 1),
            "grammar_score": round(grammar_score, 1),
            "filler_score": round(filler_score, 1),
            "confidence_score": round(confidence_score, 1),
            "vocabulary_score": round(vocabulary_score, 1),
            "tedx_score": round(tedx_score, 1),
            "grade": self._get_grade(overall),
            "breakdown": self._get_breakdown(
                grammar_score, filler_score, confidence_score,
                vocabulary_score, tedx_score
            )
        }

    def _score_grammar(self, grammar: Dict[str, Any]) -> float:
        """Calculate grammar score"""
        if grammar.get("is_valid", True):
            return 100.0

        error_count = grammar.get("error_count", 0)
        return max(0.0, 100.0 - error_count * 10)

    def _score_filler(self, filler: Dict[str, Any]) -> float:
        """Calculate filler word score"""
        ratio = filler.get("filler_ratio", 0)
        return max(0.0, 100.0 - ratio * 10)

    def _get_grade(self, score: float) -> str:
        """Get letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _get_breakdown(
        self,
        grammar: float,
        filler: float,
        confidence: float,
        vocabulary: float,
        tedx: float
    ) -> Dict[str, str]:
        """Get score breakdown with labels"""
        return {
            "grammar": self._score_label(grammar),
            "filler": self._score_label(filler),
            "confidence": self._score_label(confidence),
            "vocabulary": self._score_label(vocabulary),
            "tedx_style": self._score_label(tedx)
        }

    def _score_label(self, score: float) -> str:
        """Get label for score"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        else:
            return "needs_work"

    def calculate_session_score(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate average score for session with multiple analyses"""
        if not analyses:
            return {"overall_score": 0, "session_length": 0}

        total = sum(a.get("overall_score", 0) for a in analyses)
        count = len(analyses)

        return {
            "overall_score": round(total / count, 1),
            "session_length": count,
            "average_grammar": sum(a.get("grammar", {}).get("error_count", 0) for a in analyses) / count,
            "average_filler_ratio": sum(a.get("filler", {}).get("filler_ratio", 0) for a in analyses) / count
        }

    def compare_scores(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare current and previous session scores"""
        overall_change = current.get("overall_score", 0) - previous.get("overall_score", 0)

        return {
            "overall_change": round(overall_change, 1),
            "improved": overall_change > 0,
            "declined": overall_change < 0,
            "stable": overall_change == 0,
            "highlights": self._get_improvement_highlights(current, previous)
        }

    def _get_improvement_highlights(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> List[str]:
        """Get areas of improvement"""
        highlights = []
        areas = ["grammar_score", "filler_score", "confidence_score", "vocabulary_score", "tedx_score"]

        for area in areas:
            curr = current.get(area, 0)
            prev = previous.get(area, 0)
            change = curr - prev

            if change > 10:
                area_name = area.replace("_score", "").replace("_", " ").title()
                highlights.append(f"Significant improvement in {area_name}")

        return highlights