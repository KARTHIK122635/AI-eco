import re
from typing import List, Set, Tuple, Optional
from enum import Enum

class ValidationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    FAILED = "FAILED"

class SemanticIsolationTester:
    STOP_WORDS = {
        "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with",
        "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "our", "their", "this", "that", "these", "those", "we", "they",
        "its", "it", "from", "as", "via", "using", "into"
    }

    NEGATION_WORDS = {
        "not", "no", "never", "cannot", "can't", "won't", "without",
        "neither", "nor", "lack", "lacks", "lacked", "lacking",
        "exclude", "excludes", "excluding", "fails", "failed", "failing",
        "unable", "prohibits", "prohibited", "omits", "omitted"
    }

    DOUBLE_NEGATION_PATTERNS = [
        r'\bcannot\s+deny\b',
        r'\bcan\s+not\s+deny\b',
        r'\bnot\s+impossible\b',
        r'\b(?:do|does|did)\s+not\s+disagree\b',
        r'\bnot\s+disagree\b',
        r'\bnot\s+uncommon\b',
        r'\bno\s+doubt\b',
        r'\bwithout\s+doubt\b',
        r'\bnot\s+unlike\b',
        r'\bnot\s+without\b'
    ]

    EXCEPTION_QUALIFIER_PATTERNS = [
        r'\bexcept\s+(?:for\s+)?([a-z0-9_\-\+\s]{2,30})\b',
        r'\bwith\s+the\s+exception\s+of\s+([a-z0-9_\-\+\s]{2,30})\b',
        r'\bexcluding\s+([a-z0-9_\-\+\s]{2,30})\b',
        r'\bsave\s+for\s+([a-z0-9_\-\+\s]{2,30})\b',
        r'\bapart\s+from\s+([a-z0-9_\-\+\s]{2,30})\b'
    ]

    CONDITIONAL_MARKERS = {
        "if", "unless", "assuming", "provided that", "in case",
        "hypothetical", "potentially", "contingent", "supposing",
        "should it", "were it", "conditional"
    }

    HISTORICAL_STATUS_WORDS = {
        "previously", "formerly", "originally", "historical", "prior to",
        "earlier", "past", "in the past", "formerly known", "deprecated",
        "discontinued", "ex-", "retired"
    }

    CURRENT_STATUS_WORDS = {
        "currently", "now", "presently", "today", "active", "is currently",
        "ongoing", "current"
    }

    @classmethod
    def normalize_text(cls, text: str) -> str:
        if not text:
            return ""
        norm = text.lower()
        norm = re.sub(r'[\r\n\t]+', ' ', norm)
        norm = re.sub(r'\s+', ' ', norm)
        return norm.strip()

    @classmethod
    def split_into_sentences(cls, text: str) -> List[str]:
        raw = re.split(r'(?<=[.!?;\n])\s+', text)
        sents = []
        for s in raw:
            s_clean = s.strip()
            if len(s_clean) > 2:
                sents.append(s_clean)
        return sents or [text.strip()]

    @classmethod
    def extract_content_words(cls, text: str) -> List[str]:
        tokens = re.split(r'\W+', text.lower())
        return [w for w in tokens if len(w) > 2 and w not in cls.STOP_WORDS]

    @classmethod
    def find_relevant_sentences(cls, norm_val: str, sentences: List[str]) -> Tuple[List[str], List[str]]:
        exact_sents = [s for s in sentences if norm_val in s]
        if exact_sents:
            return exact_sents, sentences

        val_content = cls.extract_content_words(norm_val)
        if not val_content:
            return sentences, sentences

        scored = []
        for s in sentences:
            s_content = set(cls.extract_content_words(s))
            overlap = set(val_content) & s_content
            scored.append((len(overlap), s))

        scored.sort(key=lambda x: x[0], reverse=True)
        max_overlap = scored[0][0]

        if max_overlap == 0:
            return sentences, sentences

        threshold = max(1, int(max_overlap * 0.6))
        supporting = [s for score, s in scored if score >= threshold]
        return supporting, sentences

    @classmethod
    def check_negation(cls, norm_val: str, supp_sents: list, all_sents: list):
        val_content = cls.extract_content_words(norm_val)
        val_tokens = re.split(r'\W+', norm_val)
        val_has_neg = any(w in cls.NEGATION_WORDS for w in val_tokens)

        neg_patterns = [
            r'\b(?:do\s+not|does\s+not|did\s+not|not|never|cannot|can\'t|won\'t|without|neither|nor|lack|lacks|lacked|lacking|exclude|excludes|excluding|fails\s+to|failed\s+to|failing\s+to|unable\s+to|omits?|prohibits?)\s+(?:requiring\s+|using\s+|having\s+|to\s+|for\s+)?([a-z0-9_\-\+]{3,25})\b',
            r'\b([a-z0-9_\-\+]{3,25})\s+is\s+not\b',
            r'\bno\s+([a-z0-9_\-\+]{3,25})\b'
        ]

        for s in supp_sents:
            norm_s = cls.normalize_text(s)
            s_tokens = re.split(r'\W+', norm_s)
            has_double_neg = any(re.search(pat, norm_s) for pat in cls.DOUBLE_NEGATION_PATTERNS)
            
            # Double negation contradicted by negative claim
            if has_double_neg and val_has_neg:
                return (ValidationStatus.FAILED, 'Evidence asserts double-negation affirmative, but proposed claim is negative')
            
            if has_double_neg and not val_has_neg:
                continue

            for pat in cls.EXCEPTION_QUALIFIER_PATTERNS:
                for m in re.finditer(pat, norm_s):
                    ex_term = m.group(1).lower()
                    if any(w in ex_term for w in val_content) or any(re.search(r'\b' + re.escape(w), ex_term) for w in val_content):
                        return (ValidationStatus.FAILED, f'Exception/qualifier in evidence excludes {ex_term}')

            for pat in neg_patterns:
                for m in re.finditer(pat, norm_s):
                    action = m.group(1).lower()
                    if action not in {"the", "and", "for", "with", "from"}:
                        if re.search(r'\b' + re.escape(action), norm_val) or any(t.startswith(action) or action.startswith(t) for t in val_content):
                            if not val_has_neg:
                                return (ValidationStatus.FAILED, f'Evidence explicitly negates or excludes {action}')

            s_has_neg = any(w in cls.NEGATION_WORDS for w in s_tokens)
            if s_has_neg and not val_has_neg and not has_double_neg:
                s_content = cls.extract_content_words(norm_s)
                if val_content and set(val_content).issubset(set(s_content)):
                    return (ValidationStatus.FAILED, 'Supporting sentence contains negation missing in affirmative claim')

            if val_has_neg and not s_has_neg:
                return (ValidationStatus.FAILED, 'Proposed claim introduces negation not in supporting sentence')

        # Check conflicting statements across sentences
        for s in all_sents:
            if s not in supp_sents:
                norm_s = cls.normalize_text(s)
                s_tokens = re.split(r'\W+', norm_s)
                s_has_neg = any(w in cls.NEGATION_WORDS for w in s_tokens)
                if s_has_neg:
                    # check if other sentence negates any action in val
                    for pat in neg_patterns:
                        for m in re.finditer(pat, norm_s):
                            action = m.group(1).lower()
                            if action not in {"the", "and", "for", "with", "from"}:
                                if re.search(r'\b' + re.escape(action), norm_val) or any(t.startswith(action) or action.startswith(t) for t in val_content):
                                    return (ValidationStatus.NEEDS_REVIEW, f'Conflicting statements in source: another sentence negates or qualifies {action}')
        return None

    @classmethod
    def check_conditional(cls, norm_val: str, supp_sents: list):
        val_has_cond = any(w in norm_val for w in cls.CONDITIONAL_MARKERS)
        for s in supp_sents:
            norm_s = cls.normalize_text(s)
            s_has_cond = any(re.search(r'\b' + re.escape(w) + r'\b', norm_s) for w in cls.CONDITIONAL_MARKERS)
            if s_has_cond and not val_has_cond:
                return (ValidationStatus.FAILED, 'Conditionality shift in supporting sentence')
        return None

    @classmethod
    def check_historical(cls, norm_val: str, supp_sents: list):
        val_has_hist = any(w in norm_val for w in cls.HISTORICAL_STATUS_WORDS)
        val_has_curr = any(w in norm_val for w in cls.CURRENT_STATUS_WORDS)
        for s in supp_sents:
            norm_s = cls.normalize_text(s)
            s_has_hist = any(re.search(r'\b' + re.escape(w) + r'\b', norm_s) for w in cls.HISTORICAL_STATUS_WORDS)
            s_has_curr = any(re.search(r'\b' + re.escape(w) + r'\b', norm_s) for w in cls.CURRENT_STATUS_WORDS)
            if s_has_hist and not s_has_curr:
                if val_has_curr or not val_has_hist:
                    return (ValidationStatus.FAILED, 'Historical status shift in supporting sentence')
        return None

if __name__ == '__main__':
    test_cases = [
        ('Case A (Unrelated negation)', 'The company does not disclose revenue. Its platform supports Python.', 'Its platform supports Python.', False),
        ('Case B (Unrelated conditional)', 'If requested, the service provides on-premise deployment. The product supports Python.', 'The product supports Python.', False),
        ('Case C (Unrelated historical)', 'The company previously sold hardware. Its current software supports Python.', 'Its current software supports Python.', False),
        ('Negation flip (Test 760)', 'We do not manufacture autonomous surgical robots.', 'We manufacture autonomous surgical robots.', True),
        ('Without (Test 658)', 'The framework operates without requiring PyTorch.', 'The framework requires PyTorch.', True),
        ('Neither (Test 678)', 'The platform supports neither Python nor R.', 'The platform supports Python and R.', True),
        ('Lack (Test 698)', 'The model lacks real-time streaming capabilities on edge hardware.', 'The model features real-time streaming capabilities.', True),
        ('Exclude (Test 718)', 'The benchmark excludes proprietary datasets.', 'The benchmark includes proprietary datasets.', True),
        ('Double negation valid', 'We cannot deny that the framework supports Python.', 'The framework supports Python.', False),
        ('Double negation invalid', 'We cannot deny that the framework supports Python.', 'The framework does not support Python.', True),
        ('Indirect negation', 'The software fails to encrypt user passwords.', 'The software encrypts user passwords.', True),
        ('Exception/qualifier', 'The software supports all languages except Python.', 'The software supports Python.', True),
        ('Conflicting sentences', 'The platform supports Python. However, legacy environments do not support Python.', 'The platform supports Python.', True)
    ]

    passed = 0
    for name, ev, val, should_fail in test_cases:
        sents = SemanticIsolationTester.split_into_sentences(ev)
        supp, all_s = SemanticIsolationTester.find_relevant_sentences(val.lower(), [s.lower() for s in sents])
        err = SemanticIsolationTester.check_negation(val.lower(), supp, all_s)
        if not err and 'conditional' in name.lower():
            err = SemanticIsolationTester.check_conditional(val.lower(), supp)
        if not err and 'historical' in name.lower():
            err = SemanticIsolationTester.check_historical(val.lower(), supp)

        has_err = err is not None
        is_ok = (has_err == should_fail)
        if is_ok:
            passed += 1
            res_str = "PASS"
        else:
            res_str = "FAIL"
        print(f"[{res_str}] {name}: should_fail={should_fail}, got_err={has_err} ({err[1] if err else 'None'})")

    print(f"\nResult: {passed}/{len(test_cases)} tests passed.")
