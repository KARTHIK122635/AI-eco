"""
JSON Schema validation engine using python's jsonschema library.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Strict Schema Validation
"""

import logging
from typing import Dict, Any, Tuple, Optional

from core.llm.schema_validator import validate_json_schema
from core.enrichment.schemas import ENRICHMENT_RESULT_SCHEMA

logger = logging.getLogger("SchemaValidator")


def validate_enrichment_result_schema(result_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates an EnrichmentResult dictionary against the canonical ENRICHMENT_RESULT_SCHEMA.
    """
    return validate_json_schema(result_dict, ENRICHMENT_RESULT_SCHEMA)
