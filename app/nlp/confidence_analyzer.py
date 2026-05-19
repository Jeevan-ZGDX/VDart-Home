"""Confidence Analyzer Module for CMFH
Analyze speech confidence indicators
"""

import re
from typing import Dict, Any, List
from collections import Counter


class ConfidenceAnalyzer:
    """Analyze speech confidence indicators"""

    HEDGING_WORDS = [
        "maybe", "perhaps", "possibly", "probably", "might", "could",
        "I think", "I guess", "I believe", "I suppose", "seems like",
        "kind of", "sort of", "something like", "I don't know",
        "I'm not sure", "not really", "not sure", "not certain"
    ]

    HEDGING_PATTERNS = [
        r'\bmaybe\b', r'\bperhaps\b', r'\bpossibly\b', r'\bprobably\b',
        r'\bmight\b', r'\bcould\b', r'\bi think\b', r'\bi guess\b',
        r'\bi believe\b', r'\bi suppose\b', r'\bseems\b', r'\bkind of\b',
        r'\bsort of\b', r'\bi don\'t know\b', r'\bi\'m not sure\b'
    ]

    WEAK_VERBS = [
        "try", "hope", "wish", "want", "need", "seem", "appear",
        "feel", "look", "sound", "guess", "suppose", "assume"
    ]

    STRONG_VERBS = [
        "know", "believe", "understand", "recognize", "ensure",
        "guarantee", "confident", "certain", "definite", "positive"
    ]

    WEAK_PHRASES = [
        "not very good", "not bad", "kind of okay", "sort of",
        "a little bit", "maybe", "I hope", "fingers crossed",
        "not sure", "question mark", "not certain"
    ]

    def __init__(self):
        self._hedging_pattern = re.compile('|'.join(self.HEDGING_PATTERNS), re.IGNORECASE)

    def analyze_confidence(self, text: str) -> Dict[str, Any]:
        """Analyze confidence level in speech"""
        hedging_matches = self._hedging_pattern.findall(text)
        hedging_count = len(hedging_matches)

        word_count = len(text.split())
        hedging_ratio = (hedging_count / word_count * 100) if word_count > 0 else 0

        hedge_types = Counter([h.lower() for h in hedging_matches])

        words_lower = text.lower()
        weak_verb_count = sum(1 for v in self.WEAK_VERBS if v in words_lower)
        strong_verb_count = sum(1 for v in self.STRONG_VERBS if v in words_lower)

        weak_phrase_count = sum(1 for p in self.WEAK_PHRASES if p in words_lower)

        sentence_count = len(re.split(r'[.!?]+', text))
        questions = text.count('?')

        confidence_score = self._calculate_confidence_score(
            hedging_ratio, weak_verb_count, strong_verb_count,
            weak_phrase_count, sentence_count, questions
        )

        return {
            "confidence_score": confidence_score,
            "hedging_count": hedging_count,
            "hedging_ratio": round(hedging_ratio, 2),
            "hedging_types": dict(hedge_types),
            "weak_verbs": weak_verb_count,
            "strong_verbs": strong_verb_count,
            "weak_phrases": weak_phrase_count,
            "questions": questions,
            "sentence_count": sentence_count,
            "assessment": self._get_assessment(confidence_score)
        }

    def _calculate_confidence_score(
        self,
        hedge_ratio: float,
        weak_verbs: int,
        strong_verbs: int,
        weak_phrases: int,
        sentences: int,
        questions: int
    ) -> float:
        """Calculate overall confidence score (0-100)"""
        score = 100.0

        score -= min(hedge_ratio * 2, 40)
        score -= weak_verbs * 3
        score += strong_verbs * 5
        score -= weak_phrases * 2

        if sentences > 0:
            question_ratio = questions / sentences
            score -= question_ratio * 10

        return max(0.0, min(100.0, score))

    def _get_assessment(self, score: float) -> str:
        """Get confidence assessment"""
        if score >= 80:
            return "highly_confident"
        elif score >= 60:
            return "confident"
        elif score >= 40:
            return "neutral"
        elif score >= 20:
            return "hesitant"
        else:
            return "very_hesitant"

    def get_improvement_tips(self, analysis: Dict[str, Any]) -> List[str]:
        """Get tips to improve confidence"""
        tips = []

        if analysis["hedging_count"] > 0:
            tips.append("Avoid hedging words like 'maybe', 'I think', 'probably'")
        if analysis["weak_verbs"] > analysis["strong_verbs"]:
            tips.append("Use stronger, more confident verbs")
        if analysis["weak_phrases"] > 0:
            tips.append("Avoid weak phrases like 'not bad', 'kind of okay'")
        if analysis["questions"] > analysis["sentence_count"] * 0.3:
            tips.append("Reduce questioning tone - state assertions confidently")

        if not tips:
            tips.append("Great confidence level! Keep it up!")

        return tips