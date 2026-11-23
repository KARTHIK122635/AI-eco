import json
import re
from collections import defaultdict, Counter
import sys
sys.path.append('scripts')
from build_audit8_reasons import records, generate_audit8_reason

reasons = [generate_audit8_reason(r) for r in records]

print(f"Total evaluated records: {len(reasons)}")
print(f"Distinct reasons count: {len(set(reasons))}")

# Check 1: Empty explanations
empty = [i for i, r in enumerate(reasons) if not r or not r.strip()]
print(f"1. Empty explanations: {len(empty)}")
assert len(empty) == 0

# Check 2: Sentence fragments / formatting
fragments = []
for i, r in enumerate(reasons):
    if not r.endswith('.'):
        fragments.append((i, r, "Does not end with period"))
    if r and r[0].islower():
        fragments.append((i, r, "Starts with lowercase"))
    if len(r.split()) < 5:
        fragments.append((i, r, "Fewer than 5 words"))
    if re.match(r'^(?:for|to|that|because|as|with)\s+', r, re.I):
        fragments.append((i, r, "Starts with subordinating preposition"))
print(f"2. Sentence fragments / formatting issues: {len(fragments)}")
assert len(fragments) == 0

# Check 3: Grammar patterns
bad_grammar_patterns = [
    r'\bresponsible for (?:drive|turn|lead|build|design|manage|support|conduct|oversee|coordinate|provide)\b',
    r'\bfocused on (?:turn|build|design|manage|lead|drive)\b',
    r'\bpartnering with customers on be\b',
    r'\bfor understand\b',
    r'\bworking with customers to [a-z]',
    r'\b(\w+)\s+\1\b' # Duplicate words
]
grammar_issues = []
for i, r in enumerate(reasons):
    for pat in bad_grammar_patterns:
        if re.search(pat, r, re.I):
            grammar_issues.append((i, r, pat))
print(f"3. Grammar pattern issues: {len(grammar_issues)}")
assert len(grammar_issues) == 0

# Check 4: Irrelevant company intros
company_intros = [
    r'at cresta', r'to cresta', r'anthropic is dedicated', r'anthropic is building',
    r'scale ai is at the', r'at scale, we', r'more than 20,000', r'about the role',
    r'about anthropic', r'join our team'
]
intro_issues = []
for i, r in enumerate(reasons):
    for pat in company_intros:
        if re.search(pat, r, re.I):
            intro_issues.append((i, r, pat))
print(f"4. Irrelevant company intros: {len(intro_issues)}")
assert len(intro_issues) == 0

# Check 5: Compensation, benefits, visa boilerplate
boilerplate_patterns = [
    r'stipend of', r'weekly stipend', r'annual salary', r'4 months of full-time',
    r'visa sponsorship', r'equal opportunity', r'fair chance', r'benefits \(these vary',
    r'\$\d+', r'€\d+', r'£\d+'
]
bp_issues = []
for i, r in enumerate(reasons):
    for pat in boilerplate_patterns:
        if re.search(pat, r, re.I):
            bp_issues.append((i, r, pat))
print(f"5. Compensation/benefits/visa boilerplate issues: {len(bp_issues)}")
assert len(bp_issues) == 0

# Check 6: Repeated explanations across materially different job categories
reasons_to_titles = defaultdict(set)
for rec, reason in zip(records, reasons):
    reasons_to_titles[reason].add((rec['category'], rec['jobTitle']))

cross_category_reasons = []
for reason, cat_titles in reasons_to_titles.items():
    cats = {c for c, t in cat_titles}
    if len(cats) > 1:
        cross_category_reasons.append((reason, cats))
print(f"6. Explanations shared across different categories: {len(cross_category_reasons)}")
assert len(cross_category_reasons) == 0

print("\nALL AUTOMATED QUALITY CHECKS PASSED WITH 0 DEFECTS!")
