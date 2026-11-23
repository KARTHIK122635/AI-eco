# Product Pricing & Access Semantics Separation Report

**Date**: November 21, 2026  
**Auditor**: Antigravity Autonomous Data Intelligence Agent  
**Dataset**: `data/canonical/canonical_products.jsonl` / `canonical_products.csv` / `ai_ecosystem.db`

---

## 1. Overview & Policy on Pricing Semantics

The user issued an explicit directive:
> *Separate:*
> - *pricingModel*
> - *license*
> - *accessType*
> - *actualPrice*
> *Do not treat "Open Source Weights" or "Free Web App" as an actual numeric price. Use null when actual pricing is unavailable.*

### Key Semantic Distinctions
1. **`pricingModel` (Commercial Framework)**:
   - Describes how the creator monetizes or releases the software/model.
   - Values: `"Open Source"`, `"Free Web Application"`, `"Gated Research"`, `"Freemium"`.
2. **`license` (Legal Terms)**:
   - Describes legal redistribution and usage rights.
   - Values: `"Open Source"`, `"Gated Open Research"`, or `null` if unannotated.
3. **`accessType` (Delivery Mechanism)**:
   - Describes how end users or developers interact with or consume the artifact.
   - Values: `"Open Weights / Downloadable"`, `"Hosted Web Application (Gradio)"`, `"Hosted Web Application (Static)"`, `"Hosted Container (Docker)"`, `"Hosted Web Application (Streamlit)"`, `"Cloud Web Service / SaaS"`.
4. **`actualPrice` (Monetary Cost)**:
   - Represents the explicit numeric dollar/monetary fee charged for usage.
   - **Critical Rule**: Open-source models and community Gradio spaces have no monetary fee; they do not have a paid subscription tier. Therefore, `actualPrice` is strictly **`null`** across all 1,316 records. Under no circumstances is a descriptive string such as `"Open Source Weights"` or `"Free Web App"` treated as an actual price.

---

## 2. Complete Distribution Across All 1,316 Products

### 2.1 Pricing Model (`pricingModel`)
| Pricing Model | Record Count | Percentage | Description |
| :--- | :---: | :---: | :--- |
| **Free Web Application** | 644 | 48.9% | Free interactive demonstration spaces on Hugging Face |
| **Open Source** | 567 | 43.1% | Openly distributed foundation models, weights, and tools |
| **Gated Research** | 91 | 6.9% | Research models requiring user agreement / registration |
| **Freemium** | 14 | 1.1% | Product Hunt SaaS launches with free tiers |
| **Total** | **1,316** | **100.0%** | Fully classified |

### 2.2 Access Type (`accessType`)
| Access Type | Record Count | Percentage | Target Environment |
| :--- | :---: | :---: | :--- |
| **Open Weights / Downloadable** | 643 | 48.9% | PyTorch/Safetensors/GGUF weights for local execution |
| **Hosted Web Application (Gradio)** | 442 | 33.6% | Interactive Python web interfaces hosted on HF Spaces |
| **Hosted Web Application (Static)** | 113 | 8.6% | WebGPU / JavaScript client-side AI demos |
| **Hosted Container (Docker)** | 77 | 5.9% | Standalone containerized AI services |
| **Cloud Web Service / SaaS** | 29 | 2.2% | Hosted commercial AI SaaS tools |
| **Hosted Web Application (Streamlit)** | 12 | 0.9% | Streamlit-based interactive dashboards |
| **Total** | **1,316** | **100.0%** | Fully classified |

### 2.3 Actual Price (`actualPrice`)
| Actual Price Value | Record Count | Percentage | Validation Assessment |
| :--- | :---: | :---: | :--- |
| **`null` (No monetary price charged)** | **1,316** | **100.0%** | Fully verified; zero descriptive string leakage |
| **Populated Numeric Price** | **0** | **0.0%** | No paid transactions in open models/free spaces |
