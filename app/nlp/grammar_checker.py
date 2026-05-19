"""Grammar Checker Module for CMFH
Enhanced grammar analysis with more patterns
"""

import re
from typing import Dict, Any, List, Tuple


class GrammarChecker:
    """Enhanced grammar and language quality analyzer"""

    CONTRACTIONS = {
        r'\bi am\b': "I'm",
        r'\byou are\b': "you're",
        r'\bhe is\b': "he's",
        r'\bshe is\b': "she's",
        r'\bit is\b': "it's",
        r'\bwe are\b': "we're",
        r'\bthey are\b': "they're",
        r'\bi have\b': "I've",
        r'\byou have\b': "you've",
        r'\bwe have\b': "we've",
        r'\bthey have\b': "they've",
        r'\bi will\b': "I'll",
        r'\byou will\b': "you'll",
        r'\bhe will\b': "he'll",
        r'\bshe will\b': "she'll",
        r'\bit will\b': "it'll",
        r'\bwe will\b': "we'll",
        r'\bthey will\b': "they'll",
        r'\bi would\b': "I'd",
        r'\byou would\b': "you'd",
        r'\bi could\b': "I'd",
        r'\byou could\b': "you'd",
        r'\bi should\b': "I'd",
        r'\byou should\b': "you'd",
    }

    COMMON_MISSPELLINGS = {
        "teh": "the",
        "recieve": "receive",
        "wierd": "weird",
        "definately": "definitely",
        "occured": "occurred",
        "seperate": "separate",
        "accomodate": "accommodate",
        "untill": "until",
        "begining": "beginning",
        "beleive": "believe",
        "calender": "calendar",
        "concensus": "consensus",
        "enviroment": "environment",
        "goverment": "government",
        "independant": "independent",
        "neccessary": "necessary",
        "occassion": "occasion",
        "posession": "possession",
        "prefered": "preferred",
        "publically": "publicly",
        "recomend": "recommend",
        "refered": "referred",
        "relevent": "relevant",
        "submitt": "submit",
        "truely": "truly",
    }

    COMMON_ERRORS = [
        (r'\bdont\b', "don't", "missing apostrophe"),
        (r'\bcant\b', "can't", "missing apostrophe"),
        (r'\bwont\b', "won't", "missing apostrophe"),
        (r'\bwouldnt\b', "wouldn't", "missing apostrophe"),
        (r'\bcouldnt\b', "couldn't", "missing apostrophe"),
        (r'\bshouldnt\b', "shouldn't", "missing apostrophe"),
        (r'\bdidnt\b', "didn't", "missing apostrophe"),
        (r'\bdoesnt\b', "doesn't", "missing apostrophe"),
        (r'\bhasnt\b', "hasn't", "missing apostrophe"),
        (r'\bhavent\b', "haven't", "missing apostrophe"),
        (r'\bisnt\b', "isn't", "missing apostrophe"),
        (r'\barent\b', "aren't", "missing apostrophe"),
        (r'\bwasnt\b', "wasn't", "missing apostrophe"),
        (r'\bwerent\b', "weren't", "missing apostrophe"),
        (r'\btheyre\b', "they're", "missing apostrophe"),
        (r'\byoure\b', "you're", "missing apostrophe"),
        (r'\bwere\b', "we're", "confused with 'were'"),
        (r'\btheir\b', "they're", "confused with 'their'"),
        (r'\bthere\b', "they're", "confused with 'there'"),
        (r'\bits\b', "it's", "confused with 'its'"),
        (r'\byour\b', "you're", "confused with 'your'"),
        (r'\bto\b', "too", "confused with 'to'"),
        (r'\bto\b', "too", "confused with 'to'"),
        (r'\bthen\b', "than", "confused with 'then'"),
        (r'\balot\b', "a lot", "not a word"),
        (r'\bcould care less\b', "couldn't care less", "double negative"),
        (r'\bdebit\b', "debit", "should be 'debt'"),
        (r'\bintresting\b', "interesting", "spelling"),
        (r'\b随意的\b', "casual", "non-English word"),
    ]

    SENTENCE_STARTERS = [
        'i', 'he', 'she', 'it', 'we', 'they', 'you', 'this', 'that', 'there',
        'however', 'therefore', 'moreover', 'furthermore', 'although', 'because'
    ]

    def __init__(self):
        pass

    def check_grammar(self, text: str) -> Dict[str, Any]:
        """Enhanced grammar checking"""
        errors = []

        for pattern, correct, error_type in self.COMMON_ERRORS:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                errors.append({
                    "message": f"{error_type}: '{match.group()}' should be '{correct}'",
                    "category": "Grammar",
                    "rule": "spelling/contraction",
                    "offset": match.start(),
                    "length": len(match.group()),
                    "context": text[max(0, match.start()-20):min(len(text), match.end()+20)],
                    "replacements": [correct]
                })

        for wrong, correct in self.COMMON_MISSPELLINGS.items():
            pattern = r'\b' + re.escape(wrong) + r'\b'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                errors.append({
                    "message": f"Misspelling: '{match.group()}' should be '{correct}'",
                    "category": "Spelling",
                    "rule": "spelling",
                    "offset": match.start(),
                    "length": len(match.group()),
                    "context": text[max(0, match.start()-20):min(len(text), match.end()+20)],
                    "replacements": [correct]
                })

        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        for sent in sentences:
            if not sent:
                continue

            words = sent.split()
            if not words:
                continue

            first_word = words[0].lower().rstrip('.,!?;:()[]"')

            if first_word in self.SENTENCE_STARTERS:
                first_char = sent[0]
                if first_char.isalpha() and first_char.islower():
                    errors.append({
                        "message": f"Capitalize first word: '{first_word}'",
                        "category": "Capitalization",
                        "rule": "sentence_start",
                        "offset": text.find(sent),
                        "length": len(first_word),
                        "context": sent,
                        "replacements": [first_word.capitalize()]
                    })

            if len(words) >= 3:
                if words[0].lower() in ['the', 'a', 'an']:
                    noun_candidates = ['thing', 'stuff', 'place', 'time']
                    if any(noun in words[1:3] for noun in noun_candidates):
                        pass

        punctuation_errors = re.findall(r'\.\.\.+', text)
        if punctuation_errors:
            for match in re.finditer(r'\.\.\.+', text):
                errors.append({
                    "message": "Use single period or proper ellipsis",
                    "category": "Punctuation",
                    "rule": "ellipsis",
                    "offset": match.start(),
                    "length": len(match.group()),
                    "context": text[max(0, match.start()-10):min(len(text), match.end()+10)],
                    "replacements": ["..."]
                })

        if re.search(r'\s{2,}', text):
            errors.append({
                "message": "Multiple spaces found",
                "category": "Formatting",
                "rule": "whitespace",
                "offset": 0,
                "length": len(text),
                "context": text,
                "replacements": [" "]
            })

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
        complex_count = 0

        for sent in sentences:
            words = sent.split()
            word_count = len(words)

            has_verb = any(w.lower() in self._get_common_verbs() for w in words)
            has_subject = any(w.lower() in self.SENTENCE_STARTERS or w.lower() in self._get_nouns() for w in words)

            is_complex = word_count > 20
            if is_complex:
                complex_count += 1

            result_sentences.append({
                "text": sent[:50] + "..." if len(sent) > 50 else sent,
                "word_count": word_count,
                "has_verb": has_verb,
                "has_subject": has_subject,
                "is_long": word_count > 20,
                "is_simple": word_count <= 10
            })

        avg_length = sum(s.get("word_count", 0) for s in result_sentences) / max(len(result_sentences), 1)

        return {
            "sentence_count": len(result_sentences),
            "sentences": result_sentences,
            "avg_sentence_length": round(avg_length, 1),
            "complex_sentences": complex_count,
            "is_valid_structure": all(s.get("has_verb") or s.get("has_subject") or s.get("word_count", 0) < 5 for s in result_sentences)
        }

    def _get_common_verbs(self) -> List[str]:
        return ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'go', 'come', 'see', 'make', 'take', 'get', 'know', 'think', 'say', 'tell', 'want', 'use', 'find', 'give', 'try', 'call', 'need', 'feel', 'become', 'leave', 'put', 'keep', 'let', 'begin', 'seem', 'help', 'show', 'hear', 'play', 'run', 'move', 'live', 'believe', 'bring', 'happen', 'write', 'provide', 'sit', 'stand', 'lose', 'pay', 'meet', 'include', 'continue', 'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak', 'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'offer', 'remember', 'love', 'consider', 'appear', 'buy', 'wait', 'serve', 'die', 'send', 'expect', 'build', 'stay', 'fall', 'cut', 'reach', 'kill', 'remain']

    def _get_nouns(self) -> List[str]:
        return ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose', 'something', 'anything', 'nothing', 'everything', 'someone', 'anyone', 'everyone', 'person', 'people', 'thing', 'place', 'time', 'way', 'day', 'man', 'woman', 'child', 'world', 'life', 'hand', 'part', 'case', 'week', 'company', 'system', 'program', 'question', 'government', 'number', 'night', 'point', 'home', 'water', 'room', 'mother', 'area', 'money', 'story', 'fact', 'month', 'lot', 'right', 'study', 'book', 'eye', 'job', 'word', 'business', 'issue', 'side', 'kind', 'head', 'house', 'service', 'friend', 'father', 'power', 'hour', 'game', 'line', 'end', 'member', 'law', 'car', 'city', 'community', 'name', 'president', 'team', 'minute', 'idea', 'kid', 'body', 'information', 'back', 'parent', 'face', 'others', 'level', 'office', 'door', 'health', 'art', 'war', 'history', 'party', 'result', 'morning', 'reason', 'research', 'girl', 'guy', 'moment', 'air', 'teacher', 'force', 'education', 'foot', 'boy', 'age', 'policy', 'process', 'music', 'market', 'sense', 'nation', 'plan', 'college', 'interest', 'death', 'experience', 'effect', 'effort', 'article', 'best', 'class', 'road', 'action', 'family', 'value', 'paper']

    def get_pos_tags(self, text: str) -> List[Dict[str, Any]]:
        """Get Part-of-Speech tags using simple heuristics"""
        words = text.split()
        tags = []

        for word in words:
            clean_word = word.lower().rstrip('.,!?;:()[]"')
            pos = self._guess_pos(clean_word)
            tags.append({"text": word, "pos": pos, "lemma": clean_word})

        return tags

    def _guess_pos(self, word: str) -> str:
        """Guess part of speech using simple rules"""
        if word in ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them']:
            return 'PRP'
        if word in ['my', 'your', 'his', 'her', 'its', 'our', 'their', 'a', 'an', 'the', 'this', 'that']:
            return 'DT'
        if word in ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would']:
            return 'VBP'
        if word in ['and', 'but', 'or', 'because', 'although', 'while', 'if', 'when', 'that', 'which', 'who', 'whom', 'so', 'because']:
            return 'CC'
        if word.endswith('ing'):
            return 'VBG'
        if word.endswith('ed'):
            return 'VBN'
        if word.endswith('ly'):
            return 'RB'
        if word.endswith('tion') or word.endswith('ment') or word.endswith('ness') or word.endswith('ity') or word.endswith('ance') or word.endswith('ence'):
            return 'NN'
        if word.endswith('ful') or word.endswith('less') or word.endswith('ous') or word.endswith('ive') or word.endswith('able') or word.endswith('ible'):
            return 'JJ'
        if word.endswith('er') or word.endswith('est'):
            return 'JJR'

        return 'NN'