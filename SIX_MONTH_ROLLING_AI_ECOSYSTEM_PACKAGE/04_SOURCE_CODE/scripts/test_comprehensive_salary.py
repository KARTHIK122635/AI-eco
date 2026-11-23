"""
Test Comprehensive Salary Parser across all 1,930 records.
Handles:
- Em-dash, en-dash, hyphens: —, –, -, to
- USD, GBP, EUR symbols ($ , £, €) and codes (USD, GBP, EUR)
- Annual ranges: $190,000 — $230,000 USD
- Ranges with k: $150k - $200k
- Hourly ranges: $60 - $80 / hr
- Base salary vs OTE distinction
"""

import json
import re
from collections import Counter

JSONL_PATH = "data/canonical/canonical_jobs.jsonl"

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    jobs = [json.loads(line)["content"]["data"] for line in f if line.strip()]

def parse_salary_comprehensive(text):
    if not text:
        return None, None, None, None # min, max, currency, comp_type (ANNUAL, HOURLY, OTE)
        
    # Check if sales role with explicit OTE
    is_ote = bool(re.search(r'\bOTE\b|on[\s-]target[\s-]earnings', text, re.I))

    # Pattern 1: Explicit "Annual Salary:" or "Salary Range:" or "Base Salary:"
    # e.g., "Annual Salary: $190,000 — $230,000 USD" or "Annual Salary: £150,000 — £200,000 GBP"
    m_labeled = re.search(
        r'(?:annual\s+salary|base\s+salary|salary\s+range|compensation\s+range)\s*:\s*([$£€])?\s*([0-9]{2,3}(?:,[0-9]{3})+|[0-9]{2,3}k)\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3}(?:,[0-9]{3})+|[0-9]{2,3}k)\s*(USD|GBP|EUR)?',
        text,
        re.IGNORECASE
    )
    if m_labeled:
        curr_sym = m_labeled.group(1) or m_labeled.group(3)
        curr_code = m_labeled.group(5)
        raw_min = m_labeled.group(2).lower()
        raw_max = m_labeled.group(4).lower()
        
        val_min = float(raw_min.replace("k", "000").replace(",", ""))
        val_max = float(raw_max.replace("k", "000").replace(",", ""))
        
        currency = "USD"
        if curr_code:
            currency = curr_code.upper()
        elif curr_sym == "£":
            currency = "GBP"
        elif curr_sym == "€":
            currency = "EUR"
            
        comp_type = "OTE" if is_ote else "ANNUAL"
        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, currency, comp_type

    # Pattern 2: Standard Currency Symbol with Dash/To
    # e.g., "$180,000 — $240,000" or "$180,000 - $240,000 USD" or "£120,000 - £150,000"
    m_standard = re.search(
        r'([$£€])\s*([0-9]{2,3}(?:,[0-9]{3})+)\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3}(?:,[0-9]{3})+)\s*(USD|GBP|EUR)?(?:\s*(?:/\s*year|annually|per\s+year|a\s+year))?',
        text,
        re.IGNORECASE
    )
    if m_standard:
        curr_sym = m_standard.group(1)
        curr_code = m_standard.group(5)
        val_min = float(m_standard.group(2).replace(",", ""))
        val_max = float(m_standard.group(4).replace(",", ""))
        
        currency = "USD"
        if curr_code:
            currency = curr_code.upper()
        elif curr_sym == "£":
            currency = "GBP"
        elif curr_sym == "€":
            currency = "EUR"
            
        comp_type = "OTE" if is_ote else "ANNUAL"
        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, currency, comp_type

    # Pattern 3: Hourly rates
    # e.g. "$60 - $90 / hr" or "$60.00 - $85.00 per hour"
    m_hourly = re.search(
        r'([$£€])\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:/\s*hr|per\s+hour|hourly)',
        text,
        re.IGNORECASE
    )
    if m_hourly:
        curr_sym = m_hourly.group(1)
        val_min = float(m_hourly.group(2))
        val_max = float(m_hourly.group(4))
        currency = "GBP" if curr_sym == "£" else ("EUR" if curr_sym == "€" else "USD")
        if 15 <= val_min <= 500 and val_max >= val_min:
            # We preserve hourly as is, but mark type HOURLY
            return val_min, val_max, currency, "HOURLY"

    # Pattern 4: $150k - $200k USD
    m_k = re.search(
        r'([$£€])\s*([0-9]{2,3})\s*k\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3})\s*k\s*(USD|GBP|EUR)?',
        text,
        re.IGNORECASE
    )
    if m_k:
        curr_sym = m_k.group(1)
        curr_code = m_k.group(5)
        val_min = float(m_k.group(2)) * 1000
        val_max = float(m_k.group(4)) * 1000
        currency = "USD"
        if curr_code:
            currency = curr_code.upper()
        elif curr_sym == "£":
            currency = "GBP"
        elif curr_sym == "€":
            currency = "EUR"
        comp_type = "OTE" if is_ote else "ANNUAL"
        if val_max >= val_min:
            return val_min, val_max, currency, comp_type

    return None, None, None, None

extracted_count = 0
by_type = Counter()
by_curr = Counter()
by_source = Counter()

for j in jobs:
    s_min, s_max, curr, ctype = parse_salary_comprehensive(j["jobDescription"])
    if s_min is not None:
        extracted_count += 1
        by_type[ctype] += 1
        by_curr[curr] += 1
        by_source[j["sourceName"]] += 1

print(f"\n==========================================")
print(f"Total Salaries Successfully Extracted: {extracted_count} / {len(jobs)} ({extracted_count/len(jobs)*100:.1f}%)")
print(f"Previously Extracted: 376")
print(f"Net Gain: +{extracted_count - 376} records!")
print(f"==========================================")
print("\nBy Compensation Type:", dict(by_type))
print("By Currency:", dict(by_curr))
print("\nBy Source:")
for s, cnt in by_source.most_common():
    print(f"  {s:<32}: {cnt}")
