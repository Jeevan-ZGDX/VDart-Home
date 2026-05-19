"""TEDX Analyzer Module for CMFH
Comprehensive TEDX-style speech analysis and coaching
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass
class TEDXMetrics:
    """TEDX-specific metrics"""
    hook_score: float
    story_score: float
    structure_score: float
    persuasion_score: float
    vocabulary_impact: float
    rhythm_score: float
    emotional_appeal: float
    overall_tedx_score: float


class TEDXStoryAnalyzer:
    """Analyze storytelling patterns in speech"""

    STORY_PATTERNS = {
        "personal_narrative": [
            r"\bI (grew up|was born|remember|discovered|learned)\b",
            r"\bmy (first|childhood|young)\b",
            r"\bwhen I was\b",
            r"\bin my (twenties|thirties|life|experience)\b",
            r"\bit started when\b",
            r"\bthat changed my\b",
            r"\bI never forgot\b",
            r"\ba moment that\b"
        ],
        "challenge_struggle": [
            r"\bI struggled with\b",
            r"\bfaced (a|the) challenge\b",
            r"\bit was (hard|difficult|tough)\b",
            r"\bI almost (gave up|quit|failed)\b",
            r"\bthe hardest part\b",
            r"\bI couldn't\b",
            r"\bfelt (lost|stuck|trapped)\b"
        ],
        "transformation": [
            r"\bthen I (decided|chose|started)\b",
            r"\beverything changed\b",
            r"\bthat was the moment\b",
            r"\bsuddenly I\b",
            r"\bI realized\b",
            r"\bthat led to\b",
            r"\bfrom then on\b",
            r"\bmy life changed\b"
        ],
        "lesson_learned": [
            r"\bI learned that\b",
            r"\bthe lesson was\b",
            r"\bwhat I discovered\b",
            r"\bit taught me\b",
            r"\bthe takeaway\b",
            r"\bhere's what I know now\b",
            r"\bif I could tell\b"
        ],
        "call_to_action": [
            r"\bwhat if you\b",
            r"\bimagine (if|what)\b",
            r"\btry (this|in your)\b",
            r"\bstart (with|today)\b",
            r"\byou can (do|be|have)\b",
            r"\bI encourage you to\b",
            r"\bthe next time\b",
            r"\bconsider (this|whether)\b"
        ]
    }

    def analyze_story_elements(self, text: str) -> Dict[str, Any]:
        """Analyze story elements in speech"""
        text_lower = text.lower()

        story_scores = {}
        total_story_points = 0

        for pattern_type, patterns in self.STORY_PATTERNS.items():
            count = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    count += 1
            story_scores[pattern_type] = min(count * 20, 40)
            total_story_points += count

        story_score = sum(story_scores.values()) / len(story_scores) if story_scores else 0

        return {
            "story_score": round(story_score, 1),
            "story_elements": story_scores,
            "total_story_markers": total_story_points,
            "story_density": round(total_story_points / max(len(text.split()), 1) * 100, 2)
        }


class TEDXPersuasionAnalyzer:
    """Analyze persuasive techniques"""

    PERSUASION_TECHNIQUES = {
        "questions_rhetorical": [
            r"\bwhat if\b",
            r"\bhave you ever\b",
            r"\bwouldn't it be\b",
            r"\bdoesn't that mean\b",
            r"\bisn't it true that\b",
            r"\bwhat would happen if\b",
            r"\bhow many of you\b"
        ],
        "numbers_data": [
            r"\b\d+%?\b",
            r"\b(one|two|three|four|five|ten|hundred|thousand|million)\b",
            r"\bstatistics show\b",
            r"\bresearch shows\b",
            r"\bstudy found\b",
            r"\bdata suggests\b"
        ],
        "contrast_pairs": [
            r"\bbut\b.*\bnot\b",
            r"\b(less|more)\b than",
            r"\b(before|after)\b",
            r"\b(old|new)\b",
            r"\b(fail|success)\b",
            r"\b(negative|positive)\b"
        ],
        "authority_引用": [
            r"\bresearch shows\b",
            r"\bstudies have\b",
            r"\baccording to\b",
            r"\bexperts say\b",
            r"\bI read that\b",
            r"\bHarvard\b",
            r"\bStanford\b"
        ],
        "repetition": {
            "patterns": [
                r"\b(\w+)\b.*\b\1\b",
                r"\brepeat",
                r"\bagain and again\b",
                r"\bover and over\b"
            ],
            "check": True
        }
    }

    def analyze_persuasion(self, text: str) -> Dict[str, Any]:
        """Analyze persuasive techniques"""
        text_lower = text.lower()

        technique_scores = {}

        for technique, patterns in self.PERSUASION_TECHNIQUES.items():
            if isinstance(patterns, list):
                count = sum(1 for p in patterns if re.search(p, text_lower))
                technique_scores[technique] = min(count * 15, 40)
            elif isinstance(patterns, dict):
                if technique == "repetition":
                    count = 0
                    for p in patterns["patterns"]:
                        if re.search(p, text_lower, re.IGNORECASE):
                            count += 1
                    technique_scores[technique] = min(count * 20, 30)

        total_persuasion = sum(technique_scores.values()) / len(technique_scores) if technique_scores else 0

        return {
            "persuasion_score": round(total_persuasion, 1),
            "techniques": technique_scores,
            "technique_count": sum(1 for v in technique_scores.values() if v > 0)
        }


class TEDXRhythmAnalyzer:
    """Analyze speech rhythm and pacing"""

    def analyze_rhythm(self, text: str) -> Dict[str, Any]:
        """Analyze speech rhythm and pacing"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

        if not sentences:
            return {"rhythm_score": 50, "avg_sentence_length": 0, "rhythm_variation": 0}

        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)

        variance = sum((x - avg_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        std_dev = variance ** 0.5

        ideal_length = 15
        deviation = abs(avg_length - ideal_length)

        rhythm_score = max(0, 100 - deviation * 3 - std_dev * 0.5)

        short_sentences = sum(1 for l in sentence_lengths if l < 10)
        medium_sentences = sum(1 for l in sentence_lengths if 10 <= l <= 20)
        long_sentences = sum(1 for l in sentence_lengths if l > 20)

        return {
            "rhythm_score": round(rhythm_score, 1),
            "avg_sentence_length": round(avg_length, 1),
            "rhythm_variation": round(std_dev, 1),
            "sentence_distribution": {
                "short": short_sentences,
                "medium": medium_sentences,
                "long": long_sentences
            },
            "rhythm_assessment": self._get_rhythm_assessment(rhythm_score, std_dev)
        }

    def _get_rhythm_assessment(self, score: float, variation: float) -> str:
        """Get rhythm assessment"""
        if score >= 80 and variation > 5:
            return "excellent_varied"
        elif score >= 80:
            return "excellent_consistent"
        elif score >= 60:
            return "good"
        elif variation > 10:
            return "choppy"
        else:
            return "monotone"


class TEDXVocabularyAnalyzer:
    """Analyze TEDX-style vocabulary"""

    IMPACT_WORDS = {
        "verbs": [
            "transform", "revolutionize", "inspire", "empower", "accelerate",
            "discover", "unlock", "ignite", "reshape", "pioneer",
            "create", "build", "drive", "lead", "achieve"
        ],
        "nouns": [
            "breakthrough", "potential", "opportunity", "impact", "journey",
            "transformation", "innovation", "solution", "perspective", "vision"
        ],
        "adjectives": [
            "powerful", "remarkable", "extraordinary", "remarkable", "profound",
            "compelling", "remarkable", "game-changing", "life-changing"
        ]
    }

    SIMPLICITY_WORDS = [
        "simple", "basic", "easy", "clear", "straightforward",
        "fundamental", "core", "essential", "understand"
    ]

    EMOTIONAL_WORDS = [
        "passion", "fear", "love", "hope", "dream", "struggle",
        "joy", "pain", "amazing", "incredible", "heart", "soul"
    ]

    def analyze_vocabulary_impact(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary impact score"""
        words = text.lower().split()

        impact_count = 0
        simplicity_count = 0
        emotional_count = 0

        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.IMPACT_WORDS["verbs"] or clean_word in self.IMPACT_WORDS["nouns"]:
                impact_count += 1
            if clean_word in self.SIMPLICITY_WORDS:
                simplicity_count += 1
            if clean_word in self.EMOTIONAL_WORDS:
                emotional_count += 1

        word_count = len(words)
        if word_count == 0:
            return {"vocabulary_impact_score": 50}

        impact_ratio = impact_count / word_count * 100
        simplicity_ratio = simplicity_count / word_count * 100
        emotional_ratio = emotional_count / word_count * 100

        vocab_score = min(impact_ratio * 50, 40) + min(simplicity_ratio * 30, 30) + min(emotional_ratio * 30, 30)

        return {
            "vocabulary_impact_score": round(min(vocab_score, 100), 1),
            "impact_words": impact_count,
            "simplicity_words": simplicity_count,
            "emotional_words": emotional_count,
            "vocabulary_assessment": self._get_vocab_assessment(vocab_score)
        }

    def _get_vocab_assessment(self, score: float) -> str:
        """Get vocabulary assessment"""
        if score >= 70:
            return "powerful_impactful"
        elif score >= 50:
            return "balanced"
        elif score >= 30:
            return "basic"
        else:
            return "needs_improvement"


class TEDXEmotionalAnalyzer:
    """Analyze emotional appeal in speech"""

    EMOTIONAL_PATTERNS = {
        "vulnerability": [
            r"\bI was (scared|afraid|terrified|nervous)\b",
            r"\bI felt (ashamed|embarrassed|hopeless)\b",
            r"\bit was my biggest fear\b",
            r"\bI didn't know what to do\b",
            r"\bI was (lost|stuck)\b"
        ],
        "passion": [
            r"\bI (love|passionate|excited)\b",
            r"\bthis (matters|means everything)\b",
            r"\bI truly believe\b",
            r"\bfor me this is\b",
            r"\bit's my dream\b"
        ],
        "hope": [
            r"\bI hope\b",
            r"\byou can\b",
            r"\bthere's a way\b",
            r"\bwe can (make|create|build)\b",
            r"\bit's possible\b"
        ],
        "connection": [
            r"\byou (all|know|see|understand)\b",
            r"\blike (you|me|us)\b",
            r"\btogether\b",
            r"\bwe (all|can|will)\b"
        ]
    }

    def analyze_emotional_appeal(self, text: str) -> Dict[str, Any]:
        """Analyze emotional appeal"""
        text_lower = text.lower()

        emotional_scores = {}

        for emotion, patterns in self.EMOTIONAL_PATTERNS.items():
            count = sum(1 for p in patterns if re.search(p, text_lower))
            emotional_scores[emotion] = min(count * 25, 50)

        total_emotional = sum(emotional_scores.values()) / len(emotional_scores) if emotional_scores else 0

        return {
            "emotional_appeal_score": round(total_emotional, 1),
            "emotional_elements": emotional_scores,
            "emotional_balance": self._check_emotional_balance(emotional_scores)
        }

    def _check_emotional_balance(self, scores: Dict[str, int]) -> str:
        """Check emotional balance"""
        if not scores:
            return "neutral"

        non_zero = sum(1 for v in scores.values() if v > 0)
        if non_zero >= 3:
            return "well_balanced"
        elif non_zero >= 2:
            return "moderate"
        else:
            return "limited"


class TEDXStructureAnalyzer:
    """Analyze speech structure"""

    STRUCTURES = {
        "opening": [
            r"^(what if|imagine|have you ever|let me tell|I want to share)",
            r"^(the question is|believe it or not|here's the surprising)",
            r"^(I have a question|I want to ask)"
        ],
        "body_markers": [
            r"\bfirst(,|ly)?\b",
            r"\bsecond(,|ly)?\b",
            r"\bthird(,|ly)?\b",
            r"\bfirst of all\b",
            r"\bmoving on\b",
            r"\bnow\b.*\blet me\b",
            r"\bhere's the thing\b"
        ],
        "climax": [
            r"\band then\b",
            r"\bsuddenly\b",
            r"\bthat's when\b",
            r"\bthe turning point\b",
            r"\beverything changed\b",
            r"\bI realized\b"
        ],
        "closing": [
            r"\bin conclusion\b",
            r"\bso what\b",
            r"\bultimately\b",
            r"\bwhat I want you to (remember|take away)\b",
            r"\bthank you\b",
            r"\bthat's (it|all)\b"
        ]
    }

    def analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze speech structure"""
        structure_scores = {}

        for section, patterns in self.STRUCTURES.items():
            count = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    count += 1
            structure_scores[section] = min(count * 30, 40)

        has_opening = structure_scores.get("opening", 0) > 0
        has_body = bool(re.search(r"\b(first|second|third|next|also|furthermore)\b", text.lower()))
        has_closing = structure_scores.get("closing", 0) > 0

        structure_completeness = sum([has_opening, has_body, has_closing]) / 3 * 40
        total_structure = sum(structure_scores.values()) / len(structure_scores) + structure_completeness

        return {
            "structure_score": round(min(total_structure, 100), 1),
            "structure_elements": structure_scores,
            "has_opening": has_opening,
            "has_body": has_body,
            "has_closing": has_closing,
            "structure_assessment": self._get_structure_assessment(has_opening, has_body, has_closing)
        }

    def _get_structure_assessment(self, opening: bool, body: bool, closing: bool) -> str:
        """Get structure assessment"""
        if opening and body and closing:
            return "complete_structure"
        elif opening and closing:
            return "needs_body"
        elif body and closing:
            return "needs_opening"
        elif opening:
            return "needs_closing"
        else:
            return "fragmented"


class TEDXAnalyzer:
    """Comprehensive TEDX style analyzer"""

    def __init__(self, data_dir: Optional[str] = None):
        self.story_analyzer = TEDXStoryAnalyzer()
        self.persuasion_analyzer = TEDXPersuasionAnalyzer()
        self.rhythm_analyzer = TEDXRhythmAnalyzer()
        self.vocab_analyzer = TEDXVocabularyAnalyzer()
        self.emotional_analyzer = TEDXEmotionalAnalyzer()
        self.structure_analyzer = TEDXStructureAnalyzer()

        self.weights = {
            "hook": 0.15,
            "story": 0.15,
            "structure": 0.15,
            "persuasion": 0.15,
            "vocabulary": 0.15,
            "rhythm": 0.10,
            "emotional": 0.15
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Comprehensive TEDX analysis"""
        if not text or len(text.strip()) < 10:
            return {"error": "Text too short for TEDX analysis", "tedx_score": 0}

        story_analysis = self.story_analyzer.analyze_story_elements(text)
        persuasion_analysis = self.persuasion_analyzer.analyze_persuasion(text)
        rhythm_analysis = self.rhythm_analyzer.analyze_rhythm(text)
        vocab_analysis = self.vocab_analyzer.analyze_vocabulary_impact(text)
        emotional_analysis = self.emotional_analyzer.analyze_emotional_appeal(text)
        structure_analysis = self.structure_analyzer.analyze_structure(text)

        hook_score = min(story_analysis["total_story_markers"] * 10 + structure_analysis["structure_elements"].get("opening", 0), 100)

        overall_score = (
            hook_score * self.weights["hook"] +
            story_analysis["story_score"] * self.weights["story"] +
            structure_analysis["structure_score"] * self.weights["structure"] +
            persuasion_analysis["persuasion_score"] * self.weights["persuasion"] +
            vocab_analysis["vocabulary_impact_score"] * self.weights["vocabulary"] +
            rhythm_analysis["rhythm_score"] * self.weights["rhythm"] +
            emotional_analysis["emotional_appeal_score"] * self.weights["emotional"]
        )

        return {
            "tedx_score": round(overall_score, 1),
            "grade": self._get_grade(overall_score),
            "hook_score": round(hook_score, 1),
            "story_score": round(story_analysis["story_score"], 1),
            "structure_score": round(structure_analysis["structure_score"], 1),
            "persuasion_score": round(persuasion_analysis["persuasion_score"], 1),
            "vocabulary_impact_score": round(vocab_analysis["vocabulary_impact_score"], 1),
            "rhythm_score": round(rhythm_analysis["rhythm_score"], 1),
            "emotional_appeal_score": round(emotional_analysis["emotional_appeal_score"], 1),
            "story_analysis": story_analysis,
            "persuasion_analysis": persuasion_analysis,
            "rhythm_analysis": rhythm_analysis,
            "vocabulary_analysis": vocab_analysis,
            "emotional_analysis": emotional_analysis,
            "structure_analysis": structure_analysis,
            "assessment": self._get_assessment(overall_score),
            "strengths": self._identify_strengths(story_analysis, persuasion_analysis, structure_analysis, vocab_analysis, emotional_analysis),
            "improvements": self._identify_improvements(story_analysis, persuasion_analysis, structure_analysis, vocab_analysis, rhythm_analysis),
            "recommendations": self._get_recommendations(story_analysis, persuasion_analysis, structure_analysis, vocab_analysis)
        }

    def _get_grade(self, score: float) -> str:
        """Get letter grade"""
        if score >= 85:
            return "A (Excellent TEDX style)"
        elif score >= 75:
            return "B (Good TEDX style)"
        elif score >= 65:
            return "C (Developing)"
        elif score >= 50:
            return "D (Needs work)"
        else:
            return "F (Requires improvement)"

    def _get_assessment(self, score: float) -> str:
        """Get overall assessment"""
        if score >= 80:
            return "excellent_tedx_style"
        elif score >= 60:
            return "good_tedx_style"
        elif score >= 40:
            return "developing_style"
        else:
            return "needs_improvement"

    def _identify_strengths(self, story, persuasion, structure, vocab, emotional) -> List[str]:
        """Identify strengths"""
        strengths = []

        story_score = story.get("story_score", 0) if story else 0
        if story_score > 30:
            strengths.append("Strong storytelling elements with clear narrative arc")

        structure_elements = structure.get("structure_elements", {}) if structure else {}
        if structure_elements.get("opening", 0) > 20:
            strengths.append("Compelling opening hook")

        persuasion_score = persuasion.get("persuasion_score", 0) if persuasion else 0
        if persuasion_score > 30:
            strengths.append("Effective persuasive techniques")

        vocab_score = vocab.get("vocabulary_impact_score", 0) if vocab else 0
        if vocab_score > 40:
            strengths.append("Impactful vocabulary with power words")

        emotional_score = emotional.get("emotional_appeal_score", 0) if emotional else 0
        if emotional_score > 30:
            strengths.append("Good emotional connection with audience")

        if not strengths:
            strengths.append("Starting point - keep practicing TEDX techniques")

        return strengths

    def _identify_improvements(self, story, persuasion, structure, vocab, rhythm) -> List[str]:
        """Identify areas for improvement"""
        improvements = []

        story_score = story.get("story_score", 0) if story else 0
        if story_score < 20:
            improvements.append("Add more personal stories or examples")

        has_opening = structure.get("has_opening", False) if structure else False
        if not has_opening:
            improvements.append("Start with a hook or question")

        has_closing = structure.get("has_closing", False) if structure else False
        if not has_closing:
            improvements.append("End with a clear call to action")

        persuasion_score = persuasion.get("persuasion_score", 0) if persuasion else 0
        if persuasion_score < 20:
            improvements.append("Use more persuasive techniques (questions, data, contrast)")

        vocab_score = vocab.get("vocabulary_impact_score", 0) if vocab else 0
        if vocab_score < 30:
            improvements.append("Incorporate more impact words and emotional language")

        rhythm_score = rhythm.get("rhythm_score", 0) if rhythm else 0
        if rhythm_score < 50:
            improvements.append("Vary sentence length for better rhythm")

        return improvements

    def _get_recommendations(self, story, persuasion, structure, vocab) -> List[str]:
        """Get actionable recommendations"""
        recommendations = []

        if story["total_story_markers"] == 0:
            recommendations.append("Try this structure: 'What if... I used to... then I realized... now I want you to...'")
        if not structure.get("has_opening"):
            recommendations.append("Start your next speech with: 'Have you ever wondered...' or 'What if we could...'")
        if not structure.get("has_closing"):
            recommendations.append("End with: 'The next time you..., consider...' or 'What I want you to remember is...'")
        if vocab.get("impact_words", 0) < 2:
            recommendations.append("Add power verbs: transform, inspire, discover, create, drive")
        if persuasion.get("technique_count", 0) < 2:
            recommendations.append("Use rhetorical questions and contrast pairs")

        return recommendations

    def compare_to_tedx_standards(self, text: str) -> Dict[str, Any]:
        """Compare speech to TEDX standards"""
        analysis = self.analyze(text)

        tedx_standards = {
            "max_duration": "18 minutes",
            "avg_sentence_length": "15-20 words",
            "story_density": "at least one personal story",
            "hook_required": True,
            "cta_required": True
        }

        return {
            "your_analysis": analysis,
            "tedx_standards": tedx_standards,
            "how_you_compare": {
                "rhythm": "optimal" if 15 <= analysis.get("rhythm_analysis", {}).get("avg_sentence_length", 0) <= 20 else "needs_adjustment",
                "story": "meets_standard" if analysis.get("story_analysis", {}).get("total_story_markers", 0) > 0 else "needs_story",
                "structure": "complete" if analysis.get("structure_analysis", {}).get("has_opening") and analysis.get("structure_analysis", {}).get("has_closing") else "incomplete"
            }
        }

    def generate_tedx_tips(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific tips based on analysis"""
        tips = []

        if analysis.get("hook_score", 0) < 30:
            tips.extend([
                "Opening: Start with a provocative question ('What if...')",
                "Hook: Use 'Imagine...' or 'Have you ever...' to engage audience",
                "Story: Begin with a personal experience that relates to your topic"
            ])

        if analysis.get("story_score", 0) < 30:
            tips.extend([
                "Storytelling: Use the 'knock-knock' structure (setup, conflict, resolution)",
                "Include at least one personal story that illustrates your main point",
                "Use specific details and emotions to make it memorable"
            ])

        if analysis.get("structure_score", 0) < 40:
            tips.extend([
                "Structure: Follow 'Hook-Insight-Action' pattern",
                "Use transition phrases: 'But here's what I realized...'",
                "End with clear call to action: 'What if you try...'"
            ])

        if analysis.get("persuasion_score", 0) < 30:
            tips.extend([
                "Persuasion: Use data and statistics to support claims",
                "Include contrast pairs (before/after, problem/solution)",
                "Reference权威 sources to build credibility"
            ])

        if analysis.get("vocabulary_impact_score", 0) < 40:
            tips.extend([
                "Vocabulary: Replace weak words (good, bad, nice) with power words",
                "Use action verbs: transform, create, build, drive, inspire",
                "Include emotional words that connect with audience"
            ])

        return tips