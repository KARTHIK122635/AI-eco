"""
JSON Schema validation utility for LLM providers.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Strict JSON Schema Validation
"""

import logging
from typing import Dict, Any, Tuple, Optional
import jsonschema
from jsonschema import Draft7Validator

logger = logging.getLogger("LLMSchemaValidator")


def validate_json_schema(data: Any, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates a data dictionary or structure against a JSON Schema.
    Returns (True, None) on success, or (False, error_description) on failure.
    """
    if not isinstance(schema, dict):
        return False, "Schema must be a valid dictionary."

    try:
        validator = Draft7Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            first_err = errors[0]
            field_path = ".".join(str(p) for p in first_err.path) or "root"
            err_msg = f"Schema validation error at '{field_path}': {first_err.message}"
            logger.warning(err_msg)
            return False, err_msg
        return True, None
    except jsonschema.SchemaError as se:
        err_msg = f"Invalid JSON Schema definition: {se.message}"
        logger.error(err_msg)
        return False, err_msg
    except Exception as e:
        err_msg = f"Unexpected error during schema validation: {str(e)}"
        logger.error(err_msg)
        return False, err_msg
