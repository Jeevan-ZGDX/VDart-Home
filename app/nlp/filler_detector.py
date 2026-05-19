"""Filler Word Detector Module for CMFH
Enhanced filler word detection
"""

import re
from typing import List, Dict, Any
from collections import Counter


class FillerDetector:
    """Detect and analyze filler words in speech"""

    FILLER_PATTERNS = [
        "um", "uh", "er", "ah", "um", "uhm",
        "basically", "actually", "literally", "honestly",
        "you know", "I mean", "sort of", "kind of",
        "I think", "I guess", "I believe", "maybe", "perhaps", "probably",
        "definitely", "obviously", "clearly", "certainly",
        "anyway", "whatever", "yeah", "okay", "right",
        "so", "well", "just", "really", "like", "kinda", "sorta",
        "gonna", "wanna", "gotta", "dunno", "idk",
        "you see", "as I said", "as I mentioned", "for real",
        "I don't know", "don't get me wrong", "if you know what I mean",
        "to be honest", "to be fair", "to tell you the truth",
        "i think", "i guess", "i mean"
    ]

    def __init__(self):
        pass

    def detect(self, text: str) -> Dict[str, Any]:
        """Detect filler words in text"""
        text_lower = text.lower()
        words = text.split()
        word_count = len(words)
        
        filler_found = []
        
        for filler in self.FILLER_PATTERNS:
            pattern = r'\b' + re.escape(filler) + r'\b'
            matches = re.findall(pattern, text_lower)
            filler_found.extend(matches)
        
        filler_count = len(filler_found)
        filler_ratio = (filler_count / word_count * 100) if word_count > 0 else 0
        
        filler_types = Counter(filler_found)
        
        conscious_fillers = 0
        if re.search(r'\bso\b(?=\s+[a-z])', text_lower):
            conscious_fillers += len(re.findall(r'\bso\b(?=\s+[a-z])', text_lower))
        if re.search(r'\bjust\b(?!\s+(saying|kidding|telling|knowing))', text_lower):
            conscious_fillers += len(re.findall(r'\bjust\b(?!\s+(saying|kidding|telling|knowing))', text_lower))
        if re.search(r'\bwell\b(?=\s+[a-z])', text_lower):
            conscious_fillers += len(re.findall(r'\bwell\b(?=\s+[a-z])', text_lower))
        if re.search(r'\blike\b(?=\s+(this|that|what|when|if|just))', text_lower):
            conscious_fillers += len(re.findall(r'\blike\b(?=\s+(this|that|what|when|if|just))', text_lower))
            
        effective_count = max(0, filler_count - conscious_fillers)
        effective_ratio = (effective_count / word_count * 100) if word_count > 0 else 0

        return {
            "filler_count": filler_count,
            "word_count": word_count,
            "filler_ratio": round(filler_ratio, 2),
            "effective_filler_count": effective_count,
            "effective_filler_ratio": round(effective_ratio, 2),
            "filler_types": dict(filler_types),
            "has_excessive_fillers": effective_ratio > 5.0,
            "severity": self._get_severity(effective_ratio),
            "top_fillers": filler_types.most_common(5)
        }

    def _get_severity(self, ratio: float) -> str:
        """Get severity level"""
        if ratio < 1:
            return "excellent"
        elif ratio < 3:
            return "good"
        elif ratio < 5:
            return "moderate"
        elif ratio < 10:
            return "high"
        else:
            return "needs_improvement"

    def get_filler_positions(self, text: str) -> List[Dict[str, Any]]:
        """Get positions of filler words"""
        positions = []
        text_lower = text.lower()
        
        for filler in self.FILLER_PATTERNS:
            pattern = r'\b' + re.escape(filler) + r'\b'
            for match in re.finditer(pattern, text_lower):
                context_start = max(0, match.start() - 20)
                context_end = min(len(text), match.end() + 20)
                positions.append({
                    "word": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "context": text[context_start:context_end]
                })
        
        return positions

    def suggest_replacements(self, filler_word: str) -> List[str]:
        """Suggest replacements"""
        replacements = {
            "um": ["pause", "take a breath"],
            "uh": ["pause", "take a breath"],
            "like": ["such as", "for example", "specifically"],
            "basically": ["essentially", "in summary", "fundamentally"],
            "actually": ["in fact", "indeed", "truly"],
            "literally": ["truly", "actually"],
            "honestly": ["frankly", "candidly"],
            "you know": ["as you know", "as we understand"],
            "I think": ["I believe", "in my opinion"],
            "I mean": ["I want to say", "the point is"],
            "kind of": ["somewhat", "to some extent"],
            "sort of": ["somewhat", "partially"],
            "maybe": ["perhaps", "possibly"],
            "probably": ["likely", "most likely"],
            "definitely": ["certainly", "absolutely"],
            "obviously": ["clearly", "naturally"],
            "just": [""],
            "so": [""],
            "well": [""],
            "really": ["particularly", "especially"],
            "kinda": ["somewhat", "rather"],
            "sorta": ["somewhat"],
            "gonna": ["going to"],
            "wanna": ["want to"],
            "gotta": ["need to"],
        }
        return replacements.get(filler_word.lower(), [])

    def analyze_filler_trends(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze trends across texts"""
        total_fillers = 0
        total_words = 0
        all_types = Counter()

        for text in texts:
            result = self.detect(text)
            total_fillers += result.get("effective_filler_count", 0)
            total_words += result.get("word_count", 0)
            all_types.update(result.get("filler_types", {}))

        overall_ratio = (total_fillers / total_words * 100) if total_words > 0 else 0

        return {
            "total_fillers": total_fillers,
            "total_words": total_words,
            "overall_ratio": round(overall_ratio, 2),
            "most_common_fillers": dict(all_types.most_common(5)),
            "trend": "improving" if overall_ratio < 3 else "needs_work"
        }

    def get_quick_tips(self) -> List[str]:
        """Get tips to reduce fillers"""
        return [
            "Pause instead of saying 'um' or 'uh'",
            "Use 'specifically' instead of 'like'",
            "Replace 'I think' with 'I believe'",
            "Replace 'basically' with 'essentially'",
            "Take a breath before speaking",
            "Practice under 2% filler words",
            "Record and count fillers",
            "Use silence - it's powerful"
        ]