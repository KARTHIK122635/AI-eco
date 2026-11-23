"""
Schemas and validation status definitions for Structured LLM Enrichment.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Strict Validation & Multi-Table Persistence
"""

import hashlib
from dataclasses import dataclass, asdict, field
from typing import Any, Optional, Dict, List, Set, Tuple, Union
from datetime import datetime, timezone
from enum import Enum


class ValidationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    FAILED = "FAILED"


# Fields that must NEVER be inferred by LLMs per anti-hallucination rules
FORBIDDEN_INFERENCE_FIELDS = {
    "salary_min", "salary_max", "currency", "compensation_type", "compensation_period",
    "location", "headquarters", "company_size", "employee_count", "publication_date",
    "published_at", "posted_at", "job_status", "vacancy_status"
}

# Protected job fields that LLM enrichment MUST NOT modify
PROTECTED_JOB_FIELDS = {
    "salary_min", "salary_max", "currency", "compensation_type", "compensation_period",
    "job_status", "vacancy_status", "job_description", "application_url",
    "responsibility_evidence", "qualification_evidence"
}

# The 15 boundary records preserved through Audits 10-18
RETAINED_15_REVIEW_JOB_IDS = {
    'job_ca9fd326e9b5b4a3', 'job_d93736d1ee4a9098', 'job_87e7a826e1904b7b',
    'job_6b50fb83f97464c3', 'job_61a941b22ab64bde', 'job_20072b58f5dc3523',
    'job_0d920108a62c8874', 'job_8ad086e5f89d9290', 'job_9a8d370f471b9403',
    'job_3f7c9cb190129a33', 'job_91fd8017f05b1d94', 'job_f3d068e4db415d90',
    'job_7427cacb294b9060', 'job_953d904c00132369', 'job_0fccf7a2e05aac14'
}


# Version 2.0.0 Classification Mapping Rules
CLASSIFICATION_RULES_VERSION = "2.0.0"

# Explicit compound classification rules: maps category to required constituent concepts.
# Generic words like "vision", "image", "video", or "diffusion" are excluded.
# Specific technical terms are required for every constituent concept.
COMPOUND_CLASSIFICATION_CONCEPTS: Dict[str, List[Dict[str, Any]]] = {
    "Computer Vision & Multimodal": [
        {
            "concept": "computer vision",
            "keywords": [
                "computer vision", "object detection", "image segmentation",
                "semantic segmentation", "instance segmentation", "image classification",
                "optical character recognition", "facial recognition", "visual reasoning",
                "convolutional neural network"
            ]
        },
        {
            "concept": "multimodal",
            "keywords": [
                "multimodal", "multi-modal", "vision-language", "vlm",
                "cross-modal", "image-text generation", "multimodal model"
            ]
        }
    ],
    "Foundation Models & LLMs": [
        {
            "concept": "foundation models",
            "keywords": [
                "foundation model", "foundation models", "frontier model",
                "transformer model", "transformer", "transformers", "pre-trained model"
            ]
        },
        {
            "concept": "large language models",
            "keywords": [
                "large language model", "large language models", "llm", "llms",
                "generative pre-trained transformer", "gpt", "claude", "gemini",
                "llama", "autoregressive language model", "language model"
            ]
        }
    ],
    "Autonomous Agents & Workflows": [
        {
            "concept": "autonomous agents",
            "keywords": [
                "autonomous agent", "autonomous agents", "ai agent", "ai agents",
                "agentic system", "multi-agent system", "reinforcement learning agent",
                "rl agent", "planning agent", "reinforcement learning"
            ]
        },
        {
            "concept": "workflows",
            "keywords": [
                "workflow automation", "tool use", "function calling",
                "agentic workflow", "agentic orchestration", "long horizon planning",
                "decision horizons", "decision making"
            ]
        }
    ],
    "AI Infrastructure & MLOps": [
        {
            "concept": "ai infrastructure",
            "keywords": [
                "gpu cluster", "cuda", "distributed training", "vllm",
                "tensorrt", "triton inference server", "accelerator hardware"
            ]
        },
        {
            "concept": "mlops",
            "keywords": [
                "mlops", "model serving", "feature store", "model registry",
                "model deployment pipeline", "distributed serving"
            ]
        }
    ],
    "Speech & Audio AI": [
        {
            "concept": "speech",
            "keywords": [
                "speech recognition", "automatic speech recognition", "asr",
                "text-to-speech", "tts", "voice synthesis", "whisper model"
            ]
        },
        {
            "concept": "audio",
            "keywords": [
                "audio processing", "acoustic model", "audio generation",
                "sound classification"
            ]
        }
    ],
    "Healthcare & Life Sciences AI": [
        {
            "concept": "healthcare / clinical",
            "keywords": [
                "clinical diagnostics", "electronic health records",
                "medical imaging", "patient care ai"
            ]
        },
        {
            "concept": "life sciences / biology",
            "keywords": [
                "drug discovery", "protein structure", "molecular modeling",
                "bioinformatics", "genomics", "computational biology"
            ]
        }
    ]
}
CLASSIFICATION_RULES = COMPOUND_CLASSIFICATION_CONCEPTS


# Canonical Approved Taxonomies per entity type and classification field (Audit 21)
APPROVED_TAXONOMY: Dict[str, Dict[str, Set[str]]] = {
    "startup": {
        "ai_specialization": {
            "Computer Vision & Multimodal",
            "Computer Vision & Generative Media",
            "Foundation Models & LLMs",
            "NLP & Foundation Models",
            "Autonomous Agents & Workflows",
            "Autonomous Agents & Copilots",
            "AI Infrastructure & MLOps",
            "Machine Learning & Core AI",
            "Speech & Audio AI",
            "Healthcare & Life Sciences AI",
            "Applied AI & Automation"
        },
        "industry": {
            "Healthcare", "Finance & Fintech", "Enterprise Software",
            "Cybersecurity", "E-commerce & Retail", "Developer Tools",
            "Education", "Manufacturing & Robotics", "Biotechnology",
            "Media & Entertainment", "Legal Tech", "Transportation & Logistics"
        }
    },
    "product": {
        "product_category": {
            "Computer Vision & Multimodal",
            "Computer Vision & Generative Media",
            "Foundation Models & LLMs",
            "NLP & Foundation Models",
            "Autonomous Agents & Workflows",
            "Autonomous Agents & Copilots",
            "AI Infrastructure & MLOps",
            "Machine Learning & Core AI",
            "Speech & Audio AI",
            "Healthcare & Life Sciences AI",
            "Applied AI & Automation",
            "Developer Tools & Frameworks",
            "Data Science & Analytics"
        },
        "category": {
            "Computer Vision & Multimodal",
            "Computer Vision & Generative Media",
            "Foundation Models & LLMs",
            "NLP & Foundation Models",
            "Autonomous Agents & Workflows",
            "Autonomous Agents & Copilots",
            "AI Infrastructure & MLOps",
            "Machine Learning & Core AI",
            "Speech & Audio AI",
            "Healthcare & Life Sciences AI",
            "Applied AI & Automation"
        }
    },
    "paper": {
        "research_domain": {
            "Computer Vision & Pattern Recognition",
            "Computation and Language",
            "Machine Learning",
            "Artificial Intelligence",
            "Neural and Evolutionary Computing",
            "Robotics",
            "Computer Vision & Multimodal",
            "Foundation Models & LLMs",
            "Autonomous Agents & Workflows",
            "AI Infrastructure & MLOps",
            "Speech & Audio AI",
            "Healthcare & Life Sciences AI"
        }
    },
    "news": {
        "news_category": {
            "General AI & Industry",
            "Generative Media & Multimodal",
            "Robotics & Embodied AI",
            "LLMs & Foundation Models",
            "AI Agents & Applications",
            "AI Hardware & Infrastructure",
            "AI Business & Investment",
            "Policy, Safety & Governance"
        },
        "category": {
            "General AI & Industry",
            "Generative Media & Multimodal",
            "Robotics & Embodied AI",
            "LLMs & Foundation Models",
            "AI Agents & Applications",
            "AI Hardware & Infrastructure",
            "AI Business & Investment",
            "Policy, Safety & Governance"
        }
    },
    "job": {
        "category": {
            "CORE_AI_ML",
            "AI_INFRASTRUCTURE",
            "AI_PRODUCT_SOLUTIONS",
            "AI_SUPPORTING_TECH",
            "NON_AI_TECH",
            "NON_TECHNICAL",
            "UNCERTAIN"
        },
        "role_specialization": {
            "Computer Vision & Multimodal",
            "Foundation Models & LLMs",
            "Autonomous Agents & Workflows",
            "AI Infrastructure & MLOps",
            "Speech & Audio AI",
            "Healthcare & Life Sciences AI",
            "Machine Learning Engineering",
            "Data Engineering",
            "AI Research",
            "AI Product Management",
            "MLOps"
        }
    }
}

# Master set of all approved category names (case-normalized)
ALL_APPROVED_TAXONOMY_CATEGORIES: Set[str] = set()
for entity_cats in APPROVED_TAXONOMY.values():
    for field_cats in entity_cats.values():
        ALL_APPROVED_TAXONOMY_CATEGORIES.update({c.strip().lower() for c in field_cats})


def is_approved_category(
    entity_type: Optional[str],
    field_name: Optional[str],
    category_name: Optional[str]
) -> bool:
    """
    Checks whether a category is part of the approved taxonomy.
    Enforces strict taxonomy compliance across all providers (Audit 21).
    """
    if not category_name or not str(category_name).strip():
        return False
    cat_clean = str(category_name).strip()
    cat_lower = cat_clean.lower()

    if entity_type and field_name:
        ent = entity_type.lower()
        fld = field_name.lower()
        if ent in APPROVED_TAXONOMY and fld in APPROVED_TAXONOMY[ent]:
            return any(c.lower() == cat_lower for c in APPROVED_TAXONOMY[ent][fld])

    return cat_lower in ALL_APPROVED_TAXONOMY_CATEGORIES


# Documented Canonical Field Mappings for Every Entity Type (Audit 21)
CANONICAL_FIELD_MAPPINGS: Dict[str, List[str]] = {
    "startup": [
        "startup_id", "entity_name", "ai_focus_area", "ai_evidence",
        "employee_count", "pricing_model", "website", "primary_source_url",
        "headquarters", "batch_or_founded", "description"
    ],
    "product": [
        "product_id", "entity_name", "product_type", "ai_task_category",
        "developer_or_company", "official_company_website", "pricing_model",
        "license", "access_type", "actual_price", "original_source_url",
        "description"
    ],
    "paper": [
        "paper_id", "title", "authors", "publication_date",
        "categories", "paper_url", "github_url", "abstract"
    ],
    "news": [
        "news_id", "title", "summary", "content", "content_status",
        "summary_type", "source_name", "article_url", "author",
        "published_at", "category", "related_companies"
    ],
    "job": [
        "job_id", "job_title", "company_name", "company_website", "category",
        "responsibility_evidence", "qualification_evidence", "job_description",
        "required_skills", "preferred_skills", "experience_level", "location",
        "remote_type", "salary_min", "salary_max", "currency",
        "compensation_type", "compensation_period", "employment_type",
        "job_status", "vacancy_status", "application_url", "source_name"
    ]
}


def build_canonical_representation(entity_type: str, record: Dict[str, Any]) -> str:
    """
    Constructs the authoritative, deterministic canonical source representation
    by serializing every documented canonical field mapped to this entity type.
    """
    fields = CANONICAL_FIELD_MAPPINGS.get(entity_type, [])
    lines = []
    for f in fields:
        val = record.get(f)
        val_str = "" if val is None else str(val).strip()
        lines.append(f"{f}: {val_str}")
    return "\n".join(lines)


def compute_canonical_source_version(entity_type: str, record: Dict[str, Any]) -> str:
    """
    Computes full 64-character SHA-256 hash of the complete authoritative canonical
    source representation across all documented canonical fields (Audit 21).
    Modifying any source field immediately alters this checksum.
    """
    rep = build_canonical_representation(entity_type, record)
    return hashlib.sha256(rep.encode("utf-8")).hexdigest()


def compute_source_version(source_text: Optional[str]) -> str:
    """Computes SHA-256 checksum of source content for provenance and deduplication."""
    if not source_text:
        return hashlib.sha256(b"").hexdigest()
    return hashlib.sha256(source_text.strip().encode("utf-8")).hexdigest()
    return hashlib.sha256(source_text.strip().encode("utf-8")).hexdigest()


@dataclass
class EnrichmentResult:
    """
    Schema-constrained enrichment outcome record.
    Complies with Audit 19 requirements.
    """
    attempt_id: str
    record_id: str
    entity_type: str
    field_name: str
    original_value: Any
    enriched_value: Any
    source_url: str
    evidence: str
    source_version: str
    confidence_score: float
    enrichment_method: str
    provider: str
    model: str
    enriched_at: str
    validation_status: str
    validation_rationale: str = ""
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# JSON Schemas for Entity-Specific LLM Extractions

STARTUP_ENRICHMENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StartupEnrichment",
    "type": "object",
    "properties": {
        "company_description": {"type": ["string", "null"], "description": "Concise summary of what the company does"},
        "industry": {"type": ["string", "null"], "description": "Primary industry sector"},
        "ai_specialization": {"type": ["string", "null"], "description": "Specific AI subfield or focus"},
        "products_and_services": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Products or services offered"
        },
        "technologies": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Core frameworks, models, or technologies used"
        },
        "company_website": {"type": ["string", "null"], "description": "Official company website if mentioned in source"},
        "evidence": {"type": "string", "description": "Verbatim quote or sentence from source supporting findings"},
        "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["evidence", "confidence_score"],
    "additionalProperties": False
}

PRODUCT_ENRICHMENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ProductEnrichment",
    "type": "object",
    "properties": {
        "product_description": {"type": ["string", "null"], "description": "Concise summary of the product"},
        "product_category": {"type": ["string", "null"], "description": "Product category classification"},
        "main_capabilities": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key capabilities or features"
        },
        "supported_technologies": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Technologies, frameworks, or models supported"
        },
        "developer_or_company": {"type": ["string", "null"], "description": "Creator or developer organization"},
        "official_product_url": {"type": ["string", "null"], "description": "Official product URL if in text"},
        "evidence": {"type": "string", "description": "Verbatim quote or sentence from source supporting findings"},
        "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["evidence", "confidence_score"],
    "additionalProperties": False
}

RESEARCH_PAPER_ENRICHMENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ResearchPaperEnrichment",
    "type": "object",
    "properties": {
        "abstract": {"type": ["string", "null"], "description": "Paper abstract if available in source"},
        "research_domain": {"type": ["string", "null"], "description": "Primary academic domain"},
        "methodology": {"type": ["string", "null"], "description": "Key methodology or experimental setup"},
        "model_or_architecture": {"type": ["string", "null"], "description": "Model architecture introduced or evaluated"},
        "key_contributions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Main novel contributions claimed"
        },
        "evidence": {"type": "string", "description": "Verbatim quote or sentence from source supporting findings"},
        "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["evidence", "confidence_score"],
    "additionalProperties": False
}

NEWS_ENRICHMENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "NewsEnrichment",
    "type": "object",
    "properties": {
        "article_summary": {"type": ["string", "null"], "description": "Summary grounded in article content"},
        "ai_topic": {"type": ["string", "null"], "description": "Specific AI topic covered"},
        "companies_or_models_mentioned": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key companies, labs, or models mentioned in text"
        },
        "news_category": {"type": ["string", "null"], "description": "Category of news development"},
        "key_developments": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key event bullets extracted from text"
        },
        "evidence": {"type": "string", "description": "Verbatim excerpt from article text"},
        "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["evidence", "confidence_score"],
    "additionalProperties": False
}

JOB_ENRICHMENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "JobEnrichment",
    "type": "object",
    "properties": {
        "role_specialization": {"type": ["string", "null"], "description": "Specialized focus within role"},
        "required_skills": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Skills and qualifications mentioned in text"
        },
        "preferred_skills": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Preferred / nice-to-have skills mentioned in text"
        },
        "technologies": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specific languages, tools, frameworks mentioned"
        },
        "evidence": {"type": "string", "description": "Verbatim excerpt from job description"},
        "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["evidence", "confidence_score"],
    "additionalProperties": False
}

# Strict JSON Schema for EnrichmentResult objects
ENRICHMENT_RESULT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "EnrichmentResultRecord",
    "type": "object",
    "properties": {
        "attempt_id": {"type": "string", "minLength": 1},
        "record_id": {"type": "string", "minLength": 1},
        "entity_type": {
            "type": "string",
            "enum": ["startup", "product", "paper", "news", "job"]
        },
        "field_name": {"type": "string", "minLength": 1},
        "original_value": {},
        "enriched_value": {},
        "source_url": {"type": "string"},
        "evidence": {"type": "string"},
        "source_version": {"type": "string", "minLength": 1},
        "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "enrichment_method": {"type": "string", "minLength": 1},
        "provider": {"type": "string", "minLength": 1},
        "model": {"type": "string", "minLength": 1},
        "enriched_at": {"type": "string"},
        "validation_status": {
            "type": "string",
            "enum": ["VERIFIED", "NEEDS_REVIEW", "INSUFFICIENT_EVIDENCE", "FAILED"]
        },
        "validation_rationale": {"type": "string"},
        "retry_count": {"type": "integer", "minimum": 0}
    },
    "required": [
        "attempt_id", "record_id", "entity_type", "field_name", "source_url",
        "evidence", "source_version", "confidence_score", "enrichment_method",
        "provider", "model", "enriched_at", "validation_status"
    ],
    "additionalProperties": False
}
