from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


def format_canonical_startup(s: Dict[str, Any]) -> Dict[str, Any]:
    """Formats an AI startup record into the canonical assignment schema."""
    provenance = s.get("provenance_sources", ["Y Combinator"])
    if isinstance(provenance, str):
        provenance = [p.strip() for p in provenance.split(";") if p.strip()]

    source_name = provenance[0] if provenance else "Y Combinator"
    source_url = s.get("primary_source_url") or s.get("original_source_url") or s.get("website") or ""

    return {
        "schemaVersion": "1.0",
        "recordType": "STARTUP",
        "source": {
            "name": source_name,
            "url": source_url
        },
        "content": {
            "entityName": s.get("name") or s.get("company_name", "Unknown"),
            "data": {
                "startupId": s.get("startup_id") or f"startup_{abs(hash(s.get('name', '')))}",
                "aiFocusArea": s.get("ai_focus_area", "Applied AI & Automation"),
                "aiEvidence": s.get("ai_evidence", []),
                "employeeCount": s.get("employee_count"),
                "pricingModel": s.get("pricing_model"),
                "website": s.get("website") or s.get("company_website"),
                "headquarters": s.get("headquarters"),
                "batchOrFounded": s.get("batch_or_founded"),
                "description": s.get("description"),
                "provenanceSources": provenance
            }
        },
        "collectedAt": s.get("discovered_at") or datetime.now(timezone.utc).isoformat()
    }


def format_canonical_product(p: Dict[str, Any]) -> Dict[str, Any]:
    """Formats an AI product record into the canonical assignment schema."""
    source_name = p.get("provenance_source", "Hugging Face Hub")
    source_url = p.get("original_source_url", "")
    author = p.get("developer_or_company") or p.get("company_name") or "Community"

    # Construct developer company profile website if not explicitly given
    company_website = p.get("company_website")
    if not company_website:
        if "Hugging Face" in source_name:
            company_website = f"https://huggingface.co/{author.strip()}"
        elif "Product Hunt" in source_name:
            company_website = source_url

    return {
        "schemaVersion": "1.0",
        "recordType": "PRODUCT",
        "source": {
            "name": source_name,
            "url": source_url
        },
        "content": {
            "entityName": p.get("name") or p.get("product_name", "Untitled Product"),
            "data": {
                "productId": p.get("product_id") or f"prod_{abs(hash(p.get('name', '') + str(source_url)))}",
                "productType": p.get("product_type", "AI Model / Application"),
                "aiTaskCategory": p.get("ai_task_category", "machine-learning"),
                "developerOrCompany": author,
                "companyWebsite": company_website,
                "pricingModel": p.get("pricing_model"),
                "license": p.get("license"),
                "description": p.get("description"),
                "metrics": p.get("metrics", {})
            }
        },
        "collectedAt": p.get("discovered_at") or datetime.now(timezone.utc).isoformat()
    }


def format_canonical_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
    """Formats an AI research paper into the canonical assignment schema."""
    return {
        "schemaVersion": "1.0",
        "recordType": "RESEARCH_PAPER",
        "source": {
            "name": paper.get("provenance", "arXiv"),
            "url": paper.get("paper_url", "")
        },
        "content": {
            "entityName": paper.get("title", "Untitled Research Paper"),
            "data": {
                "paperId": paper.get("paper_id"),
                "authors": paper.get("authors", []),
                "publicationDate": paper.get("publication_date"),
                "categories": paper.get("categories", []),
                "abstract": paper.get("abstract"),
                "githubUrl": paper.get("github_url"),
                "githubStars": paper.get("github_stars")
            }
        },
        "collectedAt": datetime.now(timezone.utc).isoformat()
    }
