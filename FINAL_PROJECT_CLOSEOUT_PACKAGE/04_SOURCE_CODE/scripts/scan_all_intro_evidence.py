import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Let's inspect all evidence excerpts for:
# 1. Company introductions ("About Anthropic", "Anthropic exists to ensure", "Built for pioneers", "CoreWeave is", "At Scale", "Scale's rapidly growing")
# 2. Team overviews ("Our team", "Our teams", "Our Reinforcement Learning teams sit", "Our Data Center Operations team is")
# 3. Promotional language ("world-class", "paint the vision", "The world's leading companies", "cutting-edge")
# 4. Role introductions ("As an Applied AI team member", "As a Deployment Manager", "Collaborative Work: Get invited")
# 5. Qualification / recruiter language ("5+ years of experience", "The ideal candidate", "Who you are", "Minimum qualifications", "We are looking for")

patterns = [
    (r'\bvision\b', 'vision'),
    (r'\bmission\b', 'mission'),
    (r'\bculture\b', 'culture'),
    (r'\bour team\b|\bour teams\b', 'our team(s)'),
    (r'\bjoin\b', 'join'),
    (r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b', 'about company'),
    (r'\bwe believe\b|\bwe think\b|\bwe view\b|\bwe are building\b|\bis building\b', 'we believe/building'),
    (r'\bequal opportunity\b|\baffirmative action\b|\bwe encourage you to apply\b', 'EEO / apply'),
    (r'\byears experience\b|\byears of experience\b', 'years of experience'),
    (r'\bbachelor\'s degree\b|\bdegree in\b', 'degree'),
    (r'\bideal candidate\b', 'ideal candidate'),
    (r'\bwho you are\b|\bwhat you\'ll need\b', 'who you are / what you need'),
    (r'\bminimum qualifications\b|\bpreferred qualifications\b', 'qualifications header'),
    (r'\bwhat we\'re looking for\b|\bwe are looking for\b|\bwe’re looking for\b', 'looking for'),
    (r'\bexists to ensure\b', 'exists to ensure'),
    (r'\bsit at the intersection\b', 'sit at the intersection'),
    (r'\bworld-class\b', 'world-class'),
    (r'\bcollaborative work:\b', 'collaborative work:'),
    (r'\bplay a key role in\b|\bplays a key role in\b', 'play a key role'),
    (r'^as an? [A-Z]', 'as an X intro'),
    (r'^scale’s rapidly growing', 'scale rapidly growing'),
]

flagged = []
for j in jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    hit_reasons = []
    for pat, label in patterns:
        if re.search(pat, ev, re.IGNORECASE):
            hit_reasons.append(label)
    if hit_reasons:
        flagged.append((j, hit_reasons))

print(f"Total flagged jobs: {len(flagged)}")

# Group by label
label_counts = {}
for j, hit_reasons in flagged:
    for h in hit_reasons:
        label_counts[h] = label_counts.get(h, 0) + 1

for l, c in sorted(label_counts.items(), key=lambda x: -x[1]):
    print(f"  {l}: {c}")
