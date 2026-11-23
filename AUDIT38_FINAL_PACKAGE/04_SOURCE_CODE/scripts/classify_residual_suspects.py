import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re
from scripts.build_audit12_evidence_map import extract_clean_evidence

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

TRULY_INTRODUCTORY_PATTERNS = [
    r'^\s*(?:about\s+(?:the\s+role|the\s+team|the\s+company|us|anthropic|scale|openai|coreweave|zilliz|google|databricks|nebius|mistral))\b',
    r'^\s*we(?:\'re|\s+are|\s*’re)\s+(?:hiring|looking|seeking)\b',
    r'\b(?:is\s+hiring|is\s+seeking|is\s+looking\s+for)\b',
    r'^\s*join\s+(?:us|the\s+team|our\s+team|anthropic|mistral|openai|scale)\b',
    r'\b(?:our\s+mission\s+is|mission\s+is\s+to|central\s+to\s+anthropic\'s\s+mission)\b',
    r'\b(?:quickly\s+growing\s+group\s+of\s+committed|safe\s+and\s+beneficial\s+for\s+our\s+users)\b',
    r'\b(?:we\'re\s+a\s+small\s+design\s+team|we\'re\s+a\s+small\s+team)\b',
    r'\b(?:how\s+we\'re\s+different|this\s+research\s+continues\s+many\s+of\s+the\s+directions)\b',
    r'\b(?:preferred\s+qualifications|minimum\s+qualifications|basic\s+qualifications)\b',
    r'\b(?:minimum\s+years\s+of\s+experience|coursework,\s+training,\s+or\s+professional\s+experience)\b',
    r'\b(?:research\s+shows\s+that\s+people\s+who\s+identify|we\s+encourage\s+you\s+to\s+apply)\b',
    r'\b(?:your\s+safety\s+matters|legitimate\s+anthropic\s+recruiters)\b',
    r'^\s*anthropic\s+is\s+an\s+ai\s+safety\b',
    r'^\s*scale\s+builds\s+rl\s+environments\b',
    r'^\s*in\s+this\s+pivotal\s+role,\s+you\s+will\s+be\s+instrumental\b'
]

intro_records = []
duty_records = []

for j in jobs:
    ev, ch = extract_clean_evidence(j)
    matched_intro = None
    for p in TRULY_INTRODUCTORY_PATTERNS:
        if re.search(p, ev, re.I):
            matched_intro = p
            break
    if matched_intro:
        intro_records.append((j['jobId'], j['companyName'], j['jobTitle'], matched_intro, ev))
    else:
        duty_records.append(j['jobId'])

print(f"Total jobs evaluated: {len(jobs)}")
print(f"Truly introductory / boilerplate records found: {len(intro_records)}")
for r in intro_records:
    print(f"{r[0]} | {r[1]} | {r[2]} | Pat: {r[3]}")
    print(f"   Excerpt: {r[4]}")
    print()
