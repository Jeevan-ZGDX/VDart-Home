"""Grammar Checker Module for CMFH
Grammar analysis using regex patterns (no external NLP dependencies)
"""

import re
from typing import Dict, Any, List


class GrammarChecker:
    """Grammar and language quality analyzer - pure regex implementation"""

    COMMON_ERRORS = [
        (r'\bi\s+am\b', 'I am', 'i am'),
        (r'\bdont\b', "don't", 'dont'),
        (r'\bcant\b', "can't", 'cant'),
        (r'\bwont\b', "won't", 'wont'),
        (r'\bwouldnt\b', "wouldn't", 'wouldnt'),
        (r'\bcouldnt\b', "couldn't", 'couldnt'),
        (r'\bshouldnt\b', "shouldn't", 'shouldnt'),
        (r'\btheyre\b', "they're", 'theyre'),
        (r'\byoure\b', "you're", 'youre'),
        (r'\bim\b', "I'm", 'im'),
        (r'\bitll\b', "it'll", 'itll'),
        (r'\bthats\b', "that's", 'thats'),
        (r'\bwhats\b', "what's", 'whats'),
        (r'\bhes\b', "he's", 'hes'),
        (r'\bshes\b', "she's", 'shes'),
        (r'\bwhos\b', "who's", 'whos'),
        (r'\blets\b', "let's", 'lets'),
    ]

    SENTENCE_STARTERS = ['i', 'he', 'she', 'it', 'we', 'they', 'you', 'this', 'that', 'there']

    def __init__(self):
        pass

    def check_grammar(self, text: str) -> Dict[str, Any]:
        """Check grammar using pattern matching"""
        errors = []

        for pattern, correct, wrong in self.COMMON_ERRORS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                errors.append({
                    "message": f"Missing apostrophe: '{wrong}' should be '{correct}'",
                    "category": "Spelling",
                    "rule": "apostrophe",
                    "offset": match.start(),
                    "length": len(match.group()),
                    "context": text[max(0, match.start()-20):min(len(text), match.end()+20)],
                    "replacements": [correct]
                })

        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        for i, sent in enumerate(sentences):
            words = sent.split()
            if not words:
                continue

            first_word = words[0].lower().rstrip('.,!?;:')
            if first_word and not first_word[0].isupper() and first_word in self.SENTENCE_STARTERS:
                errors.append({
                    "message": f"Capitalize first word: '{first_word}'",
                    "category": "Capitalization",
                    "rule": "capitalization",
                    "offset": text.find(sent),
                    "length": len(first_word),
                    "context": sent,
                    "replacements": [first_word.capitalize()]
                })

            if len(words) > 2:
                has_article = words[0].lower() in ['a', 'an', 'the']
                has_noun = any(w.lower() in ['thing', 'stuff', 'person', 'place', 'idea'] for w in words[1:3])
                if has_article and has_noun:
                    pass

        return {
            "is_valid": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "text": text
        }

    def analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
        """Analyze sentence structure"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        result_sentences = []
        for sent in sentences:
            words = sent.split()
            has_verb = any(w.lower() in self._get_verbs() for w in words)
            has_subject = any(w.lower() in self.SENTENCE_STARTERS or w.lower() in self._get_nouns() for w in words)

            result_sentences.append({
                "text": sent,
                "has_verb": has_verb,
                "has_subject": has_subject,
                "word_count": len(words)
            })

        return {
            "sentence_count": len(result_sentences),
            "sentences": result_sentences,
            "is_valid_structure": all(s.get("has_verb") or s.get("has_subject") for s in result_sentences)
        }

    def _get_verbs(self) -> List[str]:
        return ['is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'go', 'come', 'see', 'make', 'take', 'get', 'know', 'think', 'say', 'tell', 'want', 'use', 'find', 'give', 'tell', 'try', 'call', 'need', 'feel', 'become', 'leave', 'put', 'keep', 'let', 'begin', 'seem', 'help', 'show', 'hear', 'play', 'run', 'move', 'live', 'believe', 'bring', 'happen', 'write', 'provide', 'sit', 'stand', 'lose', 'pay', 'meet', 'include', 'continue', 'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak', 'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'offer', 'remember', 'love', 'consider', 'appear', 'buy', 'wait', 'serve', 'die', 'send', 'expect', 'build', 'stay', 'fall', 'cut', 'reach', 'kill', 'remain']

    def _get_nouns(self) -> List[str]:
        return ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose', 'something', 'anything', 'nothing', 'everything', 'someone', 'anyone', 'everyone', 'person', 'people', 'thing', 'place', 'time', 'way', 'day', 'man', 'woman', 'child', 'world', 'life', 'hand', 'part', 'case', 'week', 'company', 'system', 'program', 'question', 'government', 'number', 'night', 'point', 'home', 'water', 'room', 'mother', 'area', 'money', 'story', 'fact', 'month', 'lot', 'right', 'study', 'book', 'eye', 'job', 'word', 'business', 'issue', 'side', 'kind', 'head', 'house', 'service', 'friend', 'father', 'power', 'hour', 'game', 'line', 'end', 'member', 'law', 'car', 'city', 'community', 'name', 'president', 'team', 'minute', 'idea', 'kid', 'body', 'information', 'back', 'parent', 'face', 'others', 'level', 'office', 'door', 'health', 'art', 'war', 'history', 'party', 'result', 'morning', 'reason', 'research', 'girl', 'guy', 'moment', 'air', 'teacher', 'force', 'education', 'foot', 'boy', 'age', 'policy', 'process', 'music', 'market', 'sense', 'nation', 'plan', 'college', 'interest', 'death', 'experience', 'effect', 'effort', 'article', 'best', 'class', 'road', 'action', 'family', 'value', 'paper']

    def get_pos_tags(self, text: str) -> List[Dict[str, Any]]:
        """Get Part-of-Speech tags using simple heuristics"""
        words = text.split()
        tags = []

        for word in words:
            clean_word = word.lower().rstrip('.,!?;:()[]"')
            pos = self._guess_pos(clean_word, word)
            tags.append({"text": word, "pos": pos, "lemma": clean_word})

        return tags

    def _guess_pos(self, word: str, original: str) -> str:
        """Guess part of speech using simple rules"""
        if word in ['i', 'you', 'he', 'she', 'it', 'we', 'they']:
            return 'PRP'
        if word in ['my', 'your', 'his', 'her', 'its', 'our', 'their', 'a', 'an', 'the']:
            return 'DT'
        if word in ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did']:
            return 'VBP'
        if word in ['and', 'but', 'or', 'because', 'although', 'while', 'if', 'when', 'that', 'which', 'who', 'whom']:
            return 'CC'
        if word.endswith('ing'):
            return 'VBG'
        if word.endswith('ed'):
            return 'VBN'
        if word.endswith('ly'):
            return 'RB'
        if word.endswith('tion') or word.endswith('ment') or word.endswith('ness'):
            return 'NN'
        if word.endswith('ful') or word.endswith('less') or word.endswith('ous'):
            return 'JJ'

        return 'NN'