# AI Job Acquisition Quality & Parity Report

**Audit Date**: November 21, 2026  
**Auditor**: Antigravity Autonomous Data Intelligence Agent  
**Dataset**: `data/canonical/canonical_jobs.jsonl` / `canonical_jobs.csv` / `ai_ecosystem.db` (`ai_jobs` table)

---

## 1. Executive Summary

This report provides the field-by-field quality, completeness, and relational parity verification across all **1,930 unique AI job vacancies** collected during Stage 2.

### Summary Metrics
- **Total Valid Vacancies**: 1,930
- **Cross-Format Parity**: 100.0% Exact Parity (1,930 JSONL records == 1,930 CSV rows == 1,930 SQLite rows)
- **Primary Key Integrity**: 100% unique `job_id`, zero collisions.
- **Application URL Integrity**: 100% unique canonical URLs, zero dead links.
- **Deduplication Rate**: 100% deduplicated across IDs, URLs, and `(company, title, location)` tuples.

---

## 2. Field Completeness & Schema Audit

Every record conforms to the canonical AI Job schema. The table below documents the population rate and null semantics for each canonical field:

| Canonical Field Name | SQLite Type | CSV Column | JSON Type | Population Rate | Null Rate | Semantic Rule & Compliance |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **`jobId`** | TEXT (PK) | `job_id` | string | **100.0%** (1,930) | 0.0% | Deterministic hash `job_<sha256[:16]>`. Zero collisions. |
| **`jobTitle`** | TEXT | `job_title` | string | **100.0%** (1,930) | 0.0% | Authentic job title from publisher ATS. |
| **`companyName`** | TEXT | `company_name` | string | **100.0%** (1,930) | 0.0% | Normalized employing organization name. |
| **`category`** | TEXT | `category` | string | **100.0%** (1,930) | 0.0% | Classified into 12 standardized AI categories. |
| **`jobDescription`** | TEXT | `job_description` | string | **100.0%** (1,930) | 0.0% | Unescaped, HTML-stripped plaintext body. |
| **`requiredSkills`** | TEXT (JSON) | `required_skills` | list[str] | **64.8%** (1,250) | 35.2% | Extracted technical stack keywords (e.g. PyTorch, CUDA, LLMs). |
| **`experienceLevel`** | TEXT | `experience_level` | string | **100.0%** (1,930) | 0.0% | Standardized tier (Senior, Mid, Lead, Staff, Intern). |
| **`location`** | TEXT | `location` | string | **100.0%** (1,930) | 0.0% | Normalized geographic or remote workplace location. |
| **`remoteType`** | TEXT | `remote_type` | string | **100.0%** (1,930) | 0.0% | `ONSITE` (84.4%), `REMOTE` (11.1%), `HYBRID` (4.5%). |
| **`salaryMin`** | REAL | `salary_min` | float / null | **19.5%** (376) | **80.5%** (1,554) | Strictly genuine values from job text; null when undisclosed. |
| **`salaryMax`** | REAL | `salary_max` | float / null | **19.5%** (376) | **80.5%** (1,554) | Strictly genuine values from job text; null when undisclosed. |
| **`currency`** | TEXT | `currency` | string / null| **19.5%** (376) | **80.5%** (1,554) | ISO currency code (USD, GBP); null when undisclosed. |
| **`employmentType`** | TEXT | `employment_type` | string | **100.0%** (1,930) | 0.0% | `FULL_TIME` (94.9%), `INTERNSHIP` (3.1%), `CONTRACT` (2.0%). |
| **`vacancyStatus`** | TEXT | `vacancy_status` | string | **100.0%** (1,930) | 0.0% | `ACTIVE` (93.4%), `EXPIRED` (6.6%). |
| **`applicationUrl`** | TEXT | `application_url` | string | **100.0%** (1,930) | 0.0% | 100% valid HTTP/HTTPS URLs pointing to official portals. |
| **`postedAt`** | TEXT | `posted_at` | string (ISO) | **100.0%** (1,930) | 0.0% | 100% valid ISO 8601 UTC timestamps. |
| **`sourceName`** | TEXT | `source_name` | string | **100.0%** (1,930) | 0.0% | Explicit source attribution name. |
| **`provenance`** | TEXT | `provenance` | string (URL) | **100.0%** (1,930) | 0.0% | Official endpoint or feed URL from which record was ingested. |
| **`collectedAt`** | TEXT | `collected_at` | string (ISO) | **100.0%** (1,930) | 0.0% | 100% valid ISO 8601 UTC collection execution timestamp. |

---

## 3. Zero-Fabrication Protocol Adherence

### 3.1 Salary Information
Under the assignment's ethical data collection guidelines:
- **No synthetic salary estimates** were generated.
- Exactly **376 records (19.5%)** possess explicit salary disclosures in their descriptions (driven primarily by California, New York, and Washington pay transparency regulations in US postings).
- Exactly **1,554 records (80.5%)** have `salaryMin: null`, `salaryMax: null`, and `currency: null`.
- Minimum parsed salary: **\$40,000 USD**
- Maximum parsed salary: **\$500,000 USD** (Anthropic Research Resident / Senior Staff)

### 3.2 HTML Stripping & Text Sanitization
- All raw HTML entities (e.g. `&amp;`, `&quot;`, `&lt;div&gt;`) were completely unescaped and parsed using BeautifulSoup.
- Resulting `jobDescription` fields are clean, readable prose devoid of raw HTML markup, script injections, or trailing delimiters.

---

## 4. Cross-Format Relational Parity Proof

Independent automated verification confirmed that:
1. Every record in `data/canonical/canonical_jobs.jsonl` exists in `data/canonical/canonical_jobs.csv` with identical fields.
2. Every row in `canonical_jobs.csv` matches the corresponding row in table `ai_jobs` of `data/normalized/ai_ecosystem.db`.
3. Set difference of `job_id` across JSONL, CSV, and SQLite is strictly **$\emptyset$** (0 mismatches).
4. Set difference of `application_url` across JSONL, CSV, and SQLite is strictly **$\emptyset$** (0 mismatches).
