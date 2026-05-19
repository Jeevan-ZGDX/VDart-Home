"""Vocabulary Analyzer Module for CMFH
Analyze vocabulary quality and complexity (no external NLP dependencies)
"""

import re
from typing import Dict, Any, List
from collections import Counter


class VocabularyAnalyzer:
    """Analyze vocabulary quality and richness - pure implementation"""

    ACADEMIC_WORDS = {
        "analyze", "evaluate", "demonstrate", "illustrate", "emphasize",
        "significance", "implications", "perspective", "comprehensive",
        "substantial", "considerable", "phenomenon", "framework",
        "methodology", "assessment", "investment", "implementation",
        "coordination", "maximize", "optimize", "investigate", "explore",
        "identify", "determine", "establish", "interpret", "conclude",
        "acquire", "advocate", "construct", "consult", "contribute"
    }

    ACTION_VERBS = {
        "accelerate", "achieve", "advance", "build", "create", "design",
        "develop", "drive", "enhance", "establish", "execute", "facilitate",
        "formulate", "generate", "implement", "improve", "increase",
        "innovate", "launch", "lead", "manage", "optimize", "organize",
        "pioneer", "plan", "prioritize", "produce", "promote", "propose",
        "revolutionize", "spearhead", "strengthen", "streamline", "transform",
        "create", "build", "establish", "launch", "pioneer", "spearhead"
    }

    WEAK_WORDS = {
        "good", "bad", "nice", "big", "small", "thing", "stuff",
        "awesome", "cool", "pretty", "quite", "very", "really",
        "okay", "fine", "great", "terrible", "amazing", "interesting"
    }

    ADJECTIVE_SUFFIXES = ['ful', 'less', 'ous', 'ive', 'able', 'ible', 'al', 'ial', 'ic', 'ent', 'ant']
    ADVERB_SUFFIXES = ['ly']

    def __init__(self):
        pass

    def analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary quality using pattern matching"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        word_count = len(words)
        unique_words = len(set(words))

        lexical_diversity = unique_words / word_count if word_count > 0 else 0

        academic_count = sum(1 for w in words if w in self.ACADEMIC_WORDS)
        action_verb_count = sum(1 for w in words if w in self.ACTION_VERBS)
        weak_word_count = sum(1 for w in words if w in self.WEAK_WORDS)

        adjectives = [w for w in words if any(w.endswith(s) for s in self.ADJECTIVE_SUFFIXES)]
        adverbs = [w for w in words if any(w.endswith(s) for s in self.ADVERB_SUFFIXES)]
        verbs = [w for w in words if self._is_verb(w)]

        avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0

        vocabulary_score = self._calculate_vocabulary_score(
            lexical_diversity, academic_count, action_verb_count,
            weak_word_count, avg_word_length, word_count
        )

        word_freq = Counter(words)

        return {
            "word_count": word_count,
            "unique_words": unique_words,
            "lexical_diversity": round(lexical_diversity * 100, 2),
            "academic_words": academic_count,
            "action_verbs": action_verb_count,
            "weak_words": weak_word_count,
            "adjectives": len(adjectives),
            "adverbs": len(adverbs),
            "verbs": len(verbs),
            "avg_word_length": round(avg_word_length, 2),
            "vocabulary_score": vocabulary_score,
            "quality": self._get_quality(vocabulary_score),
            "top_words": dict(word_freq.most_common(10))
        }

    def _is_verb(self, word: str) -> bool:
        """Check if word is likely a verb"""
        verb_endings = ['ate', 'ify', 'ize', 'ise', 'en', 'ed', 'ing']
        return any(word.endswith(e) for e in verb_endings)

    def _calculate_vocabulary_score(
        self,
        diversity: float,
        academic: int,
        action: int,
        weak: int,
        avg_length: float,
        total: int
    ) -> float:
        """Calculate vocabulary quality score (0-100)"""
        score = 40.0

        score += min(diversity * 30, 30)

        if total > 0:
            score += min(academic / total * 200, 15)
            score += min(action / total * 150, 15)

        score -= min(weak * 2, 20)

        score += min((avg_length - 4) * 5, 10)

        return max(0.0, min(100.0, score))

    def _get_quality(self, score: float) -> str:
        """Get vocabulary quality assessment"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "average"
        else:
            return "limited"

    def suggest_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest vocabulary improvements"""
        suggestions = []

        if analysis["weak_words"] > 0:
            suggestions.append("Replace weak words (good, bad, nice) with stronger alternatives")
        if analysis["lexical_diversity"] < 50:
            suggestions.append("Use more varied vocabulary")
        if analysis["academic_words"] < 2:
            suggestions.append("Incorporate more professional/academic words")
        if analysis["action_verbs"] < 2:
            suggestions.append("Use more action verbs (lead, create, design, develop)")

        if not suggestions:
            suggestions.append("Excellent vocabulary usage!")

        return suggestions

    def get_word_list(self, text: str) -> Dict[str, List[str]]:
        """Get categorized word lists"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        words_dict = {
            "nouns": [],
            "verbs": [],
            "adjectives": [],
            "adverbs": []
        }

        for word in words:
            if any(word.endswith(s) for s in self.ADJECTIVE_SUFFIXES):
                words_dict["adjectives"].append(word)
            elif any(word.endswith(s) for s in self.ADVERB_SUFFIXES):
                words_dict["adverbs"].append(word)
            elif self._is_verb(word):
                words_dict["verbs"].append(word)
            else:
                words_dict["nouns"].append(word)

        return {k: list(set(v)) for k, v in words_dict.items()}