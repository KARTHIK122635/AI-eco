# Phase V: GitHub Repository Discovery & Evidence Association Report

## 1. Executive Summary

Phase V introduces an automated, multi-entity **Repository Discovery & Evidence Engine** (`core/github_discovery.py`, `core/github_evidence.py`). The engine systematically evaluates the entire AI ecosystem inventory across 1,060 research papers, 1,316 products, and 1,307 startups to identify, validate, and track open-source code repositories.

Every proposed repository association is backed by verifiable provenance, classified into formal evidence types, and assigned a deterministic confidence score. Zero repository links are invented or assumed based on name similarity alone.

---

## 2. Discovery Methodology & Entity Scanning

The discovery engine processes three distinct entity classes from the Phase V candidate database:

### 2.1 Research Papers (`ai_research_papers`)
- **Canonical GitHub URLs**: 190 papers have direct `github_url` fields populated during Phase I-III.
- **Abstract & Text Mining**: Regex URL extraction (`https://github.com/<owner>/<repo>`) executed across 1,060 abstracts and source URLs.
- **Discovered Inclusions**: Identified paper `arxiv_2611_24597` ("DAL: Dynamic Angular Loss for Imbalanced Medical Image Classification") containing an explicit abstract link to `https://github.com/msalman95/DAL`.

### 2.2 AI Products (`ai_products`)
- **Developer Profiles & Source URLs**: Inspected `developer_profile_url`, `original_source_url`, `official_company_website`, and `description`.
- **Discovered Inclusions**: Product `hf_space_reycn_PDFMathTranslate-Docker` ("PDFMathTranslate Demo") contains an explicit repository link in its description to `https://github.com/Byaidu/PDFMathTranslate`.

### 2.3 AI Startups (`ai_startups`)
- **Websites & Primary Source URLs**: Evaluated all 1,307 startup records for direct repository bindings.
- **Heuristic Restraint**: Organization profiles without exact repository paths remain `UNVERIFIED` and are not promoted to active repositories without corroborated code links.

---

## 3. Evidence Classification & Confidence Framework

Associations are stored in the dedicated `github_repository_associations` table under the following taxonomy:

| Evidence Type | Description | Default Confidence | Verification Status |
|---|---|---|---|
| `CANONICAL_FIELD` | Explicit repository URL in audited source record | `HIGH` | `VERIFIED` |
| `ABSTRACT_MENTION` | Direct repository URL extracted from paper abstract | `HIGH` | `VERIFIED` |
| `HOMEPAGE_LINK` | Direct repository URL on official company website | `HIGH` | `VERIFIED` |
| `EXPLICIT_SOURCE_LINK` | Direct repository URL in source description/metadata | `HIGH` | `VERIFIED` |
| `DEVELOPER_PROFILE` | Developer profile or organization match | `MEDIUM` | `UNVERIFIED` (until corroborated) |
| `SEARCH_HEURISTIC` | Name/keyword similarity search | `LOW` | `UNVERIFIED` (pending manual review) |

### Strict Association Rules:
1. **Name Similarity Alone Is Insufficient**: A project named "FastAI" is NOT linked to `github.com/fastai/fastai` unless an explicit verified URL or corroborated developer binding exists.
2. **Ambiguous Matches Remain Unverified**: Any link with multiple candidate repos or indeterminate ownership is held in `UNVERIFIED` status.
3. **No Duplicate Repositories**: Repositories are normalized to canonical `owner/repo` (lowercased) to guarantee unique identity across multiple referring entities.

---

## 4. Discovery Execution Results

Summary of initial discovery execution against `data/working/phase5_github_candidate.db`:

| Metric | Count | Notes |
|---|---|---|
| **Total Discovered Associations** | **192** | 190 canonical + 1 paper abstract + 1 product |
| **Research Paper Associations** | 191 | 190 canonical paper implementations + `arxiv_2611_24597` |
| **Product Associations** | 1 | `hf_space_reycn_PDFMathTranslate-Docker` -> `Byaidu/PDFMathTranslate` |
| **Startup Associations** | 0 | Strict filter prevented unverified company name heuristics |
| **Newly Registered Repositories** | 2 | `msalman95/DAL`, `Byaidu/PDFMathTranslate` |
| **Total Tracked Repositories** | **192** | Scaled from 190 to 192 |

---

## 5. Sample Discovered Associations

```json
[
  {
    "association_id": "assoc_research_paper_arxiv_2611_24597_msalman95_DAL",
    "source_entity_type": "research_paper",
    "source_entity_id": "arxiv_2611_24597",
    "repo_id": "msalman95/DAL",
    "evidence_url": "https://github.com/msalman95/DAL",
    "evidence_type": "ABSTRACT_MENTION",
    "confidence": "HIGH",
    "verification_status": "VERIFIED",
    "notes": "Direct GitHub repository URL extracted from official abstract text. Discovered in paper abstract: 'DAL: Dynamic Angular Loss for Imbalanced Medical Image Class'"
  },
  {
    "association_id": "assoc_product_hf_space_reycn_PDFMathTranslate-Docker_Byaidu_PDFMathTranslate",
    "source_entity_type": "product",
    "source_entity_id": "hf_space_reycn_PDFMathTranslate-Docker",
    "repo_id": "Byaidu/PDFMathTranslate",
    "evidence_url": "https://github.com/Byaidu/PDFMathTranslate",
    "evidence_type": "EXPLICIT_SOURCE_LINK",
    "confidence": "HIGH",
    "verification_status": "VERIFIED",
    "notes": "Direct official link in source entity record. Extracted from product description for 'PDFMathTranslate Demo'"
  }
]
```

---

## 6. Data Integrity & Invariants

- **Foreign Key Consistency**: Every association links to a valid `repo_id` present in `github_repositories`.
- **Database Safety**: All discovery writes were executed strictly on the isolated Phase V database `data/working/phase5_github_candidate.db`. The four established databases remain 100% untouched.
