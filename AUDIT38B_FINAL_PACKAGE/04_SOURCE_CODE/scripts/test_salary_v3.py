import json
import re
from collections import Counter

# Load canonical jobs
with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

def is_sales_role(title: str, desc: str) -> bool:
    t = title.lower()
    sales_indicators = [
        "account executive", "sales director", "sales manager", "enterprise sales",
        "commercial sales", "inside sales", "business development", "sales development",
        "strategic pursuits lead", "partner account manager", "renewals manager",
        "head of sales", "sales lead", "gtm enablement", "commercial associate"
    ]
    return any(ind in t for ind in sales_indicators)

def parse_salary_v3(desc: str, title: str, company: str):
    if not desc:
        return None, None, None, None

    # Check for placeholder values like $1-$2, $0, etc.
    if re.search(r'[\$€£]\s*[0-9]\s*(?:—|–|-|to)\s*[\$€£]?\s*[0-9]\b', desc):
        # Could be placeholder unless surrounded by larger numbers
        pass

    # 1. Anthropic / Labeled salary sections with EUR, USD, GBP
    # Handles: "Annual Salary: €220.000 — €235.000 EUR", "Annual Salary: $190,000 — $230,000 USD", etc.
    m_labeled = re.search(
        r'(?:annual\s+salary|base\s+salary|salary\s+range|compensation\s+range|pay\s+range)\s*:\s*([$£€]|EUR|USD|GBP)?\s*([0-9]{2,3}(?:[,\.][0-9]{3})+|[0-9]{2,3}k)\s*(?:—|–|-|to)\s*([$£€]|EUR|USD|GBP)?\s*([0-9]{2,3}(?:[,\.][0-9]{3})+|[0-9]{2,3}k)\s*(USD|GBP|EUR)?',
        desc,
        re.IGNORECASE
    )
    if m_labeled:
        curr_prefix = m_labeled.group(1) or m_labeled.group(3)
        curr_code = m_labeled.group(5)
        raw_min = m_labeled.group(2).lower()
        raw_max = m_labeled.group(4).lower()

        # Parse numbers (handle European . and US ,)
        val_min = float(raw_min.replace("k", "000").replace(",", "").replace(".", ""))
        val_max = float(raw_max.replace("k", "000").replace(",", "").replace(".", ""))

        # Currency detection
        currency = "USD"
        if curr_code:
            currency = curr_code.upper()
        elif curr_prefix:
            cp = curr_prefix.upper()
            if "€" in cp or "EUR" in cp:
                currency = "EUR"
            elif "£" in cp or "GBP" in cp:
                currency = "GBP"
            elif "$" in cp or "USD" in cp:
                currency = "USD"

        # Determine compensationType
        if company == "Anthropic":
            if is_sales_role(title, desc):
                comp_type = "ANNUAL_OTE"
            else:
                comp_type = "ANNUAL_BASE"
        elif "base" in m_labeled.group(0).lower():
            comp_type = "ANNUAL_BASE"
        elif "ote" in desc.lower():
            comp_type = "ANNUAL_OTE"
        else:
            comp_type = "ANNUAL_BASE"

        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, currency, comp_type

    # 2. General Standard Currency Symbol with Dash/To (e.g. "$120,000 - $180,000", "€74.000 — €100.100 EUR")
    m_standard = re.search(
        r'([$£€]|EUR|GBP|USD)\s*([0-9]{2,3}(?:[,\.][0-9]{3})+)\s*(?:—|–|-|to)\s*([$£€]|EUR|GBP|USD)?\s*([0-9]{2,3}(?:[,\.][0-9]{3})+)\s*(USD|GBP|EUR)?(?:\s*(?:/\s*year|annually|per\s+year|a\s+year|brut|brutto))?',
        desc,
        re.IGNORECASE
    )
    if m_standard:
        curr_sym = m_standard.group(1) or m_standard.group(3)
        curr_code = m_standard.group(5)
        val_min = float(m_standard.group(2).replace(",", "").replace(".", ""))
        val_max = float(m_standard.group(4).replace(",", "").replace(".", ""))

        currency = "USD"
        if curr_code:
            currency = curr_code.upper()
        elif curr_sym:
            cs = curr_sym.upper()
            if "€" in cs or "EUR" in cs:
                currency = "EUR"
            elif "£" in cs or "GBP" in cs:
                currency = "GBP"
            elif "$" in cs or "USD" in cs:
                currency = "USD"

        if company == "Anthropic":
            comp_type = "ANNUAL_OTE" if is_sales_role(title, desc) else "ANNUAL_BASE"
        elif "base" in desc.lower():
            comp_type = "ANNUAL_BASE"
        elif "ote" in desc.lower() or is_sales_role(title, desc):
            comp_type = "ANNUAL_OTE"
        else:
            comp_type = "ANNUAL_UNSPECIFIED"

        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, currency, comp_type

    # 3. European Suffix Euro (e.g. "41.000-52.000€", "38.000 bis 45.000 €", "46 000 à 58 000 €")
    m_eur_suffix = re.search(
        r'([0-9]{2,3}(?:[,\.\s][0-9]{3})+)\s*(?:—|–|-|to|à|bis)\s*([0-9]{2,3}(?:[,\.\s][0-9]{3})+)\s*€',
        desc,
        re.IGNORECASE
    )
    if m_eur_suffix:
        raw_min = re.sub(r'[\s\.,]', '', m_eur_suffix.group(1))
        raw_max = re.sub(r'[\s\.,]', '', m_eur_suffix.group(2))
        val_min = float(raw_min)
        val_max = float(raw_max)
        comp_type = "ANNUAL_BASE" if "fixe" in desc.lower() or "base" in desc.lower() else "ANNUAL_UNSPECIFIED"
        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, "EUR", comp_type

    # 4. K-notation (e.g. "$150k - $200k", "EUR255K- 295K", "€60 k‑€90 k")
    m_k = re.search(
        r'([$£€]|EUR|USD|GBP)?\s*([0-9]{2,3})\s*k\s*(?:—|–|-|to)\s*([$£€]|EUR|USD|GBP)?\s*([0-9]{2,3})\s*k\s*(USD|GBP|EUR)?',
        desc,
        re.IGNORECASE
    )
    if m_k:
        curr_sym = m_k.group(1) or m_k.group(3)
        curr_code = m_k.group(5)
        val_min = float(m_k.group(2)) * 1000
        val_max = float(m_k.group(4)) * 1000
        currency = "USD"
        if curr_code:
            currency = curr_code.upper()
        elif curr_sym:
            cs = curr_sym.upper()
            if "€" in cs or "EUR" in cs:
                currency = "EUR"
            elif "£" in cs or "GBP" in cs:
                currency = "GBP"
            elif "$" in cs or "USD" in cs:
                currency = "USD"

        comp_type = "ANNUAL_UNSPECIFIED"
        if "base" in desc.lower():
            comp_type = "ANNUAL_BASE"
        elif "ote" in desc.lower():
            comp_type = "ANNUAL_OTE"

        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, currency, comp_type

    # 5. Hourly rates (e.g. "$26 - $45 / hr", "€28 per hour")
    m_hourly = re.search(
        r'([$£€])\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:/\s*hr|per\s+hour|hourly)',
        desc,
        re.IGNORECASE
    )
    if m_hourly:
        curr_sym = m_hourly.group(1)
        val_min = float(m_hourly.group(2))
        val_max = float(m_hourly.group(4))
        currency = "GBP" if curr_sym == "£" else ("EUR" if curr_sym == "€" else "USD")
        if 15 <= val_min <= 500 and val_max >= val_min:
            return val_min, val_max, currency, "HOURLY"

    # Single hourly rate (e.g. "€28 per hour")
    m_single_hourly = re.search(
        r'([$£€])\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:/\s*hr|per\s+hour|hourly)',
        desc,
        re.IGNORECASE
    )
    if m_single_hourly:
        curr_sym = m_single_hourly.group(1)
        val = float(m_single_hourly.group(2))
        currency = "GBP" if curr_sym == "£" else ("EUR" if curr_sym == "€" else "USD")
        if 15 <= val <= 500:
            return val, val, currency, "HOURLY"

    return None, None, None, None

# Run on all jobs
results = []
comp_type_counter = Counter()
anthropic_comp_types = Counter()
currency_counter = Counter()

for j in jobs:
    desc = j.get('jobDescription', '')
    title = j['jobTitle']
    comp = j['companyName']
    s_min, s_max, curr, comp_type = parse_salary_v3(desc, title, comp)
    results.append((j['jobId'], title, comp, s_min, s_max, curr, comp_type))
    comp_type_counter[str(comp_type)] += 1
    if curr:
        currency_counter[curr] += 1
    if comp == "Anthropic" and comp_type is not None:
        anthropic_comp_types[comp_type] += 1

print(f"Total jobs evaluated: {len(results)}")
print(f"Compensation types: {dict(comp_type_counter)}")
print(f"Anthropic compensation breakdown: {dict(anthropic_comp_types)}")
print(f"Currencies observed: {dict(currency_counter)}")

# Check user's specific test examples:
test_titles = [
    "3P Revenue Accounting & Reporting",
    "Anthropic Research Resident",
    "AI Infrastructure Operations, Demand Planning",
    "Account Executive, AI Native"
]
print("\nUser Test Examples:")
for jid, title, comp, s_min, s_max, curr, comp_type in results:
    if title in test_titles and comp == "Anthropic":
        print(f"  {title:<48} -> {comp_type} | {curr} {s_min} - {s_max}")
