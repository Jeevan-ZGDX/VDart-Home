"""Filler Word Detector Module for CMFH
Detect and analyze filler words in speech
"""

import re
from typing import List, Dict, Any, Tuple
from collections import Counter


class FillerDetector:
    """Detect and analyze filler words in speech"""

    FILLER_WORDS = {
        "um", "uh", "er", "ah", "like", "you know", "basically",
        "actually", "literally", "honestly", "so", "well", "right",
        "I mean", "sort of", "kind of", "yeah", "okay", "right",
        "anyway", "whatever", "I think", "I guess", "you see",
        "as I said", "as I mentioned", "believe me", "really",
        "just", "maybe", "perhaps", "probably", "definitely",
        "obviously", "clearly", "certainly", "sure", "obviously"
    }

    FILLER_PATTERNS = [
        r'\b(um|uh|er|ah)\b',
        r'\blike\b(?=\s+\w)',
        r'\byou know\b',
        r'\bbasically\b',
        r'\bactually\b',
        r'\bliterally\b',
        r'\bhonestly\b',
        r'\bI mean\b',
        r'\bsort of\b',
        r'\bkind of\b',
        r'\byeah\b(?=\s+[,.])',
        r'\banyway\b',
        r'\bi think\b',
        r'\bi guess\b',
    ]

    def __init__(self):
        self._pattern = self._compile_pattern()

    def _compile_pattern(self) -> re.Pattern:
        """Compile regex pattern for filler words"""
        return re.compile('|'.join(self.FILLER_PATTERNS), re.IGNORECASE)

    def detect(self, text: str) -> Dict[str, Any]:
        """Detect filler words in text"""
        matches = self._pattern.findall(text)
        filler_count = len(matches)

        word_count = len(text.split())
        filler_ratio = (filler_count / word_count * 100) if word_count > 0 else 0

        filler_types = Counter([m.lower() for m in matches])

        return {
            "filler_count": filler_count,
            "word_count": word_count,
            "filler_ratio": round(filler_ratio, 2),
            "filler_types": dict(filler_types),
            "has_excessive_fillers": filler_ratio > 5.0,
            "severity": self._get_severity(filler_ratio)
        }

    def _get_severity(self, ratio: float) -> str:
        """Get severity level based on filler ratio"""
        if ratio < 1:
            return "excellent"
        elif ratio < 3:
            return "good"
        elif ratio < 5:
            return "moderate"
        else:
            return "needs_improvement"

    def get_filler_positions(self, text: str) -> List[Dict[str, Any]]:
        """Get positions of filler words in text"""
        positions = []
        for match in self._pattern.finditer(text):
            positions.append({
                "word": match.group(),
                "start": match.start(),
                "end": match.end(),
                "context": text[max(0, match.start()-20):min(len(text), match.end()+20)]
            })
        return positions

    def suggest_replacements(self, filler_word: str) -> List[str]:
        """Suggest professional replacements for filler words"""
        replacements = {
            "um": ["pause briefly"],
            "uh": ["pause briefly"],
            "like": ["such as", "for example"],
            "basically": ["essentially", "in summary"],
            "actually": ["in fact", "indeed"],
            "you know": ["as you may know"],
            "I think": ["I believe", "in my opinion"],
            "kind of": ["somewhat", "to some extent"],
            "sort of": ["partially", "somewhat"],
            "literally": ["actually", "truly"],
            "honestly": ["frankly", "candidly"],
            "so": [""],
            "well": [""],
            "right": ["certainly", "indeed"],
            "anyway": ["moving on", "returning to"],
            "maybe": ["perhaps", "possibly"],
            "I guess": ["I believe", "it appears"]
        }
        return replacements.get(filler_word.lower(), [])

    def analyze_filler_trends(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze filler word trends across multiple texts"""
        total_fillers = 0
        total_words = 0
        all_types = Counter()

        for text in texts:
            result = self.detect(text)
            total_fillers += result["filler_count"]
            total_words += result["word_count"]
            all_types.update(result["filler_types"])

        overall_ratio = (total_fillers / total_words * 100) if total_words > 0 else 0

        return {
            "total_fillers": total_fillers,
            "total_words": total_words,
            "overall_ratio": round(overall_ratio, 2),
            "most_common_fillers": dict(all_types.most_common(5)),
            "trend": "improving" if overall_ratio < 3 else "needs_work"
        }