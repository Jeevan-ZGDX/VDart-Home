"""NLP Analyzer Module for CMFH
Combined NLP analysis engine
"""

from typing import Dict, Any, List
from .grammar_checker import GrammarChecker
from .filler_detector import FillerDetector
from .confidence_analyzer import ConfidenceAnalyzer
from .vocabulary_analyzer import VocabularyAnalyzer


class NLPAnalyzer:
    """Combined NLP analysis engine"""

    def __init__(self):
        self.grammar_checker = GrammarChecker()
        self.filler_detector = FillerDetector()
        self.confidence_analyzer = ConfidenceAnalyzer()
        self.vocabulary_analyzer = VocabularyAnalyzer()

    def analyze(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive NLP analysis"""
        if not text or len(text.strip()) < 3:
            return {
                "error": "Text too short for analysis",
                "text": text
            }

        grammar = self.grammar_checker.check_grammar(text)
        filler = self.filler_detector.detect(text)
        confidence = self.confidence_analyzer.analyze_confidence(text)
        vocabulary = self.vocabulary_analyzer.analyze_vocabulary(text)

        structure = self.grammar_checker.analyze_sentence_structure(text)

        return {
            "text": text,
            "grammar": grammar,
            "filler": filler,
            "confidence": confidence,
            "vocabulary": vocabulary,
            "structure": structure,
            "overall_score": self._calculate_overall_score(
                grammar, filler, confidence, vocabulary
            )
        }

    def _calculate_overall_score(
        self,
        grammar: Dict,
        filler: Dict,
        confidence: Dict,
        vocabulary: Dict
    ) -> float:
        """Calculate overall speaking score (0-100)"""
        score = 100.0

        grammar_errors = grammar.get("error_count", 0)
        score -= min(grammar_errors * 5, 30)

        filler_ratio = filler.get("filler_ratio", 0)
        score -= min(filler_ratio * 3, 25)

        conf_score = confidence.get("confidence_score", 50)
        score = score * 0.3 + conf_score * 0.7

        vocab_score = vocabulary.get("vocabulary_score", 50)
        score = score * 0.7 + vocab_score * 0.3

        return max(0.0, min(100.0, round(score, 1)))

    def get_quick_analysis(self, text: str) -> Dict[str, Any]:
        """Quick analysis without grammar check (faster)"""
        filler = self.filler_detector.detect(text)
        confidence = self.confidence_analyzer.analyze_confidence(text)
        vocabulary = self.vocabulary_analyzer.analyze_vocabulary(text)

        return {
            "text": text,
            "filler": filler,
            "confidence": confidence,
            "vocabulary": vocabulary,
            "quick_score": self._calculate_quick_score(filler, confidence, vocabulary)
        }

    def _calculate_quick_score(
        self,
        filler: Dict,
        confidence: Dict,
        vocabulary: Dict
    ) -> float:
        """Calculate quick score without grammar"""
        score = 100.0
        score -= min(filler.get("filler_ratio", 0) * 3, 25)
        score = score * 0.4 + confidence.get("confidence_score", 50) * 0.4
        score += vocabulary.get("vocabulary_score", 50) * 0.2
        return max(0.0, min(100.0, round(score, 1)))

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts"""
        return [self.analyze(text) for text in texts]

    def get_improvement_plan(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement plan based on analysis"""
        suggestions = []

        if analysis.get("filler", {}).get("has_excessive_fillers"):
            suggestions.append("Focus on reducing filler words - practice pausing instead")

        conf_analysis = analysis.get("confidence", {})
        if conf_analysis.get("confidence_score", 100) < 60:
            suggestions.append("Work on assertiveness - avoid hedging phrases")

        vocab_analysis = analysis.get("vocabulary", {})
        if vocab_analysis.get("quality") in ("average", "limited"):
            suggestions.append("Expand vocabulary with professional synonyms")

        grammar_errors = analysis.get("grammar", {}).get("error_count", 0)
        if grammar_errors > 2:
            suggestions.append("Review basic grammar rules")

        structure = analysis.get("structure", {})
        if not structure.get("is_valid_structure", True):
            suggestions.append("Practice structured sentences with clear subject-verb")

        if not suggestions:
            suggestions.append("Great progress! Continue practicing to maintain level")

        return suggestions