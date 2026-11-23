import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

def parse_salary_v4(desc: str, title: str, company: str):
    if not desc:
        return None, None, None, None, None

    # Helper to check sales role
    t = title.lower()
    is_sales = any(w in t for w in [
        "account executive", "sales director", "sales lead", "sales manager",
        "enterprise sales", "commercial sales", "inside sales", "business development representative",
        "sales development", "strategic pursuits lead", "partner account manager",
        "partner sales manager", "renewals manager", "head of sales", "sales leader enablement",
        "sales excellence", "scaled growth account executive"
    ]) and not any(nw in t for nw in ["commercial associate", "strategic business development lead", "sales engineer", "solutions architect"])

    # 1. Weekly Stipend (e.g. Anthropic Fellows: "Weekly stipend of 4,615 USD / 3,440 GBP / 6,470 CAD / 4,110 EUR per week")
    m_weekly_stipend = re.search(
        r'(?:weekly\s+stipend\s+(?:of\s+)?|base\s+stipend\s+for\s+this\s+role\s+is\s+)([0-9]{1,2}(?:,[0-9]{3})+)\s*(USD|GBP|EUR|CAD)?(?:\s*/\s*week|\s*per\s+week)?',
        desc,
        re.IGNORECASE
    )
    if m_weekly_stipend:
        val = float(m_weekly_stipend.group(1).replace(",", ""))
        curr = (m_weekly_stipend.group(2) or "USD").upper()
        return val, val, curr, "STIPEND", "WEEKLY"

    # Monthly Stipend (e.g. Ema: "Stipend: £ 2,500 - £ 3,000 / month")
    m_mon_stipend = re.search(
        r'stipend\s*:\s*([$£€]|GBP|EUR|USD)?\s*([0-9]{1,2}(?:[,\.][0-9]{3})*)\s*(?:—|–|-|to)\s*([$£€]|GBP|EUR|USD)?\s*([0-9]{1,2}(?:[,\.][0-9]{3})*)\s*(USD|GBP|EUR)?\s*/\s*month',
        desc,
        re.IGNORECASE
    )
    if m_mon_stipend:
        curr_sym = m_mon_stipend.group(1) or m_mon_stipend.group(3)
        curr_code = m_mon_stipend.group(5)
        v_min = float(m_mon_stipend.group(2).replace(",", "").replace(".", ""))
        v_max = float(m_mon_stipend.group(4).replace(",", "").replace(".", ""))
        curr = "GBP" if curr_sym == "£" or curr_code == "GBP" else ("EUR" if "€" in str(curr_sym) else "USD")
        return v_min, v_max, curr, "STIPEND", "MONTHLY"

    # 2. Hourly Rates (e.g. "CAD $30-50/hour", "$54 — $60 USD", "$45-$50/hour", "€28 per hour")
    m_hourly_labeled = re.search(
        r'(?:hourly\s+rate|compensation)?[:\s]*([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:—|–|-|to)\s*([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(USD|CAD|EUR|GBP)?\s*(?:/\s*hr|/\s*hour|hourly|per\s+hour)',
        desc,
        re.IGNORECASE
    )
    if m_hourly_labeled:
        curr_p = (m_hourly_labeled.group(1) or m_hourly_labeled.group(3) or "").upper()
        curr_s = (m_hourly_labeled.group(5) or "").upper()
        v_min = float(m_hourly_labeled.group(2))
        v_max = float(m_hourly_labeled.group(4))
        curr = "USD"
        if "CAD" in curr_p or "CAD" in curr_s:
            curr = "CAD"
        elif "GBP" in curr_p or "GBP" in curr_s or "£" in curr_p:
            curr = "GBP"
        elif "EUR" in curr_p or "EUR" in curr_s or "€" in curr_p:
            curr = "EUR"
        if 15 <= v_min <= 500 and v_max >= v_min:
            return v_min, v_max, curr, "HOURLY", "HOURLY"

    # Single hourly rate (e.g. "€28 per hour")
    m_single_hr = re.search(
        r'([$£€]|CAD|USD|EUR|GBP)\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:/\s*hr|per\s+hour|hourly)',
        desc,
        re.IGNORECASE
    )
    if m_single_hr:
        curr_p = m_single_hr.group(1).upper()
        val = float(m_single_hr.group(2))
        curr = "EUR" if "€" in curr_p or "EUR" in curr_p else ("GBP" if "£" in curr_p or "GBP" in curr_p else "USD")
        if 15 <= val <= 500:
            return val, val, curr, "HOURLY", "HOURLY"

    # 3. Monthly compensation (e.g. "€4.000 – €7.000 bruto per maand", "€ 2.800 - € 3.600 per maand")
    m_monthly = re.search(
        r'([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{1,2}(?:[,\.][0-9]{3})*)\s*(?:—|–|-|to)\s*([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{1,2}(?:[,\.][0-9]{3})*)\s*(USD|CAD|EUR|GBP)?\s*(?:/\s*month|monthly|per\s+maand|per\s+month|p/m|bruto\s+per\s+maand)',
        desc,
        re.IGNORECASE
    )
    if m_monthly:
        curr_p = (m_monthly.group(1) or m_monthly.group(3) or "").upper()
        curr_s = (m_monthly.group(5) or "").upper()
        raw_min = m_monthly.group(2).replace(",", "").replace(".", "")
        raw_max = m_monthly.group(4).replace(",", "").replace(".", "")
        v_min = float(raw_min)
        v_max = float(raw_max)
        curr = "EUR" if "€" in curr_p or "EUR" in curr_s or "EUR" in curr_p else "USD"
        comp_type = "MONTHLY_BASE" if "brut" in desc.lower() or "base" in desc.lower() or "salaris" in desc.lower() else "MONTHLY_UNSPECIFIED"
        if 1000 <= v_min <= 50000 and v_max >= v_min:
            return v_min, v_max, curr, comp_type, "MONTHLY"

    # 4. Explicit Labeled Salary Pattern (Handles European €220.000 — €235.000 EUR, $190,000 — $230,000 USD, .00 decimals)
    m_labeled = re.search(
        r'(?:annual\s+salary|base\s+salary|salary\s+range|compensation\s+range|pay\s+range)\s*:\s*([$£€]|EUR|USD|GBP|CAD)?\s*([0-9]{2,3}(?:[,\.][0-9]{3})+(?:\.[0-9]{2})?|[0-9]{2,3}k)\s*(?:—|–|-|to)\s*([$£€]|EUR|USD|GBP|CAD)?\s*([0-9]{2,3}(?:[,\.][0-9]{3})+(?:\.[0-9]{2})?|[0-9]{2,3}k)\s*(USD|GBP|EUR|CAD)?',
        desc,
        re.IGNORECASE
    )
    if m_labeled:
        curr_prefix = (m_labeled.group(1) or m_labeled.group(3) or "").upper()
        curr_code = (m_labeled.group(5) or "").upper()
        raw_min = re.sub(r'\.00$', '', m_labeled.group(2).lower())
        raw_max = re.sub(r'\.00$', '', m_labeled.group(4).lower())

        val_min = float(raw_min.replace("k", "000").replace(",", "").replace(".", ""))
        val_max = float(raw_max.replace("k", "000").replace(",", "").replace(".", ""))

        currency = "USD"
        if curr_code:
            currency = curr_code
        elif curr_prefix:
            if "€" in curr_prefix or "EUR" in curr_prefix:
                currency = "EUR"
            elif "£" in curr_prefix or "GBP" in curr_prefix:
                currency = "GBP"
            elif "CAD" in curr_prefix:
                currency = "CAD"

        if company == "Anthropic":
            comp_type = "ANNUAL_OTE" if is_sales else "ANNUAL_BASE"
        elif "base" in m_labeled.group(0).lower():
            comp_type = "ANNUAL_BASE"
        elif "ote" in desc.lower() or is_sales:
            comp_type = "ANNUAL_OTE"
        else:
            comp_type = "ANNUAL_BASE"

        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, currency, comp_type, "ANNUAL"

    # 5. CoreWeave style "$120,000.00 - $160,000.00" / "The base salary range for this role is $108,000.00 to $143,000.00"
    m_decimals = re.search(
        r'(?:base\s+salary\s+range|salary\s+range|cash\s+for\s+this\s+position\s+range\s+from)\s*(?:for\s+this\s+role\s+is)?\s*([$£€])\s*([0-9]{2,3}(?:,[0-9]{3})+\.[0-9]{2})\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3}(?:,[0-9]{3})+\.[0-9]{2})',
        desc,
        re.IGNORECASE
    )
    if m_decimals:
        val_min = float(m_decimals.group(2).replace(",", ""))
        val_max = float(m_decimals.group(4).replace(",", ""))
        return val_min, val_max, "USD", "ANNUAL_BASE", "ANNUAL"

    # 6. Together AI style: "$250-295K" / "$250-300K OTE" / "$ 265-310K"
    m_k_asym = re.search(
        r'([$£€])\s*([0-9]{2,3})\s*(?:k)?\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3})\s*k(?:\s*(USD|CAD|EUR|GBP))?(?:\s*(OTE))?',
        desc,
        re.IGNORECASE
    )
    if m_k_asym:
        val_min = float(m_k_asym.group(2)) * 1000
        val_max = float(m_k_asym.group(4)) * 1000
        curr = (m_k_asym.group(5) or "USD").upper()
        is_explicit_ote = bool(m_k_asym.group(6))
        comp_type = "ANNUAL_OTE" if is_explicit_ote or (company == "Anthropic" and is_sales) else "ANNUAL_BASE"
        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, curr, comp_type, "ANNUAL"

    # 7. Standard integer currency range (e.g. "$120,000 - $180,000", "250,000 to 300,000 USD")
    m_standard = re.search(
        r'([$£€]|EUR|GBP|USD)?\s*([0-9]{2,3}(?:[,\.][0-9]{3})+)\s*(?:—|–|-|to)\s*([$£€]|EUR|GBP|USD)?\s*([0-9]{2,3}(?:[,\.][0-9]{3})+)\s*(USD|GBP|EUR)?(?:\s*(?:/\s*year|annually|per\s+year|a\s+year|brut|brutto))?',
        desc,
        re.IGNORECASE
    )
    if m_standard:
        curr_sym = (m_standard.group(1) or m_standard.group(3) or "").upper()
        curr_code = (m_standard.group(5) or "").upper()
        val_min = float(m_standard.group(2).replace(",", "").replace(".", ""))
        val_max = float(m_standard.group(4).replace(",", "").replace(".", ""))

        currency = "USD"
        if curr_code:
            currency = curr_code
        elif curr_sym:
            if "€" in curr_sym or "EUR" in curr_sym:
                currency = "EUR"
            elif "£" in curr_sym or "GBP" in curr_sym:
                currency = "GBP"

        if company == "Anthropic":
            comp_type = "ANNUAL_OTE" if is_sales else "ANNUAL_BASE"
        elif "base" in desc.lower():
            comp_type = "ANNUAL_BASE"
        elif "ote" in desc.lower() or is_sales:
            comp_type = "ANNUAL_OTE"
        else:
            comp_type = "ANNUAL_UNSPECIFIED"

        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, currency, comp_type, "ANNUAL"

    # 8. European Suffix Euro (e.g. "41.000-52.000€", "38.000 bis 45.000 €", "46 000 à 58 000 €", "52-58K€")
    m_eur_suffix = re.search(
        r'([0-9]{2,3}(?:[,\.\s][0-9]{3})*)\s*(?:k)?\s*(?:—|–|-|to|à|bis)\s*([0-9]{2,3}(?:[,\.\s][0-9]{3})*)\s*k?\s*€',
        desc,
        re.IGNORECASE
    )
    if m_eur_suffix:
        raw_min = re.sub(r'[\s\.,]', '', m_eur_suffix.group(1))
        raw_max = re.sub(r'[\s\.,]', '', m_eur_suffix.group(2))
        val_min = float(raw_min)
        val_max = float(raw_max)
        if val_min < 1000:
            val_min *= 1000
        if val_max < 1000:
            val_max *= 1000
        comp_type = "ANNUAL_BASE" if "fixe" in desc.lower() or "base" in desc.lower() else "ANNUAL_UNSPECIFIED"
        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, "EUR", comp_type, "ANNUAL"

    return None, None, None, None, None

# Test on all jobs
results = []
from collections import Counter
comp_types = Counter()
comp_periods = Counter()
currencies = Counter()
anthropic_comp = Counter()

for j in jobs:
    s_min, s_max, curr, c_type, c_per = parse_salary_v4(j.get('jobDescription', ''), j['jobTitle'], j['companyName'])
    results.append((j['jobId'], j['companyName'], j['jobTitle'], s_min, s_max, curr, c_type, c_per))
    comp_types[str(c_type)] += 1
    comp_periods[str(c_per)] += 1
    if curr:
        currencies[curr] += 1
    if j['companyName'] == 'Anthropic' and c_type is not None:
        anthropic_comp[c_type] += 1

print(f"Total jobs: {len(results)}")
print(f"Compensation Types: {dict(comp_types)}")
print(f"Compensation Periods: {dict(comp_periods)}")
print(f"Currencies: {dict(currencies)}")
print(f"Anthropic breakdown: {dict(anthropic_comp)}")
