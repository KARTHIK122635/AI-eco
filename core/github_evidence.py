"""
core/github_evidence.py
=======================
Defines domain models, evidence types, confidence scoring rules, and validation logic
for associating AI ecosystem entities (research papers, products, startups) with
GitHub repositories.

Strict Rules:
- Direct official links are strong evidence (HIGH confidence).
- Abstract/paper mentions with verified repository structure are strong evidence.
- Organization/profile links require project name corroboration.
- Name similarity alone is insufficient.
- Ambiguous matches remain UNVERIFIED.
- Zero fabrication of repository links or associations.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from core.github_client import parse_github_owner_repo, normalize_repo_id


class EntityType(str, Enum):
    RESEARCH_PAPER = "research_paper"
    PRODUCT = "product"
    STARTUP = "startup"


class EvidenceType(str, Enum):
    CANONICAL_FIELD = "CANONICAL_FIELD"               # Explicit repository URL in source record
    ABSTRACT_MENTION = "ABSTRACT_MENTION"             # Extracted from paper abstract or description text
    DEVELOPER_PROFILE = "DEVELOPER_PROFILE"           # Developer GitHub profile URL
    HOMEPAGE_LINK = "HOMEPAGE_LINK"                   # Official website linking directly to GitHub repo
    EXPLICIT_SOURCE_LINK = "EXPLICIT_SOURCE_LINK"     # Direct URL in provenance/source metadata
    SEARCH_HEURISTIC = "SEARCH_HEURISTIC"             # Keyword match (UNVERIFIED without direct link)


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNVERIFIED = "UNVERIFIED"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    DISCOVERED = "DISCOVERED"
    REJECTED = "REJECTED"


@dataclass
class RepositoryAssociation:
    """Represents a validated or candidate association between an entity and a GitHub repository."""
    association_id: str
    source_entity_type: str
    source_entity_id: str
    repo_id: str
    evidence_url: Optional[str]
    evidence_type: str
    confidence: str
    discovery_timestamp: str
    verification_status: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvidenceValidator:
    """Validates and assigns confidence scores to proposed entity-repository associations."""

    @staticmethod
    def evaluate_association(
        source_entity_type: str,
        source_entity_id: str,
        raw_url: str,
        evidence_type: str,
        entity_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[RepositoryAssociation]:
        """
        Parses raw URL, validates evidence strength, and returns a RepositoryAssociation.
        Returns None if raw_url cannot be parsed as a valid GitHub repository.
        """
        parsed = parse_github_owner_repo(raw_url)
        if not parsed:
            return None

        owner, repo = parsed
        repo_id = f"{owner}/{repo}"
        now_iso = datetime.now(timezone.utc).isoformat()
        clean_assoc_id = f"assoc_{source_entity_type}_{source_entity_id}_{owner}_{repo}".replace("/", "_").replace(".", "_")

        # Apply strict confidence scoring rules
        if evidence_type in (EvidenceType.CANONICAL_FIELD.value, EvidenceType.EXPLICIT_SOURCE_LINK.value):
            # Check for truncated or suspicious repository name (e.g., <= 2 chars or obvious truncation)
            if len(repo) <= 2:
                confidence = ConfidenceLevel.MEDIUM.value
                status = VerificationStatus.MANUAL_REVIEW.value
                rule_note = f"Direct link in source entity record has truncated or suspicious repository name '{repo}'; flagged for manual review."
            else:
                confidence = ConfidenceLevel.HIGH.value
                status = VerificationStatus.VERIFIED.value
                rule_note = "Direct official link in source entity record."
        elif evidence_type == EvidenceType.ABSTRACT_MENTION.value:
            # Abstract text mentions require live API confirmation before verification
            confidence = ConfidenceLevel.MEDIUM.value
            status = VerificationStatus.UNVERIFIED.value
            rule_note = "Direct GitHub repository URL extracted from official abstract text; requires live API confirmation."
        elif evidence_type == EvidenceType.HOMEPAGE_LINK.value:
            confidence = ConfidenceLevel.HIGH.value
            status = VerificationStatus.VERIFIED.value
            rule_note = "Official homepage links directly to repository."
        elif evidence_type == EvidenceType.DEVELOPER_PROFILE.value:
            # If repo name matches entity name, high confidence; else medium
            clean_repo = repo.lower().replace("-", "").replace("_", "")
            clean_entity = entity_name.lower().replace("-", "").replace("_", "").replace(" ", "") if entity_name else ""
            if entity_name and (clean_repo in clean_entity or clean_entity in clean_repo):
                confidence = ConfidenceLevel.HIGH.value
                status = VerificationStatus.VERIFIED.value
                rule_note = f"Developer profile repository matches entity name '{entity_name}'."
            else:
                confidence = ConfidenceLevel.MEDIUM.value
                status = VerificationStatus.UNVERIFIED.value
                rule_note = "Developer repository identified; pending entity name confirmation."
        elif evidence_type == EvidenceType.SEARCH_HEURISTIC.value:
            clean_repo = repo.lower().replace("-", "").replace("_", "")
            clean_entity = entity_name.lower().replace("-", "").replace("_", "").replace(" ", "") if entity_name else ""
            if not entity_name or (clean_repo not in clean_entity and clean_entity not in clean_repo):
                # Reject unrelated repository found via search heuristic (name similarity rejection)
                return None
            confidence = ConfidenceLevel.LOW.value
            status = VerificationStatus.UNVERIFIED.value
            rule_note = "Heuristic match; requires manual verification."
        else:
            confidence = ConfidenceLevel.LOW.value
            status = VerificationStatus.UNVERIFIED.value
            rule_note = "Heuristic match; requires manual verification."

        final_note = f"{rule_note} {notes or ''}".strip()

        return RepositoryAssociation(
            association_id=clean_assoc_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            repo_id=repo_id,
            evidence_url=raw_url,
            evidence_type=evidence_type,
            confidence=confidence,
            discovery_timestamp=now_iso,
            verification_status=status,
            notes=final_note
        )
