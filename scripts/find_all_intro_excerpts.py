import csv
import json
import re

with open('reports/stage2_semantic_classification_audit.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Patterns identifying introductory job description language
INTRO_PATTERNS = [
    r'^\s*we are looking for\b',
    r'^\s*we are seeking\b',
    r'^\s*we’re looking for\b',
    r'^\s*we\'re looking for\b',
    r'^\s*we’re seeking\b',
    r'^\s*we\'re seeking\b',
    r'^\s*join our\b',
    r'^\s*join (?:anthropic|scale|openai|coreweave|our)\b',
    r'^\s*about (?:the|us|anthropic|scale|openai|coreweave|our|this)\b',
    r'^\s*who we are\b',
    r'^\s*at [a-zA-Z0-9\s]+, we\b',
    r'^\s*as a [a-zA-Z0-9\s]+ at [a-zA-Z0-9\s]+, you will join\b',
    r'^\s*our team is\b',
    r'^\s*our mission is\b',
    r'^\s*come join\b',
    r'is looking for a\b',
    r'is looking for an\b',
    r'is seeking a\b',
    r'is seeking an\b',
    r'^\s*overview\b',
    r'^\s*the role\b',
    r'^\s*the position\b',
    r'^\s*about the role\b',
    r'^\s*about the team\b',
    r'^\s*we are an equal\b'
]

flagged_records = []
for r in rows:
    ev = r['Source evidence supporting explanation'].strip()
    matched = None
    for pat in INTRO_PATTERNS:
        if re.search(pat, ev, re.I):
            matched = pat
            break
    if matched:
        flagged_records.append((r['Job ID'], r['Company'], r['Job title'], matched, ev))

print(f"Total flagged introductory evidence excerpts: {len(flagged_records)}")
