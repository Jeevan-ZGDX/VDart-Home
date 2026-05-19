"""Singleton model registry for CMFH services."""

from ..stt.whisper_engine import WhisperEngine
from ..nlp.analyzer import NLPAnalyzer
from ..ai.tedx_rewriter import Phi3Rewriter
from ..tedx import TEDXAnalyzer
from ..feedback.scoring_engine import ScoringEngine
from ..feedback.feedback_generator import FeedbackGenerator
from ..database.sqlite_manager import SQLiteManager
from ..vision import PoseAnalyzer


class ModelRegistry:
    """Lazy-loaded shared service instances."""

    def __init__(self):
        self.whisper = WhisperEngine()
        self.nlp = NLPAnalyzer()
        self.rewriter = Phi3Rewriter()
        self.tedx = TEDXAnalyzer()
        self.scoring = ScoringEngine()
        self.feedback = FeedbackGenerator()
        self.db = SQLiteManager()
        self.pose = PoseAnalyzer()
        self._warmed = False

    def warmup(self) -> None:
        """Load CPU-heavy models at startup."""
        if self._warmed:
            return
        print("Loading Whisper model...")
        self.whisper._load_model()
        print(f"Whisper ({self.whisper.model_size}) ready.")
        _ = self.nlp  # ensure NLP submodules initialize
        ollama_ok = self.rewriter.is_available()
        print(f"Ollama / Phi-3 available: {ollama_ok}")
        self._warmed = True


registry = ModelRegistry()
