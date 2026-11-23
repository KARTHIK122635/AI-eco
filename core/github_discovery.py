"""
core/github_discovery.py
========================
Discovers GitHub repositories linked to AI ecosystem entities (research papers,
products, startups) using multi-source evidence extraction and strict validation.

Inputs:
- ai_research_papers: canonical github_url, abstract text mentions, paper_url
- ai_products: developer_profile_url, original_source_url, official_company_website, description
- ai_startups: website, primary_source_url, description

Rules:
- Never invents repository URLs.
- Deduplicates repositories and associations.
- Assigns strict evidence types and confidence levels via EvidenceValidator.
- Persists new associations and newly discovered repositories to the database.
"""

import re
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from core.github_client import parse_github_owner_repo, normalize_repo_id
from core.github_evidence import (
    EvidenceValidator, RepositoryAssociation,
    EntityType, EvidenceType, ConfidenceLevel, VerificationStatus
)

DEFAULT_DB_PATH = "data/working/phase5_github_candidate.db"


def extract_github_urls_from_text(text: Optional[str]) -> List[str]:
    """Extracts candidate GitHub repository URLs from arbitrary text."""
    if not text:
        return []
    # Pattern to match https://github.com/owner/repo
    pattern = r'https?://(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)'
    matches = re.finditer(pattern, text)
    urls = []
    for m in matches:
        full_match = m.group(0).rstrip('.)],;\'"')
        parsed = parse_github_owner_repo(full_match)
        if parsed:
            urls.append(f"https://github.com/{parsed[0]}/{parsed[1]}")
    # Deduplicate while preserving order
    return list(dict.fromkeys(urls))


class GitHubDiscoveryEngine:
    """Discovers repository links across all ecosystem entities in SQLite."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk_status == 1, "Foreign key enforcement failed to activate!"
        conn.row_factory = sqlite3.Row
        return conn

    def discover_from_research_papers(self) -> List[RepositoryAssociation]:
        """Discovers repositories from research papers (canonical field + abstract text)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT paper_id, title, paper_url, github_url, abstract
            FROM ai_research_papers;
        """)
        papers = cursor.fetchall()
        conn.close()

        associations: List[RepositoryAssociation] = []

        for p in papers:
            paper_id = p["paper_id"]
            title = p["title"]
            gh_url = p["github_url"]
            abstract = p["abstract"] or ""
            paper_url = p["paper_url"] or ""

            # 1. Canonical field
            if gh_url and "github.com" in gh_url:
                assoc = EvidenceValidator.evaluate_association(
                    source_entity_type=EntityType.RESEARCH_PAPER.value,
                    source_entity_id=paper_id,
                    raw_url=gh_url,
                    evidence_type=EvidenceType.CANONICAL_FIELD.value,
                    entity_name=title,
                    notes=f"Canonical paper implementation for '{title[:60]}'"
                )
                if assoc:
                    associations.append(assoc)

            # 2. Abstract mentions (if not already captured by canonical field)
            abstract_urls = extract_github_urls_from_text(abstract)
            for a_url in abstract_urls:
                # Skip if matches the canonical URL
                if gh_url and parse_github_owner_repo(gh_url) == parse_github_owner_repo(a_url):
                    continue
                assoc = EvidenceValidator.evaluate_association(
                    source_entity_type=EntityType.RESEARCH_PAPER.value,
                    source_entity_id=paper_id,
                    raw_url=a_url,
                    evidence_type=EvidenceType.ABSTRACT_MENTION.value,
                    entity_name=title,
                    notes=f"Discovered in paper abstract: '{title[:60]}'"
                )
                if assoc:
                    associations.append(assoc)

        return associations

    def discover_from_products(self) -> List[RepositoryAssociation]:
        """Discovers repositories from AI products (developer profiles, source URLs, descriptions)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT product_id, entity_name, developer_profile_url, original_source_url,
                   official_company_website, description
            FROM ai_products;
        """)
        products = cursor.fetchall()
        conn.close()

        associations: List[RepositoryAssociation] = []

        for prod in products:
            prod_id = prod["product_id"]
            name = prod["entity_name"]
            fields = [
                (prod["developer_profile_url"], EvidenceType.DEVELOPER_PROFILE.value),
                (prod["original_source_url"], EvidenceType.EXPLICIT_SOURCE_LINK.value),
                (prod["official_company_website"], EvidenceType.HOMEPAGE_LINK.value),
            ]

            for url, ev_type in fields:
                if url and "github.com" in url:
                    assoc = EvidenceValidator.evaluate_association(
                        source_entity_type=EntityType.PRODUCT.value,
                        source_entity_id=prod_id,
                        raw_url=url,
                        evidence_type=ev_type,
                        entity_name=name,
                        notes=f"Product repository for '{name}'"
                    )
                    if assoc:
                        associations.append(assoc)

            # Check description for explicit GitHub links
            desc_urls = extract_github_urls_from_text(prod["description"])
            for d_url in desc_urls:
                assoc = EvidenceValidator.evaluate_association(
                    source_entity_type=EntityType.PRODUCT.value,
                    source_entity_id=prod_id,
                    raw_url=d_url,
                    evidence_type=EvidenceType.EXPLICIT_SOURCE_LINK.value,
                    entity_name=name,
                    notes=f"Extracted from product description for '{name}'"
                )
                if assoc:
                    associations.append(assoc)

        return associations

    def discover_from_startups(self) -> List[RepositoryAssociation]:
        """Discovers repositories from AI startups (website, source URLs, descriptions)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT startup_id, entity_name, website, primary_source_url, description
            FROM ai_startups;
        """)
        startups = cursor.fetchall()
        conn.close()

        associations: List[RepositoryAssociation] = []

        for st in startups:
            st_id = st["startup_id"]
            name = st["entity_name"]
            fields = [
                (st["website"], EvidenceType.HOMEPAGE_LINK.value),
                (st["primary_source_url"], EvidenceType.EXPLICIT_SOURCE_LINK.value),
            ]

            for url, ev_type in fields:
                if url and "github.com" in url:
                    assoc = EvidenceValidator.evaluate_association(
                        source_entity_type=EntityType.STARTUP.value,
                        source_entity_id=st_id,
                        raw_url=url,
                        evidence_type=ev_type,
                        entity_name=name,
                        notes=f"Startup repository for '{name}'"
                    )
                    if assoc:
                        associations.append(assoc)

            # Check description for explicit links
            desc_urls = extract_github_urls_from_text(st["description"])
            for d_url in desc_urls:
                assoc = EvidenceValidator.evaluate_association(
                    source_entity_type=EntityType.STARTUP.value,
                    source_entity_id=st_id,
                    raw_url=d_url,
                    evidence_type=EvidenceType.EXPLICIT_SOURCE_LINK.value,
                    entity_name=name,
                    notes=f"Extracted from startup description for '{name}'"
                )
                if assoc:
                    associations.append(assoc)

        return associations

    def run_discovery(self, persist: bool = True) -> Dict[str, Any]:
        """
        Executes discovery across papers, products, and startups.
        Optionally persists new associations and newly discovered repositories to SQLite.
        """
        paper_assocs = self.discover_from_research_papers()
        prod_assocs = self.discover_from_products()
        startup_assocs = self.discover_from_startups()

        all_assocs = paper_assocs + prod_assocs + startup_assocs

        # Deduplicate associations by (source_entity_type, source_entity_id, repo_id)
        unique_assocs: Dict[Tuple[str, str, str], RepositoryAssociation] = {}
        for a in all_assocs:
            key = (a.source_entity_type, a.source_entity_id, a.repo_id)
            if key not in unique_assocs:
                unique_assocs[key] = a

        persisted_assocs = 0
        newly_registered_repos = 0

        if persist:
            conn = self._get_connection()
            cursor = conn.cursor()
            now_iso = datetime.now(timezone.utc).isoformat()

            for assoc in unique_assocs.values():
                # 1. Insert association
                cursor.execute("""
                    INSERT OR IGNORE INTO github_repository_associations (
                        association_id, source_entity_type, source_entity_id, repo_id,
                        evidence_url, evidence_type, confidence, discovery_timestamp,
                        verification_status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    assoc.association_id, assoc.source_entity_type, assoc.source_entity_id,
                    assoc.repo_id, assoc.evidence_url, assoc.evidence_type,
                    assoc.confidence, assoc.discovery_timestamp,
                    assoc.verification_status, assoc.notes
                ))
                if cursor.rowcount > 0:
                    persisted_assocs += 1

                # 2. Check if repository is in github_repositories; if not, register it!
                cursor.execute("SELECT repo_id FROM github_repositories WHERE repo_id = ?;", (assoc.repo_id,))
                if not cursor.fetchone():
                    parsed = parse_github_owner_repo(assoc.evidence_url or f"https://github.com/{assoc.repo_id}")
                    owner, repo = parsed if parsed else assoc.repo_id.split("/", 1)
                    cursor.execute("""
                        INSERT OR IGNORE INTO github_repositories (
                            repo_id, owner, repo_name, full_name, html_url,
                            description, associated_paper_id, is_archived,
                            latest_stars, latest_forks, last_checked_at, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        assoc.repo_id, owner, repo, assoc.repo_id,
                        f"https://github.com/{assoc.repo_id}",
                        f"Discovered via {assoc.source_entity_type} {assoc.source_entity_id}",
                        assoc.source_entity_id if assoc.source_entity_type == "research_paper" else None,
                        0, 0, 0, now_iso, "DISCOVERED"
                    ))
                    if cursor.rowcount > 0:
                        newly_registered_repos += 1

            conn.commit()
            conn.close()

        return {
            "total_discovered_associations": len(unique_assocs),
            "paper_associations": len(paper_assocs),
            "product_associations": len(prod_assocs),
            "startup_associations": len(startup_assocs),
            "persisted_associations": persisted_assocs,
            "newly_registered_repos": newly_registered_repos
        }
