"""
Canonical Schema Mapping & Verification for Stage 3 Enrichment
==============================================================
Provides formal schema allowlisting, column existence verification,
and schema compatibility enforcement for Stage 3 proposals.
Prevents SQLite OperationalError (no such column) and guarantees SQL identifier safety.
"""

import re
from typing import Dict, List, Optional, Set, Tuple

# Strict SQL Identifier regex to prevent SQL injection
IDENTIFIER_REGEX = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# Authoritative Canonical Table Schemas (Audit 26 Baseline)
CANONICAL_TABLE_SCHEMAS: Dict[str, Set[str]] = {
    "ai_startups": {
        "startup_id", "entity_name", "ai_focus_area", "ai_evidence",
        "employee_count", "pricing_model", "website", "primary_source_url",
        "provenance_sources", "headquarters", "batch_or_founded",
        "description", "collected_at"
    },
    "ai_products": {
        "product_id", "entity_name", "product_type", "ai_task_category",
        "developer_or_company", "developer_profile_url", "official_company_website",
        "pricing_model", "license", "access_type", "actual_price",
        "original_source_url", "provenance_source", "description", "collected_at"
    },
    "ai_research_papers": {
        "paper_id", "title", "authors", "publication_date", "categories",
        "paper_url", "github_url", "github_stars", "github_star_source",
        "github_star_retrieved_at", "provenance", "abstract", "collected_at"
    },
    "ai_news": {
        "news_id", "title", "summary", "content", "content_status",
        "summary_type", "content_retrieved_at", "source_name", "article_url",
        "author", "published_at", "category", "related_companies",
        "collected_at", "provenance"
    },
    "ai_jobs": {
        "job_id", "job_title", "company_name", "company_website", "category",
        "classification_reason", "responsibility_evidence", "qualification_evidence",
        "classification_confidence", "job_description", "required_skills",
        "preferred_skills", "experience_level", "location", "remote_type",
        "salary_min", "salary_max", "currency", "compensation_type",
        "compensation_period", "employment_type", "job_status", "vacancy_status",
        "application_url", "posted_at", "source_name", "provenance", "collected_at"
    }
}

ENTITY_TABLE_MAP: Dict[str, Tuple[str, str]] = {
    "startup": ("ai_startups", "startup_id"),
    "product": ("ai_products", "product_id"),
    "paper": ("ai_research_papers", "paper_id"),
    "news": ("ai_news", "news_id"),
    "job": ("ai_jobs", "job_id"),
}


def is_valid_sql_identifier(identifier: str) -> bool:
    """Verifies that an identifier contains only alphanumeric characters and underscores."""
    if not identifier or not isinstance(identifier, str):
        return False
    return bool(IDENTIFIER_REGEX.match(identifier))


def is_column_allowed(table_name: str, column_name: str) -> bool:
    """Verifies that a table and column exist in the canonical schema allowlist."""
    if not is_valid_sql_identifier(table_name) or not is_valid_sql_identifier(column_name):
        return False
    if table_name not in CANONICAL_TABLE_SCHEMAS:
        return False
    return column_name in CANONICAL_TABLE_SCHEMAS[table_name]


def check_proposal_schema_compatibility(entity_type: str, field_name: str) -> Tuple[bool, str, str]:
    """
    Checks if a proposal's target field can be safely written to the canonical SQLite table.
    Returns:
        (is_compatible: bool, status_code: str, rationale: str)
    """
    if entity_type not in ENTITY_TABLE_MAP:
        return False, "INVALID_ENTITY", f"Entity type '{entity_type}' is not recognized in canonical mapping."

    table_name, _ = ENTITY_TABLE_MAP[entity_type]

    if not is_valid_sql_identifier(field_name):
        return False, "INVALID_IDENTIFIER", f"Field name '{field_name}' contains disallowed characters."

    if is_column_allowed(table_name, field_name):
        return (
            True,
            "SCHEMA_COMPATIBLE",
            f"Field '{field_name}' exists as a valid column in canonical table '{table_name}'."
        )

    # Detailed explanation of schema incompatibility
    reason = (
        f"BLOCKED_SCHEMA: Column '{field_name}' does not exist in canonical table '{table_name}'. "
        f"Direct SQL UPDATE would raise sqlite3.OperationalError: no such column. "
        f"Requires formal schema migration or schema mapping decision."
    )
    return False, "BLOCKED_SCHEMA", reason


def get_physical_table_columns(db_path: str, table_name: str) -> Set[str]:
    """Queries actual physical SQLite database via PRAGMA table_info."""
    if not is_valid_sql_identifier(table_name):
        return set()
    import sqlite3
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        c = conn.cursor()
        c.execute(f"PRAGMA table_info({table_name})")
        cols = {r[1] for r in c.fetchall()}
        conn.close()
        return cols
    except Exception:
        return set()

