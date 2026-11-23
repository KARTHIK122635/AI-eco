# Phase VI Analytics & Chart Range Reconciliation Report — Audit 3

**Project:** AI Ecosystem Intelligence Pipeline  
**Phase:** Phase VI — Dashboard Integration (Audit & Reconciliation)  
**Document:** Analytics Worksheet Structure & Chart Range Audit  
**Execution Timestamp:** 2026-11-23 11:37:00 UTC  
**Target Worksheet:** `GitHub_Analytics`  
**Source Export File:** `data/exports/phase6/github_analytics.csv` (SHA-256: `6ef4c4795eda2db2b7c1e02e9e30e278c7a7685964367db3dc5096a1983c2548`)  

---

## 1. Executive Summary

This audit performs an exhaustive, row-by-row verification of `data/exports/phase6/github_analytics.csv` (47 data rows, 8 columns) and evaluates the proposed chart ranges for Dashboard visualizations.

### Critical Audit Finding
> [!CAUTION]
> **SEVERE CHART RANGE MISALIGNMENT DETECTED IN INITIAL PROPOSAL:**
> The initially proposed source range for Chart 8 (`GitHub_Analytics!C26:D35`) was fundamentally flawed. It started at Rank 8 (`DreamTechAI/Direct3D-V3`), completely omitted the top 7 repositories (including `PDFMathTranslate` with 38,601 stars), and crossed section boundaries into `SHORT_TERM_VELOCITY` (rows 34–35), which would have plotted short-term star deltas alongside total stars.
> 
> This audit provides the exact, corrected row mappings and ranges for all visual feeds.

---

## 2. Exhaustive Inventory of `GitHub_Analytics` Data Segments

`github_analytics.csv` contains 8 columns:
- **Col A:** `section` (Dimension name)
- **Col B:** `metric_key` (Technical programmatic identifier)
- **Col C:** `metric_name` (Human-readable label)
- **Col D:** `value` (Primary numeric measurement)
- **Col E:** `secondary_value` (Auxiliary textual/percentage info)
- **Col F:** `unit` (Unit of measurement)
- **Col G:** `status` (Audit/evidence tag)
- **Col H:** `notes` (Contextual documentation)

When written to Google Sheets with 1 header row at Row 1, the 47 data rows map to **Sheet Rows 2 through 48**:

| Segment ID | Section / Dimension | Row Count | CSV Data Rows | Sheet Row Range | Content & Key Metrics |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **SEG-1** | `LIFECYCLE_DISTRIBUTION` | 8 | 1 – 8 | **Rows 2 – 9** | 8-State lifecycle breakdown: 61 `ACTIVE_VERIFIED`, 131 `NOT_YET_CHECKED`, 0 errors. |
| **SEG-2** | `ECOSYSTEM_COVERAGE` | 6 | 9 – 14 | **Rows 10 – 15** | Papers with code (190), Products with code (1), Startups (0), Association quality (190 Verified, 1 Manual Review, 1 Unverified). |
| **SEG-3** | `LANGUAGE_DISTRIBUTION` | 3 | 15 – 17 | **Rows 16 – 18** | Unknown/Not Specified (188 repos), Python (3 repos, 38,628 stars), Java (1 repo, 4 stars). |
| **SEG-4** | `TOP_REPOSITORIES_STARS` | 15 | 18 – 32 | **Rows 19 – 33** | Top 15 repositories ranked strictly by stargazer volume (Rank 1: `PDFMathTranslate` down to Rank 15: `TabBioMed`). |
| **SEG-5** | `SHORT_TERM_VELOCITY` | 15 | 33 – 47 | **Rows 34 – 48** | Top 15 short-term observed velocity observations (Rank 1: `ACCORD` $+59$ down to Rank 15: `itpd` $+1$). |
| **TOTAL** | **Full Analytics Table** | **47** | **1 – 47** | **Rows 2 – 48** | **100% Accounted For** |

---

## 3. Detailed Audit of Proposed Visualizations

### 3.1 Audit of Chart 7: Repository Lifecycle Distribution
* **Intended Visualization:** Donut Chart (`PIE`) showing active vs unchecked repositories.
* **Previously Proposed Range:** `GitHub_Analytics!B2:D9`
* **Defect Identified:**
  - Column B contains the technical programmatic key (`metric_key`, e.g. `lifecycle_active_verified`).
  - Column C contains the human-readable label (`metric_name`, e.g. `Repositories: ACTIVE_VERIFIED`).
  - Column D contains the quantitative value (`value`, e.g. `61`).
  - Including Column B in the source range causes Google Sheets to produce redundant or unformatted legend keys.
* **Corrected Specification:**
  - **Chart Type:** `PIE` (Donut hole: 40%)
  - **Domain (Labels):** `GitHub_Analytics!C2:C9`
  - **Series (Values):** `GitHub_Analytics!D2:D9`
  - **Combined Range (if single range passed):** `GitHub_Analytics!C2:D9`
  - **Data Validation:** Row 2 (`ACTIVE_VERIFIED` = 61), Row 8 (`NOT_YET_CHECKED` = 131), Rows 3–7, 9 = 0. Total = 192 repositories.

---

### 3.2 Audit of Chart 8: Top AI Research Repositories by Stargazers
* **Intended Visualization:** Horizontal Bar Chart (`BAR`) showing the top repositories by stargazers.
* **Previously Proposed Range:** `GitHub_Analytics!C26:D35`
* **Defects Identified:**
  1. **Omission of Top 7 Repositories:** Rows 19–25 contain the top 7 repositories. Row 19 is `PDFMathTranslate/PDFMathTranslate` with 38,601 stars (96.6% of ecosystem stars). Starting at Row 26 missed this entirely.
  2. **Boundary Spillover into Different Metrics:** Rows 26–33 contain Ranks 8 through 15 of `TOP_REPOSITORIES_STARS`. Rows 34–35 cross into `SHORT_TERM_VELOCITY`, where values represent 2-day star deltas (e.g. $+59$ stars), not cumulative stargazers!
* **Corrected Specification:**
  - **Chart Type:** `BAR` (Horizontal Bar Chart)
  - **Target Selection:** Top 10 AI Research Repositories (Ranks 1 through 10)
  - **Domain (Labels / Repository Names):** `GitHub_Analytics!C19:C28`
  - **Series (Values / Cumulative Stars):** `GitHub_Analytics!D19:D28`
  - **Combined Range:** `GitHub_Analytics!C19:D28`
  - **Top 10 Breakdown:**
    1. `PDFMathTranslate/PDFMathTranslate`: 38,601 stars (Row 19)
    2. `apple-aiml-research/ml-depth-pro-2`: 205 stars (Row 20)
    3. `inclusionAI/CodeWorldModel`: 159 stars (Row 21)
    4. `Shengxiang-Lin/PGPO`: 157 stars (Row 22)
    5. `Carol-lyh/Jeveration`: 72 stars (Row 23)
    6. `be2rlab/ACCORD`: 68 stars (Row 24)
    7. `agentscope-ai/Piccolo`: 60 stars (Row 25)
    8. `DreamTechAI/Direct3D-V3`: 57 stars (Row 26)
    9. `Tencent/WeMM-Video`: 55 stars (Row 27)
    10. `Tencent/WeVisForensics`: 48 stars (Row 28)

---

## 4. Corrected Dashboard Formula Range Mappings

The primary `Dashboard` references `GitHub_Analytics` for auxiliary lookups:

| Dashboard Display Element | Target Cell | Metric Retrieved | Corrected Source Reference | Source Value |
| :--- | :---: | :--- | :--- | :---: |
| **Active Verified Card Subtitle** | `Dashboard!D28` | Active share % | `=GitHub_Analytics!E2` | `"31.77%"` |
| **Unchecked Repositories** | `Dashboard!F27` | Pending backlog | `=GitHub_Analytics!D8` | `131` |
| **Paper Code Coverage %** | `Dashboard!L28` | Paper coverage % | `=GitHub_Analytics!E10` | `"17.92%"` |
| **Top Repository Name** | `Dashboard!A33` | Rank 1 repo name | `=GitHub_Analytics!C19` | `"PDFMathTranslate/PDFMathTranslate"` |
| **Top Repository Stars** | `Dashboard!D33` | Rank 1 stars | `=GitHub_Analytics!D19` | `38,601` |
| **Python Language Share** | `Dashboard!I34` | Python stars % | `=GitHub_Analytics!E17` | `"1.56% (38,628 stars)"` |

---

## 5. Summary & Remediation Classification

- **Status:** **NEEDS_REMEDIATION $\rightarrow$ REMEDIATED**
- **Action Required:** Update chart creation requests in the synchronization engine to use `C2:D9` for Chart 7 and `C19:D28` for Chart 8. Ensure no requests use the broken `C26:D35` range.
