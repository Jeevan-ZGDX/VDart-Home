"""TEDX Reference Module for CMFH
TED Talk style analysis and suggestions
"""

import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path


class TEDXReference:
    """TEDX style reference and coaching system"""

    TEDX_PATTERNS = {
        "hook": [
            "what if", "imagine", "have you ever", "what would happen",
            "let me tell you", "I want to share", "the question is",
            "believe it or not", "here's the surprising"
        ],
        "story": [
            "once", "when I", "years ago", "I remember", "my first",
            "growing up", "in my experience", "I discovered", "that changed"
        ],
        "transition": [
            "but here's", "now here's", "the interesting part",
            "what I realized", "that taught me", "the key insight",
            "here's what happened", "the turning point"
        ],
        "call_to_action": [
            "what if you", "imagine what", "try this", "start with",
            "the next time", "consider", "think about", "ask yourself"
        ]
    }

    TEDX_VOCABULARY = {
        "power_words": [
            "transform", "revolutionize", "breakthrough", "inspire",
            "passion", "purpose", "impact", "change", "challenge",
            "opportunity", "discovery", "journey", "potential"
        ],
        "confidence_words": [
            "definitely", "certainly", "clearly", "absolutely",
            "unquestionably", "convinced", "confident", "assured"
        ],
        "simplicity_words": [
            "simple", "basic", "fundamental", "core", "essential",
            "straightforward", "clear", "obvious"
        ]
    }

    STRUCTURES = [
        {
            "name": "Problem-Solution",
            "description": "Present a problem, then offer solution",
            "template": "What if [problem]? The answer is [solution]."
        },
        {
            "name": "Story Arc",
            "description": "Tell a personal story with a lesson",
            "template": "I used to [past]. Then [change]. Now [present]."
        },
        {
            "name": "Three Points",
            "description": "Three key takeaways",
            "template": "First [point1]. Second [point2]. Finally [point3]."
        },
        {
            "name": "Hook-Insight-Action",
            "description": "Hook listener, give insight, call to action",
            "template": "What if [hook]? [Insight]. What if you [action]?"
        }
    ]

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else None
        self._knowledge_base = None

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analyze text for TEDX style elements"""
        text_lower = text.lower()

        hooks = sum(1 for h in self.TEDX_PATTERNS["hook"] if h in text_lower)
        stories = sum(1 for s in self.TEDX_PATTERNS["story"] if s in text_lower)
        transitions = sum(1 for t in self.TEDX_PATTERNS["transition"] if t in text_lower)
        ctas = sum(1 for c in self.TEDX_PATTERNS["call_to_action"] if c in text_lower)

        power_word_count = sum(1 for w in self.TEDX_VOCABULARY["power_words"] if w in text_lower)
        confidence_count = sum(1 for w in self.TEDX_VOCABULARY["confidence_words"] if w in text_lower)
        simplicity_count = sum(1 for w in self.TEDX_VOCABULARY["simplicity_words"] if w in text_lower)

        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)

        tedx_score = self._calculate_tedx_score(
            hooks, stories, transitions, ctas,
            power_word_count, confidence_count, simplicity_count,
            avg_sentence_length
        )

        return {
            "tedx_score": tedx_score,
            "hooks": hooks,
            "stories": stories,
            "transitions": transitions,
            "calls_to_action": ctas,
            "power_words": power_word_count,
            "confidence_words": confidence_count,
            "simplicity_words": simplicity_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "style_assessment": self._get_style_assessment(tedx_score),
            "suggestions": self._get_suggestions(
                hooks, stories, transitions, ctas,
                power_word_count, confidence_count, avg_sentence_length
            )
        }

    def _calculate_tedx_score(
        self,
        hooks: int, stories: int, transitions: int, ctas: int,
        power_words: int, confidence: int, simplicity: int,
        avg_length: float
    ) -> float:
        """Calculate TEDX style score (0-100)"""
        score = 20.0

        score += min(hooks * 5, 15)
        score += min(stories * 8, 20)
        score += min(transitions * 5, 15)
        score += min(ctas * 8, 20)

        score += min(power_words * 3, 12)
        score += min(confidence * 2, 8)
        score += min(simplicity * 2, 8)

        if 10 <= avg_length <= 20:
            score += 10
        elif avg_length > 25:
            score -= 10

        return max(0.0, min(100.0, score))

    def _get_style_assessment(self, score: float) -> str:
        """Get style assessment"""
        if score >= 80:
            return "excellent_tedx_style"
        elif score >= 60:
            return "good_tedx_style"
        elif score >= 40:
            return "developing_style"
        else:
            return "needs_improvement"

    def _get_suggestions(
        self,
        hooks: int, stories: int, transitions: int, ctas: int,
        power_words: int, confidence: int, avg_length: float
    ) -> List[str]:
        """Get improvement suggestions"""
        suggestions = []

        if hooks == 0:
            suggestions.append("Start with a hook - use 'what if', 'imagine', or a surprising fact")
        if stories == 0:
            suggestions.append("Add a personal story or example to make it relatable")
        if transitions == 0:
            suggestions.append("Use transition phrases like 'but here's what I realized'")
        if ctas == 0:
            suggestions.append("End with a call to action - 'what if you try this'")
        if power_words < 2:
            suggestions.append("Use power words: transform, inspire, breakthrough, passion")
        if confidence < 1:
            suggestions.append("Use confident language: definitely, certainly, clearly")
        if avg_length > 25:
            suggestions.append("Shorten your sentences - aim for 15-20 words average")

        if not suggestions:
            suggestions.append("Great TEDX style! Your speech has strong elements.")

        return suggestions

    def suggest_structure(self, topic: str) -> Dict[str, Any]:
        """Suggest TEDX structure for a topic"""
        return {
            "topic": topic,
            "recommended_structure": self.STRUCTURES[0],
            "all_structures": self.STRUCTURES,
            "tip": "Choose the structure that best fits your content and audience"
        }

    def get_tedx_tips(self) -> List[str]:
        """Get general TEDX speaking tips"""
        return [
            "Start with a hook - grab attention in the first 30 seconds",
            "Tell stories - personal stories make ideas memorable",
            "Use simple language - avoid jargon and complex terms",
            "Pause for effect - silence is powerful",
            "Make one point - don't overload with information",
            "End with action - tell audience what to do next",
            "Practice conversion - speak like you talk",
            "Show passion - your enthusiasm is contagious"
        ]

    def apply_tedx_improvements(self, text: str) -> Dict[str, Any]:
        """Apply TEDX style improvements to text"""
        analysis = self.analyze_style(text)

        improvements = []

        if analysis["hooks"] == 0:
            improvements.append("Consider starting with a compelling question or statement")

        if analysis["stories"] == 0:
            improvements.append("Add a brief personal story or example")

        if analysis["calls_to_action"] == 0:
            improvements.append("End with a clear call to action")

        if analysis["power_words"] < 2:
            improvements.append("Incorporate more impactful words like 'transform' or 'inspire'")

        return {
            "original": text,
            "analysis": analysis,
            "improvements": improvements,
            "tips": self.get_tedx_tips()
        }