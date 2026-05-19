"""Feedback Generator Module for CMFH
Generate comprehensive feedback and suggestions
"""

from typing import Dict, Any, List


class FeedbackGenerator:
    """Generate comprehensive feedback for speakers"""

    def __init__(self):
        self._general_tips = {
            "grammar": [
                "Review subject-verb agreement rules",
                "Practice using correct tense consistently",
                "Read your speech aloud to catch errors",
                "Keep sentences concise and clear"
            ],
            "filler": [
                "Practice pauses instead of filler words",
                "Take a breath when tempted to use fillers",
                "Record yourself and count filler words",
                "Replace 'um' with brief silence"
            ],
            "confidence": [
                "Use strong, direct statements",
                "Avoid hedging words like 'maybe' and 'I think'",
                "Maintain eye contact while speaking",
                "Practice power poses before speaking"
            ],
            "vocabulary": [
                "Learn synonyms for common weak words",
                "Use specific, concrete terms",
                "Incorporate action verbs",
                "Read professional content to expand vocabulary"
            ],
            "tedx": [
                "Start with a compelling hook",
                "Tell personal stories to illustrate points",
                "Use simple, clear language",
                "End with a call to action"
            ]
        }

    def generate_feedback(
        self,
        nlp_analysis: Dict[str, Any],
        tedx_analysis: Dict[str, Any],
        score_breakdown: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive feedback"""
        feedback = {
            "summary": self._generate_summary(score_breakdown),
            "strengths": self._identify_strengths(nlp_analysis, tedx_analysis),
            "areas_for_improvement": self._identify_improvements(nlp_analysis, tedx_analysis),
            "specific_tips": self._generate_specific_tips(nlp_analysis, tedx_analysis),
            "action_items": self._generate_action_items(nlp_analysis, tedx_analysis, score_breakdown),
            "encouragement": self._generate_encouragement(score_breakdown)
        }

        return feedback

    def _generate_summary(self, scores: Dict[str, Any]) -> str:
        """Generate summary based on scores"""
        overall = scores.get("overall_score", 0)
        grade = scores.get("grade", "F")

        if overall >= 80:
            return f"Excellent performance! You scored {overall} ({grade}) - your communication is strong and professional."
        elif overall >= 60:
            return f"Good effort! You scored {overall} ({grade}) - with some practice, you'll be communicating professionally."
        else:
            return f"You scored {overall} ({grade}). Focus on the key areas below to improve your communication skills."

    def _identify_strengths(
        self,
        nlp_analysis: Dict[str, Any],
        tedx_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify strengths"""
        strengths = []

        if nlp_analysis.get("grammar", {}).get("error_count", 5) < 2:
            strengths.append("Strong grammar - your sentences are well-structured")
        if nlp_analysis.get("filler", {}).get("filler_ratio", 10) < 2:
            strengths.append("Minimal filler words - you speak clearly")
        if nlp_analysis.get("confidence", {}).get("confidence_score", 0) > 70:
            strengths.append("Confident delivery - you speak with authority")
        if nlp_analysis.get("vocabulary", {}).get("vocabulary_score", 0) > 70:
            strengths.append("Good vocabulary - you use varied and appropriate words")
        if tedx_analysis.get("tedx_score", 0) > 60:
            strengths.append("TEDX-style elements - you use hooks and storytelling")

        if not strengths:
            strengths.append("Good effort - keep practicing to build your skills")

        return strengths

    def _identify_improvements(
        self,
        nlp_analysis: Dict[str, Any],
        tedx_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify areas for improvement"""
        improvements = []

        errors = nlp_analysis.get("grammar", {}).get("error_count", 0)
        if errors > 2:
            improvements.append(f"Address {errors} grammar errors in your speech")

        filler_ratio = nlp_analysis.get("filler", {}).get("filler_ratio", 0)
        if filler_ratio > 3:
            improvements.append(f"Reduce filler words (currently {filler_ratio}% of speech)")

        conf_score = nlp_analysis.get("confidence", {}).get("confidence_score", 100)
        if conf_score < 60:
            improvements.append("Use more confident language - avoid hedging")

        vocab_score = nlp_analysis.get("vocabulary", {}).get("vocabulary_score", 100)
        if vocab_score < 50:
            improvements.append("Expand vocabulary - use more precise words")

        tedx_score = tedx_analysis.get("tedx_score", 100)
        if tedx_score < 50:
            improvements.append("Add more TEDX-style elements - hooks, stories, calls to action")

        return improvements

    def _generate_specific_tips(
        self,
        nlp_analysis: Dict[str, Any],
        tedx_analysis: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate specific tips for each category"""
        tips = {}

        errors = nlp_analysis.get("grammar", {}).get("error_count", 0)
        if errors > 0:
            tips["grammar"] = self._general_tips["grammar"][:2]
        else:
            tips["grammar"] = ["Your grammar is strong! Keep it up."]

        filler_ratio = nlp_analysis.get("filler", {}).get("filler_ratio", 0)
        if filler_ratio > 2:
            tips["filler"] = self._general_tips["filler"]
        else:
            tips["filler"] = ["Great job minimizing fillers!"]

        conf_score = nlp_analysis.get("confidence", {}).get("confidence_score", 100)
        if conf_score < 70:
            tips["confidence"] = self._general_tips["confidence"]
        else:
            tips["confidence"] = ["Your confidence level is excellent!"]

        vocab = nlp_analysis.get("vocabulary", {})
        if vocab.get("quality") in ("average", "limited"):
            tips["vocabulary"] = self._general_tips["vocabulary"]
        else:
            tips["vocabulary"] = ["Your vocabulary is well-developed."]

        tedx_score = tedx_analysis.get("tedx_score", 100)
        if tedx_score < 60:
            tips["tedx_style"] = self._general_tips["tedx"]
        else:
            tips["tedx_style"] = ["You have good TEDX-style presentation!"]

        return tips

    def _generate_action_items(
        self,
        nlp_analysis: Dict[str, Any],
        tedx_analysis: Dict[str, Any],
        scores: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable items"""
        action_items = []

        filler = nlp_analysis.get("filler", {})
        if filler.get("filler_ratio", 0) > 3:
            action_items.append("Practice: Record 2 minutes and count filler words - aim for <2%")

        conf = nlp_analysis.get("confidence", {})
        if conf.get("confidence_score", 100) < 60:
            action_items.append("Exercise: Replace 'I think', 'maybe', 'probably' with direct statements")

        vocab = nlp_analysis.get("vocabulary", {})
        if vocab.get("quality") != "excellent":
            action_items.append("Learn: Pick 5 power words and use them in sentences daily")

        if tedx_analysis.get("tedx_score", 100) < 50:
            action_items.append("Watch: Study a favorite TED Talk and note the opening hook")

        overall = scores.get("overall_score", 0)
        if overall < 60:
            action_items.append("Focus: Practice 10 minutes daily for 2 weeks")

        return action_items

    def _generate_encouragement(self, scores: Dict[str, Any]) -> str:
        """Generate encouraging message"""
        overall = scores.get("overall_score", 0)

        if overall >= 80:
            return "You're on track for professional communication! Keep refining your skills."
        elif overall >= 60:
            return "Progress takes time. Every practice session makes you better!"
        else:
            return "Everyone starts somewhere. Focus on one area at a time and celebrate small wins!"

    def generate_progress_report(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate progress report from session history"""
        if not history:
            return {"message": "No sessions recorded yet. Start practicing!"}

        scores = [s.get("overall_score", 0) for s in history if "overall_score" in s]
        if not scores:
            return {"message": "No score data available"}

        avg = sum(scores) / len(scores)
        latest = scores[-1]
        first = scores[0]
        improvement = latest - first

        return {
            "total_sessions": len(history),
            "average_score": round(avg, 1),
            "latest_score": latest,
            "improvement": round(improvement, 1),
            "trend": "improving" if improvement > 5 else "stable" if improvement > -5 else "declining",
            "recommendation": self._get_progress_recommendation(improvement, avg)
        }

    def _get_progress_recommendation(self, improvement: float, average: float) -> str:
        """Get recommendation based on progress"""
        if improvement > 10 and average > 70:
            return "Excellent progress! You're ready for advanced techniques."
        elif improvement > 5:
            return "Good improvement! Keep consistent practice."
        elif average > 70:
            return "You're maintaining a good level. Challenge yourself more."
        else:
            return "Focus on fundamentals. Daily short practice will help."