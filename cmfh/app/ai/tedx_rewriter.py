"""TEDX Rewriter Module for CMFH
Professional speech rewriting using Phi-3 LLM via Ollama
"""

import json
from typing import Dict, Any, Optional, List
import requests


class Phi3Rewriter:
    """Professional speech rewriter using Phi-3 Mini via Ollama"""

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model_name: str = "phi3",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._is_available = None

    def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                return any(self.model_name in name for name in model_names)
            return False
        except Exception:
            return False

    def is_available(self) -> bool:
        """Check if rewriter is available"""
        if self._is_available is None:
            self._is_available = self.check_ollama()
        return self._is_available

    def rewrite(self, text: str, style: str = "professional") -> Dict[str, Any]:
        """Rewrite text in specified style"""
        if not self.is_available():
            return self._fallback_rewrite(text, style)

        prompt = self._build_prompt(text, style)

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stream": False
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                rewritten = result.get("response", "").strip()
                return {
                    "original": text,
                    "rewritten": rewritten,
                    "style": style,
                    "success": True,
                    "source": "ollama"
                }
            else:
                return self._fallback_rewrite(text, style)

        except Exception as e:
            return self._fallback_rewrite(text, style, error=str(e))

    def _build_prompt(self, text: str, style: str) -> str:
        """Build prompt for professional rewrite"""
        base_prompt = f"""You are a professional speech coach and communication expert.
Your task is to rewrite the following speech to be more professional, confident, and impactful.

Transform informal speech into TED-style professional communication.
Remove filler words, improve vocabulary, and add confidence.

Original speech:
{text}

Requirements:
- Keep the same meaning and ideas
- Make it more professional and confident
- Use stronger, more impactful words
- Remove filler words (um, uh, like, basically, actually, you know)
- Improve sentence structure
- Make it sound like a confident speaker

Rewritten speech:"""

        if style == "tedx":
            base_prompt += """

Also apply these TED-style principles:
- Start with a hook or story
- Use clear, simple language
- Build to a key message
- End with a call to action or insight
"""
        return base_prompt

    def _fallback_rewrite(
        self,
        text: str,
        style: str,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fallback rewrite without LLM"""
        import re

        filler_replacements = {
            r'\b(um|uh|er|ah)\b': '',
            r'\bbasically\b': 'essentially',
            r'\bactually\b': 'in fact',
            r'\bliterally\b': 'truly',
            r'\byou know\b': '',
            r'\bI think\b': 'I believe',
            r'\bkind of\b': 'somewhat',
            r'\bsort of\b': 'partially',
            r'\blike\b(?=\s)': '',
            r'\bhonestly\b': 'frankly',
        }

        rewritten = text
        for pattern, replacement in filler_replacements.items():
            rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)

        rewritten = re.sub(r'\s+', ' ', rewritten).strip()
        rewritten = rewritten[0].upper() + rewritten[1:] if rewritten else rewritten

        return {
            "original": text,
            "rewritten": rewritten,
            "style": style,
            "success": False if error else True,
            "source": "fallback",
            "error": error,
            "message": "Used rule-based rewrite - Ollama unavailable"
        }

    def batch_rewrite(self, texts: List[str], style: str = "professional") -> List[Dict[str, Any]]:
        """Rewrite multiple texts"""
        return [self.rewrite(text, style) for text in texts]

    def get_ollama_status(self) -> Dict[str, Any]:
        """Get Ollama status"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "available": True,
                    "models": [m.get("name") for m in models],
                    "target_model_available": self.model_name in [m.get("name") for m in models]
                }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }


class RuleBasedRewriter:
    """Fallback rule-based rewriter when LLM is unavailable"""

    FILLER_WORDS = {
        "um", "uh", "er", "ah", "basically", "actually", "literally",
        "honestly", "you know", "I think", "kind of", "sort of"
    }

    IMPROVEMENTS = {
        "good": "excellent",
        "bad": "poor",
        "nice": "pleasant",
        "big": "significant",
        "small": "minor",
        "thing": "aspect",
        "stuff": "elements",
        "really": "genuinely",
        "very": "particularly",
        "quite": "notably",
        "try": "attempt",
        "help": "assist",
        "make": "create",
        "get": "obtain",
        "use": "utilize"
    }

    def rewrite(self, text: str) -> str:
        """Apply rule-based improvements"""
        import re

        words = text.split()

        improved_words = []
        for word in words:
            lower = word.lower().strip('.,!?;:')
            if lower in self.FILLER_WORDS:
                continue
            if lower in self.IMPROVEMENTS:
                improved_words.append(self.IMPROVEMENTS[lower])
            else:
                improved_words.append(word)

        result = ' '.join(improved_words)
        result = re.sub(r'\s+', ' ', result).strip()
        result = result[0].upper() + result[1:] if result else result

        return result