"""
Deterministic Heuristic Offline Provider for air-gapped, credential-free enrichment.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 20 - Heuristic Pilot Attribution, Calibrated Confidence, Zero Token Reporting
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
import jsonschema

from core.llm.base import BaseLLMProvider, ProviderConfig, LLMResponse, TokenUsage
from core.llm.schema_validator import validate_json_schema
from core.enrichment.schemas import CLASSIFICATION_RULES

logger = logging.getLogger("OfflineProvider")

# Domain keyword ontologies for grounded extraction
# Each tech has its display name and specific contextual regex to avoid common-word false positives
TECH_ONTOLOGY: List[Dict[str, Any]] = [
    {"name": "Python", "pattern": r'\bpython\b', "case_sensitive": False},
    {"name": "PyTorch", "pattern": r'\bpytorch\b', "case_sensitive": False},
    {"name": "TensorFlow", "pattern": r'\btensorflow\b', "case_sensitive": False},
    {"name": "CUDA", "pattern": r'\bcuda\b', "case_sensitive": False},
    {"name": "Kubernetes", "pattern": r'\b(?:kubernetes|k8s)\b', "case_sensitive": False},
    {"name": "Docker", "pattern": r'\bdocker\b', "case_sensitive": False},
    {"name": "SQL", "pattern": r'\bsql\b', "case_sensitive": False},
    # Context-constrained matching for ambiguous terms
    {"name": "Spark", "pattern": r'\b(?:apache spark|pyspark|spark)\b(?=.*(?:cluster|data|big data|pipeline|hadoop|sql))', "case_sensitive": False},
    {"name": "LLMs", "pattern": r'\b(?:llm|llms|large language models?)\b', "case_sensitive": False},
    {"name": "RAG", "pattern": r'\b(?:rag|retrieval[- ]augmented generation)\b', "case_sensitive": False},
    {"name": "LangChain", "pattern": r'\blangchain\b', "case_sensitive": False},
    {"name": "Hugging Face", "pattern": r'\bhugging\s*face\b', "case_sensitive": False},
    {"name": "AWS", "pattern": r'\baws\b|\bamazon web services\b', "case_sensitive": False},
    {"name": "GCP", "pattern": r'\bgcp\b|\bgoogle cloud\b', "case_sensitive": False},
    {"name": "Azure", "pattern": r'\bazure\b|\bmicrosoft azure\b', "case_sensitive": False},
    # C++ and C require strict distinction from plain words
    {"name": "C++", "pattern": r'(?:\b|(?<=/))c\+\+(?=[^\w+]|\Z)', "case_sensitive": False},
    {"name": "C", "pattern": r'\b(?:c\s*language|c\/c\+\+|c\s*and\s*c\+\+)\b', "case_sensitive": False},
    # Go programming language: never match 'we go to' or 'on the go'
    {"name": "Go", "pattern": r'\b(?:golang|go language|(?:python|c\+\+|rust|java),\s*go\b|\bgo,\s*(?:python|c\+\+|rust|java))\b', "case_sensitive": False},
    # Rust programming language: never match 'rust patina' or non-code
    {"name": "Rust", "pattern": r'\b(?:rust language|rust programming|rust,\s*(?:c\+\+|python|go))\b|\bRust\b', "case_sensitive": True},
    # R language: never match single letter 'r'
    {"name": "R", "pattern": r'\b(?:r\s*language|r\s*programming|r\s*statistical|r\/python|python\/r)\b', "case_sensitive": False},
    {"name": "Ray", "pattern": r'\bray\b(?=.*(?:distributed|cluster|train|serve|tune))', "case_sensitive": False},
    {"name": "Triton", "pattern": r'\btriton\b(?=.*(?:kernel|compiler|inference|gpu|server))', "case_sensitive": False},
    {"name": "JAX", "pattern": r'\bjax\b', "case_sensitive": True},
    {"name": "vLLM", "pattern": r'\bvllm\b', "case_sensitive": False},
    {"name": "Transformers", "pattern": r'\btransformers\b', "case_sensitive": False},
    # Git: distinguish from ordinary words
    {"name": "Git", "pattern": r'\b(?:git|github|gitlab|git flow)\b', "case_sensitive": False},
    {"name": "Linux", "pattern": r'\blinux\b', "case_sensitive": False},
    # FastAPI: must not match 'fast-paced' or 'fast'
    {"name": "FastAPI", "pattern": r'\bfastapi\b', "case_sensitive": False},
    {"name": "Pandas", "pattern": r'\bpandas\b', "case_sensitive": False},
    {"name": "Scikit-Learn", "pattern": r'\b(?:scikit-learn|sklearn)\b', "case_sensitive": False},
    {"name": "OpenCV", "pattern": r'\bopencv\b', "case_sensitive": False},
    {"name": "TypeScript", "pattern": r'\btypescript\b', "case_sensitive": False},
    {"name": "React", "pattern": r'\breact\b|\breact\.js\b', "case_sensitive": False},
    {"name": "Node.js", "pattern": r'\bnode\.?js\b', "case_sensitive": False},
    {"name": "Java", "pattern": r'\bjava\b(?!script)', "case_sensitive": False},
    {"name": "GraphQL", "pattern": r'\bgraphql\b', "case_sensitive": False}
]


class OfflineProvider(BaseLLMProvider):
    """
    Deterministic rule-based heuristic provider.
    Accurately identified as a heuristic extractor and classifier (not an LLM).
    Extracts terms only when explicitly present in source text and selects exact sentence evidence.
    Calibrated confidence: 0.70-0.80 (never unearned 0.95).
    Audit 20: Reports zero prompt, completion, and total tokens ($0.00 cost) so heuristic
    word counts are not conflated with genuine LLM token consumption.
    """
    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            config = ProviderConfig(
                provider_name="offline",
                model_name="heuristic-keyword-v1",
                rate_limit_rpm=None
            )
        else:
            config.rate_limit_rpm = None
            if not config.model_name or config.model_name == "heuristic-grounded-v1":
                config.model_name = "heuristic-keyword-v1"
        super().__init__(config)

    def is_available(self) -> bool:
        return True

    def _split_into_sentences(self, text: str) -> List[str]:
        """Splits text into substantive sentences for exact sentence evidence extraction."""
        raw_sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
        sentences = []
        for s in raw_sentences:
            cleaned = re.sub(
                r'^(?:Company Name|Product Name|AI Focus|Existing Description|Features|Title|Job Title|Company|Article Content|Description|Evidence):\s*',
                '',
                s.strip(),
                flags=re.IGNORECASE
            ).strip()
            if len(cleaned) > 15:
                sentences.append(cleaned)
        return sentences

    def _find_evidence_sentence_for_terms(self, terms: List[str], sentences: List[str], full_text: str) -> str:
        """Finds the most representative sentence or contiguous span containing the extracted terms."""
        if not terms or not sentences:
            return sentences[0] if sentences else full_text[:200].strip()

        # Score sentences by number of extracted terms found
        best_sentence = ""
        max_matches = 0

        for sentence in sentences:
            s_lower = sentence.lower()
            matches = sum(1 for term in terms if term.lower() in s_lower)
            if matches > max_matches:
                max_matches = matches
                best_sentence = sentence

        # If a single sentence matched all terms or at least some
        if best_sentence and max_matches >= min(2, len(terms)):
            return best_sentence

        # Check adjacent pairs of sentences in full_text
        for i in range(len(sentences) - 1):
            s1 = sentences[i]
            s2 = sentences[i + 1]
            comb_lower = (s1 + " " + s2).lower()
            matches = sum(1 for term in terms if term.lower() in comb_lower)
            if matches > max_matches:
                idx1 = full_text.find(s1)
                idx2 = full_text.find(s2)
                if idx1 != -1 and idx2 != -1 and idx2 > idx1 and (idx2 - (idx1 + len(s1))) < 20:
                    span = full_text[idx1:idx2 + len(s2)].strip()
                    max_matches = matches
                    best_sentence = span

        if best_sentence:
            return best_sentence

        # Fallback to first substantive sentence
        if sentences:
            return sentences[0]
        cleaned_text = re.sub(
            r'^(?:Company Name|Product Name|AI Focus|Existing Description|Features|Title|Job Title|Company|Article Content|Description|Evidence):\s*',
            '',
            full_text.strip(),
            flags=re.IGNORECASE
        ).strip()
        return cleaned_text[:200].strip()

    def _execute_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        # Audit 20: Offline heuristic provider reports exactly 0 tokens and $0.00 cost
        prompt_tokens = 0
        completion_tokens = 0

        # Parse source text from prompt
        source_text = ""
        source_match = re.search(
            r'(?:Source Content|Context|Description|Text|Job Description|Article Content):\s*["\']?(.*?)(?:["\']?\s*\n\n|\Z)',
            prompt,
            re.DOTALL | re.IGNORECASE
        )
        if source_match:
            source_text = source_match.group(1).strip()
        else:
            source_text = prompt.strip()

        sentences = self._split_into_sentences(source_text)

        # 1. Deterministic Technology / Skill extraction
        found_techs: List[str] = []
        matched_terms: List[str] = []
        for tech_def in TECH_ONTOLOGY:
            name = tech_def["name"]
            pat = tech_def["pattern"]
            case_sens = tech_def.get("case_sensitive", False)
            flags = 0 if case_sens else re.IGNORECASE
            match = re.search(pat, source_text, flags)
            if match:
                found_techs.append(name)
                matched_terms.append(match.group(0))

        # 2. Heuristic Classification using CLASSIFICATION_RULES (Audit 20: requires all constituent concepts)
        ai_spec: Optional[str] = None
        source_lower = source_text.lower()
        classification_confidence = 0.70

        for cat, concepts in CLASSIFICATION_RULES.items():
            all_concepts_matched = True
            cat_matched_kws = []
            for concept in concepts:
                matched = [kw for kw in concept["keywords"] if re.search(r'\b' + re.escape(kw) + r's?\b', source_lower)]
                if not matched:
                    all_concepts_matched = False
                    break
                cat_matched_kws.append(matched[0])
            if all_concepts_matched:
                ai_spec = cat
                classification_confidence = 0.75
                matched_terms.extend(cat_matched_kws)
                break

        # 3. Product capabilities / developments (deterministic sentence extraction)
        capabilities: List[str] = []
        for s in sentences:
            if len(s) > 25 and any(k in s.lower() for k in ["features", "allows", "enables", "provides", "supports", "built for", "designed to"]):
                capabilities.append(s[:180])
                if len(capabilities) >= 3:
                    break

        # Find exact sentence/span evidence for extracted terms
        all_extracted_terms = list(found_techs) + list(matched_terms)
        if not all_extracted_terms and ai_spec:
            all_extracted_terms.append(ai_spec)
        evidence_sentence = self._find_evidence_sentence_for_terms(all_extracted_terms, sentences, source_text)

        # Calibrated confidence score (never 0.95!)
        if found_techs:
            confidence = 0.80  # Grounded exact keyword match
        elif ai_spec:
            confidence = classification_confidence  # Heuristic classification
        elif capabilities:
            confidence = 0.75
        elif source_text:
            confidence = 0.70
        else:
            confidence = 0.0

        # Populate structured output adhering to schema
        extracted: Dict[str, Any] = {}
        if json_schema and "properties" in json_schema:
            props = json_schema["properties"]
            for prop in props:
                if prop in ["technologies", "supported_technologies", "required_skills"]:
                    extracted[prop] = found_techs[:8]
                elif prop in ["preferred_skills"]:
                    extracted[prop] = found_techs[8:12] if len(found_techs) > 8 else []
                elif prop in ["ai_specialization", "research_domain", "ai_topic", "product_category"]:
                    extracted[prop] = ai_spec
                elif prop in ["main_capabilities", "key_developments", "key_contributions", "products_and_services"]:
                    extracted[prop] = capabilities
                elif prop in ["article_summary", "product_description", "company_description", "abstract", "methodology"]:
                    # Grounded verbatim substantive sentence matching evidence
                    extracted[prop] = evidence_sentence if evidence_sentence and len(evidence_sentence) > 20 else (sentences[0] if sentences else "")
                elif prop == "company_website" or prop == "official_product_url":
                    # Look for URL in text
                    url_m = re.search(r'https?://[^\s<>"\']+', source_text)
                    extracted[prop] = url_m.group(0) if url_m else None
                elif prop == "developer_or_company" or prop == "industry":
                    extracted[prop] = None
                elif prop == "role_specialization":
                    extracted[prop] = ai_spec
                elif prop == "evidence":
                    extracted[prop] = evidence_sentence
                elif prop == "confidence_score":
                    extracted[prop] = round(confidence, 2)
        else:
            extracted = {
                "technologies": found_techs[:8],
                "ai_specialization": ai_spec,
                "capabilities": capabilities,
                "evidence": evidence_sentence,
                "confidence_score": round(confidence, 2)
            }

        # Validate with jsonschema if schema was supplied
        if json_schema:
            is_valid, schema_err = validate_json_schema(extracted, json_schema)
            if not is_valid:
                logger.warning(f"Offline provider extracted data failed JSON schema validation: {schema_err}")
                return LLMResponse(
                    content="",
                    structured_data=None,
                    token_usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0, estimated_cost_usd=0.0),
                    model=self.model,
                    provider=self.name,
                    success=False,
                    error=f"Schema validation failed: {schema_err}"
                )

        out_json = json.dumps(extracted, ensure_ascii=False)

        return LLMResponse(
            content=out_json,
            structured_data=extracted,
            token_usage=TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                estimated_cost_usd=0.0
            ),
            model=self.model,
            provider=self.name,
            success=True
        )
