# Phase I: AI Products Empirical Validation Report

**Generated:** 2026-11-22T14:23:03.498441+00:00  
**Canonical Database:** `data/normalized/ai_ecosystem.db` (STRICTLY READ-ONLY)  
**Dataset Table:** `ai_products`  

---

## 1. Executive Summary & Quantitative Milestones

- **Total Ingested AI Products:** **1,316** (Target: ≥ 1,000 — **EXCEEDED by +31.6%**)
- **Primary Key Uniqueness (`product_id`):** 1316/1316 (100.0% Unique, Zero Collisions)
- **Distinct Product Entities:** 1239/1316 (High specificity product indexing)
- **Developer / Company Attribution:** 1,316 / 1,316 (100.0%)
- **Official Website / Portal Coverage:** 123 / 1,316 (9.3%)
- **Original Source URL Coverage:** 1,316 / 1,316 (100.0%)

## 2. Pricing Semantics & Access Architecture

The pipeline rigorously isolates **Pricing Model** (licensing tier) from **Actual Numeric Price** to eliminate LLM hallucinations.

| Dimension | Field Name | Populated Records | Semantics Preserved |
|---|---|:---:|---|
| Licensing Tier | `pricing_model` | 1,316 (100.0%) | Categorical: Freemium, Free, Paid, Subscription, Open Source |
| Deployment Type | `access_type` | 1,316 | Delivery modality: API, Web App, Desktop, Cloud, CLI |
| Verifiable Figure | `actual_price` | 0 | Verifiable dollar/tier values; NULL preserved when unverified |

### Pricing Model Breakdown

| Pricing Model | Product Count | Share |
|---|:---:|:---:|
| `Free Web Application` | 644 | 48.9% |
| `Open Source` | 567 | 43.1% |
| `Gated Research` | 91 | 6.9% |
| `Freemium` | 14 | 1.1% |

### Access Type Breakdown

| Access Type | Product Count | Share |
|---|:---:|:---:|
| `Open Weights / Downloadable` | 643 | 48.9% |
| `Hosted Web Application (Gradio)` | 442 | 33.6% |
| `Hosted Web Application (Static)` | 113 | 8.6% |
| `Hosted Container (Docker)` | 77 | 5.9% |
| `Cloud Web Service / SaaS` | 29 | 2.2% |
| `Hosted Web Application (Streamlit)` | 12 | 0.9% |

## 3. AI Task Categories

| AI Task Category | Product Count | Share |
|---|:---:|:---:|
| gradio | 442 | 33.6% |
| image-text-to-text | 156 | 11.9% |
| text-generation | 140 | 10.6% |
| static | 113 | 8.6% |
| docker | 77 | 5.9% |
| machine-learning | 77 | 5.9% |
| text-to-image | 50 | 3.8% |
| text-to-speech | 42 | 3.2% |
| Applied AI & Automation | 23 | 1.7% |
| image-to-image | 20 | 1.5% |
| automatic-speech-recognition | 18 | 1.4% |
| any-to-any | 18 | 1.4% |
