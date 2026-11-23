"""
Evidence Validator and Anti-Hallucination Enforcement Engine.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 22 - Comprehensive Semantic Adversarial Validation, Negation/Voice Inversion Detection,
Strict Taxonomy Compliance, and Heuristic Safeguards
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple, Set, List

from core.enrichment.schemas import (
    EnrichmentResult,
    ValidationStatus,
    FORBIDDEN_INFERENCE_FIELDS,
    PROTECTED_JOB_FIELDS,
    RETAINED_15_REVIEW_JOB_IDS,
    CLASSIFICATION_RULES_VERSION,
    COMPOUND_CLASSIFICATION_CONCEPTS,
    CLASSIFICATION_RULES,
    is_approved_category,
    APPROVED_TAXONOMY
)

logger = logging.getLogger("EvidenceValidator")


class EvidenceValidator:
    """
    Strict field-level evidence validator enforcing anti-hallucination rules.
    Audit 22:
    - Enforces semantic contradiction, negation polarity, date/number, modality,
      and attribution verification. Never accepts mere word presence.
    - Extends adversarial checks: active vs passive voice, subject/object reversal,
      some vs all, improved vs doubled, conditional vs factual, historical vs current,
      and expanded negation (without, neither, lack, exclude).
    - Invariant: A claim that cannot be conclusively validated must be NEEDS_REVIEW, never VERIFIED.
    - Enforces approved taxonomy membership across all providers.
    - Applies heuristic safeguards to list fields (never automatically VERIFIED).
    """

    NEGATION_WORDS = {
        "not", "no", "never", "none", "neither", "nor", "without",
        "cannot", "cant", "can't", "wont", "won't", "dont", "don't",
        "doesnt", "doesn't", "didnt", "didn't", "isnt", "isn't",
        "arent", "aren't", "wasnt", "wasn't", "werent", "weren't",
        "hardly", "scarcely", "barely", "refuse", "refuses", "fails to",
        "lack", "lacks", "lacked", "lacking",
        "exclude", "excludes", "excluded", "excluding",
        "omits", "omitted", "omitting", "exempt", "devoid of", "free of", "absence of"
    }

    PLAN_MODALITY_WORDS = {
        "plan", "plans", "planned", "planning", "plan to",
        "intend", "intends", "intended", "intending", "intend to",
        "aim", "aims", "aimed", "aiming", "aim to", "aims to",
        "propose", "proposes", "proposed", "proposing", "propose to",
        "hope", "hopes", "hoped", "hoping",
        "target", "targets", "targeted", "targeting",
        "seek to", "seeking to", "seeks to", "expected to", "expects to",
        "will develop", "to develop", "in development", "roadmap", "aspire", "aspires"
    }

    ACCOMPLISHED_MODALITY_WORDS = {
        "have developed", "has developed", "had developed", "developed",
        "have built", "has built", "built", "created", "have created", "has created",
        "launched", "have launched", "has launched",
        "deployed", "have deployed", "has deployed",
        "operates", "provides", "offers", "manufacture", "manufactures", "produces"
    }

    TENTATIVE_ATTRIBUTION_WORDS = {
        "reports that", "reported that", "report that",
        "claims that", "claimed that", "claim that",
        "states that", "stated that", "state that",
        "alleges", "alleged", "believes", "believed",
        "suggests", "preliminary", "pilot study", "anecdotal"
    }

    PROVEN_CAUSAL_WORDS = {
        "independently proven", "proven to", "proves that", "proved that",
        "proven", "guarantees", "guaranteed", "demonstrated conclusively",
        "established fact", "causes", "cure", "cures"
    }

    PARTIAL_QUANTIFIERS = {
        "some", "select", "a few", "few", "subset", "partial", "partially",
        "limited", "certain", "several", "optional", "sometimes", "occasionally"
    }

    UNIVERSAL_QUANTIFIERS = {
        "all", "every", "each", "entire", "entirely", "always",
        "universally", "completely", "total", "wholly", "100%"
    }

    METRIC_MULTIPLIERS = {
        "doubled", "tripled", "quadrupled", "halved", "10x", "5x", "2x", "3x", "100x",
        "twofold", "threefold", "fourfold", "tenfold"
    }

    CONDITIONAL_MARKERS = {
        "if", "unless", "provided that", "providing that", "assuming",
        "subject to", "in case of", "on condition that", "whether", "conditional upon"
    }

    HISTORICAL_STATUS_WORDS = {
        "previously", "formerly", "historically", "used to", "in the past",
        "prior to", "earlier", "former", "previous", "discontinued"
    }

    CURRENT_STATUS_WORDS = {
        "currently", "presently", "now", "today", "active", "is currently",
        "currently operates", "currently provides"
    }

    CAUSAL_CONNECTIVES = {
        "caused", "causes", "leading directly to", "resulted in",
        "which produced", "thereby causing", "directly caused", "responsible for causing"
    }

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with",
        "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "our", "their", "this", "that", "these", "those", "we", "they",
        "its", "it", "from", "as", "via", "using", "into"
    }

    DOUBLE_NEGATION_PATTERNS = [
        r'\bcannot\s+deny\b',
        r'\bcan\s+not\s+deny\b',
        r'\b(?:cannot|can\s+not)\s+(?:be\s+)?denied?\b',
        r'\b(?:cannot|can\s+not)\s+(?:be\s+)?disputed?\b',
        r'\b(?:cannot|can\s+not)\s+(?:be\s+)?ignored?\b',
        r'\b(?:cannot|can\s+not)\s+(?:be\s+)?overlooked?\b',
        r'\bnot\s+impossible\b',
        r'\b(?:do|does|did)\s+not\s+disagree\b',
        r'\bnot\s+disagree\b',
        r'\bnot\s+uncommon\b',
        r'\bno\s+doubt\b',
        r'\bwithout\s+doubt\b',
        r'\bnot\s+unlike\b',
        r'\bnot\s+without\b'
    ]

    GENERIC_NOUNS = {
        'integration', 'integrations', 'support', 'supports', 'solution', 'solutions',
        'platform', 'platforms', 'system', 'systems', 'tool', 'tools', 'service', 'services',
        'feature', 'features', 'capability', 'capabilities', 'technology', 'technologies',
        'product', 'products', 'application', 'applications', 'api', 'apis', 'software',
        'model', 'models', 'data', 'access'
    }

    EXCEPTION_QUALIFIER_PATTERNS = [
        r'\bexcept\s+(?:for\s+)?([a-z0-9_\-\+\s]{2,30})\b',
        r'\bwith\s+the\s+exception\s+of\s+([a-z0-9_\-\+\s]{2,30})\b',
        r'\bexcluding\s+([a-z0-9_\-\+\s]{2,30})\b',
        r'\bsave\s+for\s+([a-z0-9_\-\+\s]{2,30})\b',
        r'\bapart\s+from\s+([a-z0-9_\-\+\s]{2,30})\b'
    ]

    TRANSITIVE_VERBS = {
        'support', 'supports', 'supported', 'supporting',
        'provide', 'provides', 'provided', 'providing',
        'use', 'uses', 'used', 'using',
        'run', 'runs', 'ran', 'running',
        'offer', 'offers', 'offered', 'offering',
        'deploy', 'deploys', 'deployed', 'deploying',
        'feature', 'features', 'featured', 'featuring',
        'include', 'includes', 'included', 'including',
        'have', 'has', 'had', 'having',
        'build', 'builds', 'built', 'building',
        'make', 'makes', 'made', 'making',
        'develop', 'develops', 'developed', 'developing',
        'contain', 'contains', 'contained', 'containing',
        'allow', 'allows', 'allowed', 'allowing',
        'enable', 'enables', 'enabled', 'enabling',
        'target', 'targets', 'targeted', 'targeting',
        'integrate', 'integrates', 'integrated', 'integrating',
        'manufacture', 'manufactures', 'manufactured', 'manufacturing',
        'focus', 'focuses', 'focused', 'focusing',
        'utilize', 'utilizes', 'utilized', 'utilizing',
        'adopt', 'adopts', 'adopted', 'adopting',
        'serve', 'serves', 'served', 'serving',
        'produce', 'produces', 'produced', 'producing',
        'stole', 'steal', 'stealing', 'stolen', 'acquired', 'acquire'
    }

    # Audit 25 Priority 2: Attribution, Limited Scope, Manual Approval, and Intent Qualifiers
    ATTRIBUTION_QUALIFIERS = [
        r'\balleged(?:ly)?\b',
        r'\balleging\b',
        r'\breportedly\b',
        r'\breports?\b',
        r'\breported\b',
        r'\breporting\b',
        r'\baccording\s+to\b',
        r'\bsays?\b',
        r'\bsaid\b',
        r'\bsaying\b',
        r'\bstates?\b',
        r'\bstated\b',
        r'\bstating\b',
        r'\bclaims?\b',
        r'\bclaimed\b',
        r'\bclaiming\b',
        r'\basserts?\b',
        r'\basserted\b',
        r'\bpurports?\b',
        r'\bpurported(?:ly)?\b'
    ]

    LIMITATION_QUALIFIERS = [
        r'\bonly\s+(?:in|after|when|for|with|if|under|upon)\b',
        r'\bsubject\s+to\b',
        r'\brestricted\s+to\b',
        r'\blimited\s+to\b',
        r'\bconditional\s+upon\b',
        r'\bcontingent\s+upon\b',
        r'\bmanual\s+approval\b',
        r'\bhuman\s+approval\b',
        r'\bmanual\s+review\b',
        r'\bunless\b'
    ]

    INTENT_QUALIFIERS = [
        r'\bplans?\s+to\b',
        r'\bplanned\s+to\b',
        r'\bplanning\s+to\b',
        r'\baims?\s+to\b',
        r'\baimed\s+to\b',
        r'\bintends?\s+to\b',
        r'\bintended\s+to\b',
        r'\bseeking\s+to\b',
        r'\bsought\s+to\b',
        r'\bscheduled\s+to\b',
        r'\bhoping\s+to\b',
        r'\btargets?\s+to\b'
    ]

    CONFLICTING_STATES = [
        ({'free', 'open_source', 'unpaid'}, {'paid', 'commercial', 'subscription', 'proprietary'}),
        ({'available', 'active', 'operational'}, {'unavailable', 'deprecated', 'discontinued', 'sunset'}),
        ({'public'}, {'private', 'confidential', 'internal'}),
        ({'unlimited'}, {'limited', 'capped', 'restricted'})
    ]

    @classmethod
    def split_into_sentences(cls, text: str) -> List[str]:
        """Splits evidence into sentences/clauses for context isolation (Audit 23 & Audit 24)."""
        raw = re.split(r'(?<=[.!?;\n])\s+|,\s*(?:but|however|whereas|while|although)\s+', str(text or ''))
        sents = []
        for s in raw:
            s_clean = s.strip()
            if len(s_clean) > 2:
                sents.append(s_clean)
        return sents or [str(text or '').strip()]

    @classmethod
    def extract_content_words(cls, text: str) -> List[str]:
        """Extracts significant content words from text."""
        tokens = re.split(r'\W+', str(text or '').lower())
        return [w for w in tokens if len(w) > 2 and w not in cls.STOP_WORDS]

    @classmethod
    def find_relevant_sentences(cls, norm_val: str, sentences: List[str]) -> Tuple[List[str], List[str]]:
        """
        Isolates supporting sentences matching the proposed claim from unrelated evidence sentences (Audit 23).
        Returns (supporting_sentences, all_sentences).
        """
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

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        """
        Performs safe whitespace and punctuation normalization:
        - Collapses contiguous whitespace into a single ASCII space.
        - Normalizes curly quotes and unicode dashes.
        - Strips surrounding whitespace and case-folds.
        """
        if not text:
            return ""
        norm = re.sub(r'[\s\u200b\xa0]+', ' ', str(text)).strip().lower()
        norm = norm.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
        norm = norm.replace("—", "-").replace("–", "-")
        return norm

    APPLICATION_LABELS = {
        "company name", "company name:", "ai focus", "ai focus:",
        "existing description", "existing description:", "evidence", "evidence:",
        "product name", "product name:", "features", "features:",
        "title", "title:", "abstract", "abstract:", "article content", "article content:",
        "job title", "job title:", "company", "company:", "description", "description:"
    }

    APPLICATION_LABEL_REGEX = re.compile(
        r"^(?:company\s+name|ai\s+focus|existing\s+description|evidence|product\s+name|features|title|abstract|article\s+content|job\s+title|company|description)\s*:",
        re.IGNORECASE
    )

    @classmethod
    def has_application_label_prefix(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detects whether text begins with or contains an application-generated context label (Audit 28).
        Matches both exact labels ('AI Focus:') and label-plus-value combinations
        ('AI Focus: Applied AI & Automation', 'Company Name: Anthropic').
        """
        if not text:
            return False, None
        stripped = text.strip()
        match = cls.APPLICATION_LABEL_REGEX.match(stripped)
        if match:
            return True, match.group(0).strip()
        norm = cls.normalize_text(stripped)
        match_norm = cls.APPLICATION_LABEL_REGEX.match(norm)
        if match_norm:
            return True, match_norm.group(0).strip()
        if norm in cls.APPLICATION_LABELS:
            return True, norm
        return False, None

    @classmethod
    def strip_application_labels(cls, text: str) -> str:
        """
        Strips application-generated context label prefixes from text, leaving only
        the underlying stored source content (Audit 28).
        """
        if not text:
            return ""
        lines = text.splitlines()
        clean_lines = []
        for line in lines:
            line_str = line.strip()
            match = cls.APPLICATION_LABEL_REGEX.match(line_str)
            if match:
                clean_lines.append(line_str[match.end():].strip())
            else:
                clean_lines.append(line_str)
        return "\n".join(clean_lines)

    @classmethod
    def is_verbatim_excerpt(
        cls,
        evidence: str,
        source_text: str,
        raw_source_content: Optional[str] = None
    ) -> bool:
        """
        Checks if the evidence excerpt is an exact verbatim substring of the underlying stored source content.
        Strictly rejects application-generated context labels, whether standalone or followed by text (Audit 28).
        """
        if not evidence or not source_text:
            return False

        # Reject any evidence that begins with or contains an application-generated label prefix
        has_lbl, _ = cls.has_application_label_prefix(evidence)
        if has_lbl:
            return False

        norm_ev = cls.normalize_text(evidence)
        if not norm_ev:
            return False

        # Disallow purely application-generated label prefixes as evidence
        if norm_ev in cls.APPLICATION_LABELS:
            return False

        # If raw_source_content (unlabeled stored values) is provided, validate strictly against it
        if raw_source_content:
            norm_raw = cls.normalize_text(raw_source_content)
            return norm_ev in norm_raw

        # Otherwise, strip application-generated labels from source_text before checking
        unlabeled_source = cls.strip_application_labels(source_text)
        norm_unlabeled = cls.normalize_text(unlabeled_source)
        return norm_ev in norm_unlabeled

    @classmethod
    def check_item_supported_in_evidence(cls, item: str, norm_ev: str) -> bool:
        """
        Checks whether an individual skill, technology, or term is substantiated in the normalized evidence excerpt.
        Uses whole-word boundary matching to avoid substring false positives.
        """
        norm_item = cls.normalize_text(item)
        if not norm_item:
            return False

        if norm_item in norm_ev:
            if len(norm_item) <= 4:
                escaped = re.escape(norm_item)
                pattern = r'(?:\A|[\s,;./()\[\]"\'`])' + escaped + r'(?:[\s,;./()\[\]"\'`:]|\Z)'
                return bool(re.search(pattern, norm_ev))
            return True

        synonyms = {
            "large language models": ["llms", "llm"],
            "llms": ["large language models", "llm"],
            "natural language processing": ["nlp"],
            "nlp": ["natural language processing"],
            "computer vision": ["cv"],
            "fastapi": ["fastapi"],
            "scikit-learn": ["sklearn", "scikit learn"],
            "postgresql": ["postgres"]
        }
        if norm_item in synonyms:
            for syn in synonyms[norm_item]:
                if syn in norm_ev:
                    return True

        return False

    @classmethod
    def check_numbers_and_dates(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Extracts numbers, years, and dates. If the proposed text contains any number,
        year, or quantitative figure not present in the evidence, returns FAILED.
        """
        val_numbers = re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', norm_val)
        ev_numbers = set(re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', norm_ev))
        for num in val_numbers:
            if num not in ev_numbers:
                return (
                    ValidationStatus.FAILED,
                    f"Semantic Mismatch: Proposed text introduces number/date '{num}' not supported by evidence."
                )
        return None

    @classmethod
    def check_negation_contradiction(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Detects negation polarity flip or contradiction between evidence and proposed value with
        sentence/clause context isolation (Audit 21, Audit 22, and Audit 23).
        Handles: not, no, never, without, neither, lack, exclude, fails to, double negation,
        indirect negation, qualifiers, and conflicting source statements.
        """
        sents = cls.split_into_sentences(norm_ev)
        supp_sents, all_sents = cls.find_relevant_sentences(norm_val, sents)

        val_content = cls.extract_content_words(norm_val)
        val_tokens = [w for w in re.split(r'\W+', norm_val) if w]
        val_has_neg = any(w in cls.NEGATION_WORDS for w in val_tokens)

        neg_patterns = [
            r'\b(?:do\s+not|does\s+not|did\s+not|not|never|cannot|can\'t|won\'t|without|neither|nor|lack|lacks|lacked|lacking|exclude|excludes|excluding|fails\s+to|failed\s+to|failing\s+to|unable\s+to|omits?|prohibits?)\s+(?:requiring\s+|using\s+|having\s+|to\s+|for\s+)?([a-z0-9_\-\+]{3,25})\b',
            r'\bneither\s+(?:company|firm|organization|party|entity|system|product|service|of\s+them)?\s*([a-z0-9_\-\+]{3,25})\b',
            r'\b([a-z0-9_\-\+]{3,25})\s+is\s+not\b',
            r'\bno\s+([a-z0-9_\-\+]{3,25})\b'
        ]

        # 1. Check supporting sentences for direct negation/exclusion/polarity flip
        for s in supp_sents:
            norm_s = cls.normalize_text(s)
            s_tokens = [w for w in re.split(r'\W+', norm_s) if w]
            has_double_neg = any(re.search(pat, norm_s) for pat in cls.DOUBLE_NEGATION_PATTERNS)

            if has_double_neg and val_has_neg:
                return (
                    ValidationStatus.FAILED,
                    "Semantic Contradiction: Evidence asserts double-negation affirmative, but proposed claim is negative."
                )

            if has_double_neg and not val_has_neg:
                # Double negation acts affirmatively (e.g. 'cannot deny that X supports Python')
                continue

            for pat in cls.EXCEPTION_QUALIFIER_PATTERNS:
                for m in re.finditer(pat, norm_s):
                    ex_term = m.group(1).lower()
                    if any(w in ex_term for w in val_content) or any(re.search(r'\b' + re.escape(w), ex_term) for w in val_content):
                        return (
                            ValidationStatus.FAILED,
                            f"Semantic Contradiction: Exception or qualifier in evidence excludes '{ex_term}'."
                        )

            for pat in neg_patterns:
                for m in re.finditer(pat, norm_s):
                    action = m.group(1).lower()
                    if action not in {"the", "and", "for", "with", "from", "that", "this"}:
                        if re.search(r'\b' + re.escape(action), norm_val) or any(t.startswith(action) or action.startswith(t) for t in val_content):
                            # Audit 24: Predicate/Object alignment for transitive actions
                            if action in cls.TRANSITIVE_VERBS:
                                rem = norm_s[m.end(1):m.end(1)+80]
                                rem = re.split(r'[,;.!?]|\b(?:but|and|or|while|whereas|although)\b', rem)[0]
                                obj_words = [w for w in re.split(r'\W+', rem.lower()) if len(w) > 2 and w not in cls.STOP_WORDS]
                                if obj_words:
                                    distinct_obj = [w for w in obj_words if w not in cls.GENERIC_NOUNS]
                                    target_obj = distinct_obj if distinct_obj else obj_words
                                    distinct_val = [w for w in val_content if w not in cls.GENERIC_NOUNS and w != action and not w.startswith(action)]
                                    target_val = distinct_val if distinct_val else val_content
                                    if target_obj and not (set(target_obj) & set(target_val)):
                                        continue  # Negated verb acts on a different object/target
                            if not val_has_neg:
                                return (
                                    ValidationStatus.FAILED,
                                    f"Semantic Contradiction: Evidence explicitly negates or excludes '{action}' but proposed claim asserts it affirmatively."
                                )

            s_has_neg = any(w in cls.NEGATION_WORDS for w in s_tokens)
            if s_has_neg and not val_has_neg and not has_double_neg:
                s_content = cls.extract_content_words(norm_s)
                if val_content and set(val_content).issubset(set(s_content)):
                    return (
                        ValidationStatus.FAILED,
                        "Semantic Contradiction: Supporting sentence contains negation that is missing from proposed affirmative claim."
                    )

            if val_has_neg and not s_has_neg:
                return (
                    ValidationStatus.FAILED,
                    "Semantic Contradiction: Proposed claim introduces negation not established in affirmative evidence."
                )

        # 2. Check for conflicting source statements across other sentences in evidence
        for s in all_sents:
            if s not in supp_sents:
                norm_s = cls.normalize_text(s)
                s_tokens = [w for w in re.split(r'\W+', norm_s) if w]
                s_has_neg = any(w in cls.NEGATION_WORDS for w in s_tokens)
                if s_has_neg:
                    for pat in neg_patterns:
                        for m in re.finditer(pat, norm_s):
                            action = m.group(1).lower()
                            if action not in {"the", "and", "for", "with", "from", "that", "this"}:
                                if re.search(r'\b' + re.escape(action), norm_val) or any(t.startswith(action) or action.startswith(t) for t in val_content):
                                    # Audit 24: Predicate/Object alignment for transitive actions
                                    if action in cls.TRANSITIVE_VERBS:
                                        rem = norm_s[m.end(1):m.end(1)+80]
                                        rem = re.split(r'[,;.!?]|\b(?:but|and|or|while|whereas|although)\b', rem)[0]
                                        obj_words = [w for w in re.split(r'\W+', rem.lower()) if len(w) > 2 and w not in cls.STOP_WORDS]
                                        if obj_words:
                                            distinct_obj = [w for w in obj_words if w not in cls.GENERIC_NOUNS]
                                            target_obj = distinct_obj if distinct_obj else obj_words
                                            distinct_val = [w for w in val_content if w not in cls.GENERIC_NOUNS and w != action and not w.startswith(action)]
                                            target_val = distinct_val if distinct_val else val_content
                                            if target_obj and not (set(target_obj) & set(target_val)):
                                                continue  # Negated verb acts on a different object/target! Not a conflict!
                                    return (
                                        ValidationStatus.NEEDS_REVIEW,
                                        f"Conflicting Statements Violation: Another sentence in evidence negates or qualifies '{action}'. Requires manual review."
                                    )

                # Audit 24: Check conflicting polarity/state claims on the same topic/entity
                s_content = set(cls.extract_content_words(norm_s))
                shared_topics = s_content & set(val_content)
                if shared_topics:
                    for set_a, set_b in cls.CONFLICTING_STATES:
                        if (any(w in val_content for w in set_a) and any(w in s_content for w in set_b)) or \
                           (any(w in val_content for w in set_b) and any(w in s_content for w in set_a)):
                            return (
                                ValidationStatus.NEEDS_REVIEW,
                                "Conflicting Statements Violation: Evidence contains contradictory assertions about the same entity or feature. Requires manual review."
                            )

        return None

    @classmethod
    def check_modality_tense_shift(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Detects changes in modality or tense, such as treating an unfulfilled plan or intent
        as an accomplished fact.
        e.g., Evidence: 'We plan to develop a medical AI platform.'
        vs Proposed: 'We have developed a medical AI platform.'
        """
        ev_has_plan = any(re.search(r'\b' + re.escape(w) + r'\b', norm_ev) for w in cls.PLAN_MODALITY_WORDS)
        val_has_accomplished = any(re.search(r'\b' + re.escape(w) + r'\b', norm_val) for w in cls.ACCOMPLISHED_MODALITY_WORDS)
        val_has_plan = any(re.search(r'\b' + re.escape(w) + r'\b', norm_val) for w in cls.PLAN_MODALITY_WORDS)

        if ev_has_plan and val_has_accomplished and not val_has_plan:
            return (
                ValidationStatus.FAILED,
                "Modality Shift Violation: Evidence expresses a plan, intent, or roadmap goal, but proposed claim asserts accomplished past or present reality."
            )
        return None

    @classmethod
    def check_attribution_and_causal_claims(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Detects unsupported attribution upgrades or unhedged causal claims.
        e.g., Evidence: 'The company reports that its product supports hospitals.'
        vs Proposed: 'The product is independently proven to improve hospital outcomes.'
        """
        val_has_proven = any(re.search(r'\b' + re.escape(w) + r'\b', norm_val) for w in cls.PROVEN_CAUSAL_WORDS)
        ev_has_proven = any(re.search(r'\b' + re.escape(w) + r'\b', norm_ev) for w in cls.PROVEN_CAUSAL_WORDS)

        ev_has_tentative = any(re.search(r'\b' + re.escape(w) + r'\b', norm_ev) for w in cls.TENTATIVE_ATTRIBUTION_WORDS)

        if val_has_proven and not ev_has_proven:
            return (
                ValidationStatus.FAILED,
                "Attribution / Causality Violation: Proposed text claims independent proof, guarantee, or conclusive causality not established in evidence."
            )

        if ev_has_tentative and ("improve hospital outcomes" in norm_val or "proven" in norm_val):
            return (
                ValidationStatus.FAILED,
                "Attribution Violation: Evidence contains self-reported or tentative statements, but proposed text claims verified or improved outcomes."
            )

        return None

    @classmethod
    def check_quantifier_shift(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Detects unearned quantifier inflation (e.g. 'some of our products' -> 'all of our products').
        Audit 22 Requirement 2.
        """
        ev_has_partial = any(re.search(r'\b' + re.escape(w) + r'\b', norm_ev) for w in cls.PARTIAL_QUANTIFIERS)
        val_has_universal = any(re.search(r'\b' + re.escape(w) + r'\b', norm_val) for w in cls.UNIVERSAL_QUANTIFIERS)
        ev_has_universal = any(re.search(r'\b' + re.escape(w) + r'\b', norm_ev) for w in cls.UNIVERSAL_QUANTIFIERS)

        if ev_has_partial and val_has_universal and not ev_has_universal:
            return (
                ValidationStatus.FAILED,
                "Quantifier Shift Violation: Evidence indicates partial or selective scope ('some'/'select'), but proposed claim asserts universal scope ('all'/'every')."
            )
        return None

    @classmethod
    def check_magnitude_inflation(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Detects ungrounded multiplier or magnitude inflation (e.g. 'improved performance' -> 'doubled performance').
        Audit 22 Requirement 2.
        """
        val_multipliers = [w for w in cls.METRIC_MULTIPLIERS if re.search(r'\b' + re.escape(w) + r'\b', norm_val)]
        for mult in val_multipliers:
            if not re.search(r'\b' + re.escape(mult) + r'\b', norm_ev):
                return (
                    ValidationStatus.FAILED,
                    f"Magnitude Inflation Violation: Proposed text introduces unverified metric multiplier '{mult}' not substantiated in evidence."
                )
        return None

    @classmethod
    def check_conditional_vs_factual(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Detects unhedged factual assertions made from conditional evidence with sentence-level context isolation.
        (e.g. 'If customers provide labeled data, our pipeline can train models' -> 'Our pipeline trains models').
        Audit 22 & Audit 23 Requirement 3.
        """
        sents = cls.split_into_sentences(norm_ev)
        supp_sents, all_sents = cls.find_relevant_sentences(norm_val, sents)
        val_has_cond = any(re.search(r'\b' + re.escape(w) + r'\b', norm_val) for w in cls.CONDITIONAL_MARKERS)

        for s in supp_sents:
            norm_s = cls.normalize_text(s)
            s_has_cond = any(re.search(r'\b' + re.escape(w) + r'\b', norm_s) for w in cls.CONDITIONAL_MARKERS)
            if s_has_cond and not val_has_cond:
                return (
                    ValidationStatus.FAILED,
                    "Conditionality Shift Violation: Evidence establishes a conditional or hypothetical claim, but proposed claim asserts an unconditional factual outcome."
                )
        return None

    @classmethod
    def check_historical_vs_current(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Detects temporal status shifts with sentence-level context isolation.
        (e.g. 'The company previously operated an ad network' -> 'The company currently operates an ad network').
        Audit 22 & Audit 23 Requirement 3.
        """
        sents = cls.split_into_sentences(norm_ev)
        supp_sents, all_sents = cls.find_relevant_sentences(norm_val, sents)
        val_has_current = any(re.search(r'\b' + re.escape(w) + r'\b', norm_val) for w in cls.CURRENT_STATUS_WORDS)
        val_has_hist = any(re.search(r'\b' + re.escape(w) + r'\b', norm_val) for w in cls.HISTORICAL_STATUS_WORDS)

        for s in supp_sents:
            norm_s = cls.normalize_text(s)
            s_has_hist = any(re.search(r'\b' + re.escape(w) + r'\b', norm_s) for w in cls.HISTORICAL_STATUS_WORDS)
            s_has_current = any(re.search(r'\b' + re.escape(w) + r'\b', norm_s) for w in cls.CURRENT_STATUS_WORDS)

            if s_has_hist and not s_has_current:
                if val_has_current or not val_has_hist:
                    return (
                        ValidationStatus.FAILED,
                        "Temporal Status Shift Violation: Evidence describes a historical or former status, but proposed claim asserts a current ongoing status."
                    )
        return None

    @classmethod
    def check_subject_object_reversal(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Detects subject/object reversals and active/passive semantic inversions.
        e.g., 'Google acquired DeepMind' vs 'DeepMind acquired Google'
        e.g., 'Researchers evaluated the AI system' vs 'The AI system evaluated the researchers'
        Audit 22 Requirement 2.
        """
        verbs = ["acquired", "bought", "evaluated", "trained", "developed", "tested", "monitored", "managed", "built", "purchased", "funded"]
        for verb in verbs:
            ev_match = re.search(r'([a-z0-9_\-\s]{2,25})\s+' + re.escape(verb) + r'\s+([a-z0-9_\-\s]{2,25})', norm_ev)
            val_match = re.search(r'([a-z0-9_\-\s]{2,25})\s+' + re.escape(verb) + r'\s+([a-z0-9_\-\s]{2,25})', norm_val)
            if ev_match and val_match:
                ev_subj, ev_obj = ev_match.group(1).strip(), ev_match.group(2).strip()
                val_subj, val_obj = val_match.group(1).strip(), val_match.group(2).strip()
                if (ev_subj in val_obj or val_obj in ev_subj) and (ev_obj in val_subj or val_subj in ev_obj):
                    if ev_subj != ev_obj:
                        return (
                            ValidationStatus.FAILED,
                            f"Subject/Object Reversal Violation: Semantic roles reversed around action '{verb}'. Evidence states '{ev_subj} {verb} {ev_obj}' but proposed asserts '{val_subj} {verb} {val_obj}'."
                        )

            # Passive voice reversal: "X was VERBed by Y" vs "X VERBed Y"
            passive_pat = r'([a-z0-9_\-\s]{2,25})\s+was\s+' + re.escape(verb) + r'\s+by\s+([a-z0-9_\-\s]{2,25})'
            pass_ev = re.search(passive_pat, norm_ev)
            if pass_ev and val_match:
                patient, agent = pass_ev.group(1).strip(), pass_ev.group(2).strip()
                val_subj, val_obj = val_match.group(1).strip(), val_match.group(2).strip()
                if (patient in val_subj or val_subj in patient) and (agent in val_obj or val_obj in agent):
                    return (
                        ValidationStatus.FAILED,
                        f"Active/Passive Voice Reversal Violation: Semantic roles reversed around '{verb}'. Evidence: '{patient} was {verb} by {agent}', proposed: '{val_subj} {verb} {val_obj}'."
                    )
        return None

    @classmethod
    def check_unsupported_causation(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Detects unsubstantiated causal claims inferred from co-occurring events.
        e.g., Evidence: 'The company released an AI assistant and revenues grew.'
        vs Proposed: 'The AI assistant caused revenues to grow.'
        Audit 22 Requirement 2.
        """
        val_has_causal = any(re.search(r'\b' + re.escape(w) + r'\b', norm_val) for w in cls.CAUSAL_CONNECTIVES)
        ev_has_causal = any(re.search(r'\b' + re.escape(w) + r'\b', norm_ev) for w in cls.CAUSAL_CONNECTIVES)

        if val_has_causal and not ev_has_causal:
            return (
                ValidationStatus.FAILED,
                "Unsupported Causal Claim: Proposed text asserts a direct causal relationship ('caused'/'resulted in') not established in evidence."
            )
        return None

    @classmethod
    def check_context_and_attribution_qualification(cls, norm_val: str, norm_ev: str) -> Optional[Tuple[ValidationStatus, str]]:
        """
        Audit 25 Priority 2: Extractive context and attribution qualifier integrity.
        Ensures that substring extraction does not strip attribution, reporting verbs,
        conditionality, limited scope, manual approval gates, or future intent qualifiers.
        """
        if norm_val not in norm_ev:
            return None

        idx = norm_ev.find(norm_val)
        sent_start = 0
        for m in re.finditer(r'[.!?\n]+', norm_ev[:idx]):
            sent_start = m.end()
        sent_end = len(norm_ev)
        m = re.search(r'[.!?\n]+', norm_ev[idx + len(norm_val):])
        if m:
            sent_end = idx + len(norm_val) + m.start()

        preceding = norm_ev[sent_start:idx].strip()
        succeeding = norm_ev[idx + len(norm_val):sent_end].strip()
        surrounding = (preceding + " " + succeeding).strip()

        all_qualifiers = cls.ATTRIBUTION_QUALIFIERS + cls.LIMITATION_QUALIFIERS + cls.INTENT_QUALIFIERS
        for pat in all_qualifiers:
            m_surr = re.search(pat, surrounding, re.IGNORECASE)
            if m_surr:
                # Check if norm_val already contains this qualifier
                m_val = re.search(pat, norm_val, re.IGNORECASE)
                if not m_val:
                    return (
                        ValidationStatus.NEEDS_REVIEW,
                        f"Context/Attribution Qualification: Claim omits critical attribution, limitation, or intent qualifier ('{m_surr.group(0)}') from source excerpt."
                    )
        return None

    @classmethod
    def validate_classification(
        cls,
        proposed_class: str,
        norm_ev: str,
        is_heuristic: bool = False,
        entity_type: Optional[str] = None,
        field_name: Optional[str] = None
    ) -> Tuple[ValidationStatus, str]:
        """
        Validates classification outputs against Approved Taxonomy and Version 2.0.0 mapping rules.
        """
        if not proposed_class or not proposed_class.strip():
            return ValidationStatus.INSUFFICIENT_EVIDENCE, "No classification value provided."

        # 1. Enforce Approved Taxonomy
        if not is_approved_category(entity_type, field_name, proposed_class):
            return (
                ValidationStatus.FAILED,
                f"Taxonomy Violation: Classification '{proposed_class}' is outside the approved taxonomy for {entity_type or 'entity'}.{field_name or 'classification'}. Unknown categories must never be verified."
            )

        # 2. Check compound concept rules if applicable
        target_rule = None
        for rule_name, concepts in COMPOUND_CLASSIFICATION_CONCEPTS.items():
            if rule_name.lower() == proposed_class.strip().lower():
                target_rule = concepts
                break

        if target_rule:
            supported_concepts = []
            unsupported_concepts = []

            for concept_def in target_rule:
                c_name = concept_def["concept"]
                kws = concept_def["keywords"]
                concept_found = False
                for kw in kws:
                    escaped_kw = re.escape(kw)
                    pattern = r'\b' + escaped_kw + r's?\b'
                    if re.search(pattern, norm_ev):
                        concept_found = True
                        break
                
                if concept_found:
                    supported_concepts.append(c_name)
                else:
                    unsupported_concepts.append(c_name)

            if not supported_concepts:
                return (
                    ValidationStatus.FAILED,
                    f"Evidence does not support classification '{proposed_class}'. None of the required concepts ({unsupported_concepts}) appear in evidence."
                )

            if unsupported_concepts:
                return (
                    ValidationStatus.NEEDS_REVIEW,
                    f"Classification '{proposed_class}' adds concepts not established by evidence: {unsupported_concepts}. Supported: {supported_concepts}."
                )

        else:
            norm_class = cls.normalize_text(proposed_class)
            class_words = [w for w in re.split(r'\W+', norm_class) if len(w) > 3]
            matched_words = [w for w in class_words if w in norm_ev]

            if not matched_words and norm_class not in norm_ev:
                return (
                    ValidationStatus.FAILED,
                    f"Classification '{proposed_class}' is unsupported by the evidence excerpt."
                )
            if len(matched_words) < len(class_words):
                return (
                    ValidationStatus.NEEDS_REVIEW,
                    f"Classification '{proposed_class}' is only partially grounded in evidence."
                )

        # Heuristic classification safeguard (Rule 8)
        if is_heuristic:
            return (
                ValidationStatus.NEEDS_REVIEW,
                f"Heuristic classification '{proposed_class}' requires review (rule 8)."
            )

        return ValidationStatus.VERIFIED, f"Classification '{proposed_class}' fully supported by evidence."

    @classmethod
    def validate_free_text_claims(
        cls,
        val: str,
        norm_ev: str,
        confidence_score: float,
        is_heuristic: bool
    ) -> Tuple[ValidationStatus, str]:
        """
        Audit 22: Deep semantic adversarial claim validation.
        - Checks for negation contradictions, modality/tense shifts, dates/numbers, and causal attribution.
        - Checks quantifier shifts (some vs all), magnitude inflation (improved vs doubled),
          conditionality shifts (conditional vs factual), temporal status shifts (historical vs current),
          active/passive voice reversals, and subject/object reversals.
        - Global Invariant: A claim that cannot be conclusively validated must be NEEDS_REVIEW, never VERIFIED.
        """
        norm_val = cls.normalize_text(val)
        if not norm_val:
            return ValidationStatus.INSUFFICIENT_EVIDENCE, "Empty text value provided."

        # 1. Semantic Check: Numbers and Dates
        num_err = cls.check_numbers_and_dates(norm_val, norm_ev)
        if num_err:
            return num_err

        # 2. Semantic Check: Negation and Contradiction (without, neither, lack, exclude)
        neg_err = cls.check_negation_contradiction(norm_val, norm_ev)
        if neg_err:
            return neg_err

        # 3. Semantic Check: Modality and Tense Shift
        mod_err = cls.check_modality_tense_shift(norm_val, norm_ev)
        if mod_err:
            return mod_err

        # 4. Semantic Check: Attribution and Causal Claims
        attr_err = cls.check_attribution_and_causal_claims(norm_val, norm_ev)
        if attr_err:
            return attr_err

        # 5. Semantic Check: Quantifier Shift (Some vs All) - Audit 22
        quant_err = cls.check_quantifier_shift(norm_val, norm_ev)
        if quant_err:
            return quant_err

        # 6. Semantic Check: Magnitude Inflation (Improved vs Doubled) - Audit 22
        mag_err = cls.check_magnitude_inflation(norm_val, norm_ev)
        if mag_err:
            return mag_err

        # 7. Semantic Check: Conditionality Shift (Conditional vs Factual) - Audit 22
        cond_err = cls.check_conditional_vs_factual(norm_val, norm_ev)
        if cond_err:
            return cond_err

        # 8. Semantic Check: Temporal Status Shift (Historical vs Current) - Audit 22
        temp_err = cls.check_historical_vs_current(norm_val, norm_ev)
        if temp_err:
            return temp_err

        # 9. Semantic Check: Subject/Object Reversal & Active/Passive Voice - Audit 22
        rev_err = cls.check_subject_object_reversal(norm_val, norm_ev)
        if rev_err:
            return rev_err

        # 10. Semantic Check: Unsupported Causal Claims - Audit 22
        caus_err = cls.check_unsupported_causation(norm_val, norm_ev)
        if caus_err:
            return caus_err

        # Case 1: Exact Extractive Grounding (substring of evidence excerpt)
        if norm_val in norm_ev:
            # Context check: verify extracted substring was not immediately preceded by a negation in evidence
            idx = norm_ev.find(norm_val)
            if idx > 0:
                preceding_snippet = norm_ev[max(0, idx - 30):idx]
                if re.search(r'\b(?:do\s+not|does\s+not|did\s+not|not|never|cannot|no|without|neither|nor|lack|lacks|exclude|excludes)\s*$', preceding_snippet):
                    return (
                        ValidationStatus.FAILED,
                        "Semantic Contradiction: Extracted substring was preceded by a negation or exclusion in evidence, reversing source meaning."
                    )
                if re.search(r'\b(?:if|unless|provided\s+that|assuming|whether)\s*$', preceding_snippet):
                    return (
                        ValidationStatus.FAILED,
                        "Conditionality Truncation: Extracted substring was preceded by a conditional marker in evidence, dropping required conditions."
                    )

            # Audit 25 Priority 2: Check for stripped attribution, limitation, manual approval, or intent context
            ctx_err = cls.check_context_and_attribution_qualification(norm_val, norm_ev)
            if ctx_err:
                return ctx_err

            if is_heuristic:
                return ValidationStatus.NEEDS_REVIEW, "Heuristic text extraction requires review."
            if confidence_score >= 0.75:
                return ValidationStatus.VERIFIED, "Text value is an exact extractive substring of verbatim evidence preserving meaning and context."
            return ValidationStatus.NEEDS_REVIEW, f"Extractive text grounded, but confidence ({confidence_score:.2f}) requires review."

        # Case 2: Multi-sentence / Paraphrased text validation
        # Audit 22: Mere word presence is strictly insufficient for semantic entailment.
        # Paraphrased or non-extractive claims must be routed to manual review (NEVER VERIFIED).
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', val) if len(s.strip()) > 5]
        if not sentences:
            sentences = [val.strip()]

        unsupported_claims = []
        for sent in sentences:
            norm_sent = cls.normalize_text(sent)
            stop_words = {
                "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with",
                "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                "do", "does", "did", "our", "their", "this", "that", "these", "those", "we", "they"
            }
            words = [w for w in re.split(r'\W+', norm_sent) if len(w) > 2 and w not in stop_words]
            if words:
                missing_words = [w for w in words if not re.search(r'\b' + re.escape(w) + r'\b', norm_ev)]
                if missing_words:
                    unsupported_claims.append((sent, missing_words))

        if unsupported_claims:
            return (
                ValidationStatus.NEEDS_REVIEW,
                f"Free-text value contains unsupported claims or fabricated entities: {unsupported_claims}."
            )

        return (
            ValidationStatus.NEEDS_REVIEW,
            "Paraphrased or non-extractive text requires manual review. Word presence alone does not establish semantic entailment (Audit 22 Requirement 2)."
        )

    @classmethod
    def validate_enrichment(
        cls,
        result: EnrichmentResult,
        source_text: str,
        canonical_record: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ValidationStatus, str]:
        """
        Validates an enrichment result against strict field-level anti-hallucination rules.
        Returns (ValidationStatus, rationale_message).
        """
        field_lower = result.field_name.lower()

        # 1. Forbidden Inferences (Rule 3)
        if field_lower in FORBIDDEN_INFERENCE_FIELDS:
            return (
                ValidationStatus.FAILED,
                f"Rule 3 Violation: Field '{result.field_name}' is strictly forbidden from LLM inference."
            )

        # 2. Canonical Job Protection
        if result.entity_type == "job" and field_lower in PROTECTED_JOB_FIELDS:
            return (
                ValidationStatus.FAILED,
                f"Job Protection Violation: Verified canonical field '{result.field_name}' must not be modified."
            )

        # 3. Retain 15 Boundary Job Classifications
        if result.entity_type == "job" and result.record_id in RETAINED_15_REVIEW_JOB_IDS:
            if field_lower in ["category", "classification_reason", "classification_status"]:
                return (
                    ValidationStatus.NEEDS_REVIEW,
                    f"Boundary Preservation: Record '{result.record_id}' is one of the 15 Stage 2 audited boundary jobs and must remain REQUIRES_REVIEW."
                )

        # 4. News Content Requirement: Check both 'article_summary' and 'summary'
        if result.entity_type == "news" and field_lower in ("article_summary", "summary"):
            if not source_text or len(source_text.strip()) < 50:
                return (
                    ValidationStatus.INSUFFICIENT_EVIDENCE,
                    "News Rule Violation: Cannot generate an article summary from a headline alone or without access to sufficient source text (>= 50 chars)."
                )

        # 5. Check if enriched value is empty/null
        val = result.enriched_value
        if val is None or val == "" or val == [] or val == {}:
            return (
                ValidationStatus.INSUFFICIENT_EVIDENCE,
                "No enriched value was extracted."
            )

        # 6. Supporting evidence requirement (Rule 5)
        if not result.evidence or not result.evidence.strip():
            return (
                ValidationStatus.FAILED,
                "Rule 5 Violation: No supporting evidence excerpt provided for enriched value."
            )

        # Disallow application-generated context label prefixes or label-plus-value quotations (Audit 28)
        has_lbl, lbl_name = cls.has_application_label_prefix(result.evidence)
        if has_lbl:
            return (
                ValidationStatus.FAILED,
                f"Rule 2 Violation: Application-generated context label prefix ('{lbl_name}') cannot qualify as an original source quotation."
            )

        eq = getattr(result, "evidence_quote", None)
        if eq and isinstance(eq, str):
            has_eq_lbl, eq_lbl_name = cls.has_application_label_prefix(eq)
            if has_eq_lbl:
                return (
                    ValidationStatus.FAILED,
                    f"Rule 2 Violation: Application-generated context label prefix ('{eq_lbl_name}') cannot qualify as an original source quotation."
                )

        norm_ev_raw = cls.normalize_text(result.evidence)
        if norm_ev_raw in cls.APPLICATION_LABELS:
            return (
                ValidationStatus.FAILED,
                "Rule 2 Violation: Application-generated context label cannot qualify as an original source quotation."
            )

        # Extract raw stored source content from canonical record independently from labels (Audit 28)
        raw_source_content = None
        if canonical_record:
            from core.enrichment.engine import EnrichmentEngine
            raw_source_content = EnrichmentEngine.get_canonical_raw_content(result.entity_type, canonical_record)
            if not raw_source_content:
                raw_values = [str(v) for k, v in canonical_record.items() if v and isinstance(v, (str, int, float))]
                raw_source_content = "\n".join(raw_values)

        # 6b. Existing Canonical Data Duplication Safeguard (Audit 27 & 28)
        if canonical_record:
            if result.entity_type == "startup":
                if field_lower in ("ai_specialization", "ai_focus_area"):
                    existing_focus = canonical_record.get("ai_focus_area")
                    if existing_focus and cls.normalize_text(str(val)) == cls.normalize_text(str(existing_focus)):
                        return (
                            ValidationStatus.NEEDS_REVIEW,
                            f"Duplication Safeguard: Proposed value '{val}' duplicates existing ai_focus_area ('{existing_focus}'). No new enrichment achieved."
                        )
                elif field_lower == "technologies" and isinstance(val, list):
                    existing_ev = canonical_record.get("ai_evidence", "")
                    if existing_ev:
                        norm_ev_field = cls.normalize_text(str(existing_ev))
                        if all(cls.normalize_text(str(item)) in norm_ev_field for item in val if item):
                            return (
                                ValidationStatus.NEEDS_REVIEW,
                                f"Duplication Safeguard: All proposed technologies {val} already exist in canonical ai_evidence. No new enrichment achieved."
                            )

        # 7. Exact Verbatim Excerpt Grounding against underlying content (Rule 2)
        if not cls.is_verbatim_excerpt(result.evidence, source_text, raw_source_content=raw_source_content):
            return (
                ValidationStatus.FAILED,
                "Rule 2 Violation: Provided evidence could not be traced as a verbatim excerpt of the source text."
            )

        norm_ev = cls.normalize_text(result.evidence)
        is_heuristic = "heuristic" in result.enrichment_method.lower() or result.provider.lower() in ("offline", "heuristic")

        # 8. Field-Level Value vs. Evidence Validation

        # Case A: List fields (validate every individual item + heuristic safeguard + negation check)
        if isinstance(val, list):
            if not val:
                return (
                    ValidationStatus.INSUFFICIENT_EVIDENCE,
                    "List field contains no extracted items."
                )

            supported_items = []
            unsupported_items = []
            negated_items = []

            for item in val:
                item_str = str(item).strip()
                if not item_str:
                    continue
                norm_item = cls.normalize_text(item_str)
                # Check negation / exclusion around item in evidence (Audit 21 & 22)
                escaped_item = re.escape(norm_item)
                neg_patterns = [
                    r'\b(?:do\s+not|does\s+not|did\s+not|not|never|without|no|neither|nor|lack|lacks|exclude|excludes|excluding|free\s+of)\s+(?:use\s+|require\s+|need\s+|having\s+)?' + escaped_item + r'\b',
                    r'\b' + escaped_item + r'\s+(?:is\s+not|not\s+used|not\s+required|is\s+excluded|is\s+lacking)\b',
                    r'\b(?:neither\s+' + escaped_item + r'|\bnor\s+' + escaped_item + r')\b'
                ]
                is_negated = any(re.search(pat, norm_ev) for pat in neg_patterns)
                if is_negated:
                    negated_items.append(item_str)
                    continue

                if cls.check_item_supported_in_evidence(item_str, norm_ev):
                    supported_items.append(item_str)
                else:
                    unsupported_items.append(item_str)

            if negated_items:
                return (
                    ValidationStatus.FAILED,
                    f"List Negation Violation: Evidence explicitly negates or excludes items: {negated_items}."
                )

            if not supported_items:
                return (
                    ValidationStatus.FAILED,
                    f"Evidence does not support any items in list. Unsupported items: {unsupported_items}."
                )

            if unsupported_items:
                return (
                    ValidationStatus.NEEDS_REVIEW,
                    f"Partially supported list: {len(supported_items)}/{len(val)} items supported. Unsupported items: {unsupported_items}."
                )

            # Heuristic-provider safeguard (Audit 21 Requirement 3)
            # A heuristic list must NOT automatically become VERIFIED!
            if is_heuristic:
                return (
                    ValidationStatus.NEEDS_REVIEW,
                    f"Heuristic list extraction requires review (rule 8 safeguard). All {len(supported_items)} items grounded in text, but contextual necessity requires human verification."
                )

            if result.confidence_score < 0.70:
                return (
                    ValidationStatus.NEEDS_REVIEW,
                    f"All items supported by evidence, but confidence ({result.confidence_score:.2f}) is below verification threshold."
                )

            return (
                ValidationStatus.VERIFIED,
                f"All {len(supported_items)} list items are directly substantiated by verbatim evidence."
            )

        # Case B: Classification fields (Audit 21: enforce approved taxonomy)
        classification_fields = {
            "ai_specialization", "industry", "product_category", "research_domain",
            "news_category", "role_specialization", "category"
        }
        if field_lower in classification_fields and isinstance(val, str):
            status, rationale = cls.validate_classification(
                proposed_class=val,
                norm_ev=norm_ev,
                is_heuristic=is_heuristic,
                entity_type=result.entity_type,
                field_name=result.field_name
            )
            return status, rationale

        # Case C: Free-text descriptions / summaries (Audit 22: deep semantic adversarial validation)
        if isinstance(val, str):
            status, rationale = cls.validate_free_text_claims(
                val=val,
                norm_ev=norm_ev,
                confidence_score=result.confidence_score,
                is_heuristic=is_heuristic
            )
            return status, rationale

        return (
            ValidationStatus.NEEDS_REVIEW,
            f"Field '{result.field_name}' requires manual review."
        )
