# AI News Content Quality & Semantics Report

**Date**: November 21, 2026  
**Auditor**: Antigravity Autonomous Data Intelligence Agent  
**Dataset**: `data/canonical/canonical_news.jsonl` / `canonical_news.csv` / `ai_ecosystem.db`

---

## 1. Executive Summary & Quality Declaration

In strict compliance with audit standards:
> **"Do not claim 100% content completeness when only excerpts or generated summaries are present."**
> **"Do not use a generated sentence based on the title as a substitute for article content."**

This report documents the exact semantic separation of content and summary fields across all 1,132 AI news records. Following peer review, the MIT Technology Review entry titled *"Research Reports"* (10 words) was reclassified from `FULL_ARTICLE` to `PUBLISHER_EXCERPT`. Records without publisher-supplied excerpts remain marked as **`METADATA_ONLY`** with `content: null` and `summary: null`.

| Content Classification Tier | Description | Record Count | Percentage | `content` Value | `summary` Value | `summaryType` |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **`FULL_ARTICLE`** | Full article body provided in publisher feed | **39** | **3.4%** | Complete article text | Publisher excerpt | `PUBLISHER_SUMMARY` |
| **`PUBLISHER_EXCERPT`** | Publisher-authored summary/teaser excerpt | **145** | **12.8%** | Publisher excerpt | Publisher excerpt | `PUBLISHER_SUMMARY` |
| **`METADATA_ONLY`** | Authentic metadata record (title, URL, date) | **948** | **83.7%** | `null` | `null` | `NONE` |
| **Total Verified Collection** | | **1,132** | **100.0%** | | | |

---

## 2. Content Tier Breakdown by Source

### 2.1 Full Article Tier (`contentStatus: "FULL_ARTICLE"`) — 39 Records
Sources providing complete article bodies via open RSS/XML:
- **Ars Technica AI** (20 articles): Complete technical journalism body (average length: 2,100 characters).
- **MarkTechPost** (10 articles): Comprehensive technical analysis and benchmark review (average length: 15,000–35,000 characters).
- **MIT Technology Review AI** (9 articles): Complete journalistic and analytical essays (average length: 8,700 characters).

### 2.2 Publisher Excerpt Tier (`contentStatus: "PUBLISHER_EXCERPT"`) — 145 Records
Sources providing publisher-authored summary excerpts:
- **Google DeepMind Blog** (67 articles): Official research teaser/summary excerpts.
- **ZDNet AI** (25 articles): Editorial summary paragraphs.
- **TechCrunch AI** (20 articles): Lead paragraphs and funding summaries.
- **InfoQ AI** (15 articles): Architecture and engineering summary excerpts.
- **Wired AI** (10 articles): Magazine excerpt teasers.
- **MIT Technology Review AI** (1 article): Short teaser excerpt (*"Research Reports"*, canonical URL: `https://www.technologyreview.com/2026/11/17/1148203/research-reports`).
- **VentureBeat AI** (7 articles): Enterprise AI lead paragraphs.

### 2.3 Metadata-Only Tier (`contentStatus: "METADATA_ONLY"`) — 948 Records
Sources where the publisher feed supplies title, canonical link, author, and date without body text:
- **Hugging Face Blog** (915 articles): Complete historical archive (2020–2026). Feed structure provides `<title>`, `<link>`, and `<published>` without `<description>` or `<content>`.
- **Google DeepMind Blog** (33 articles): Historical announcements published without summary text in the XML payload.
- **Integrity Rule**: Rather than fabricating artificial text bodies, `content` and `summary` are strictly preserved as **`null`**, and `summaryType` is marked as **`NONE`**.

---

## 3. Timestamp Audit & Precision

All 1,132 records were audited for timestamp precision and timezone compliance:
- **`published_at`**: 100.0% valid ISO 8601 UTC timestamps (`%Y-%m-%dT%H:%M:%SZ`). Spans from `2020-02-14T00:00:00Z` to `2026-11-21T04:01:04Z`.
- **`collected_at`**: 100.0% valid ISO 8601 UTC timestamps spanning from `2026-11-21T08:05:25Z` to `2026-11-21T08:05:33Z` (an 8-second ingestion execution window).
- **`content_retrieved_at`**: Exactly **184 records** (16.3%) carry content retrieval timestamps (`2026-11-21T08:05:25Z`). The 948 metadata-only records carry **`null`**.
