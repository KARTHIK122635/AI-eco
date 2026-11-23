import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('reports/all_109_targets.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

# Let's inspect each job and define a clean, verbatim duty excerpt from its jobDescription.
# Let's write a helper to find candidate sentences in the description that:
# 1. Are in jobDescription
# 2. Do not contain any of the banned words:
BANNED = [
    r'\bvision\b',
    r'\bmission\b',
    r'\bculture\b',
    r'\bour team\b|\bour teams\b',
    r'\bjoin\b',
    r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b',
    r'\bwe believe\b|\bwe think\b|\bwe view\b|\bwe are building\b|\bis building\b',
    r'\bequal opportunity\b|\baffirmative action\b|\bwe encourage you to apply\b',
    r'\byears experience\b|\byears of experience\b',
    r'\bbachelor\'s degree\b|\bdegree in\b',
    r'\bideal candidate\b',
    r'\bwho you are\b|\bwhat you\'ll need\b',
    r'\bminimum qualifications\b|\bpreferred qualifications\b',
    r'\bwhat we\'re looking for\b|\bwe are looking for\b|\bwe’re looking for\b',
    r'\bexists to ensure\b',
    r'\bsit at the intersection\b',
    r'\bworld-class\b',
    r'\bcollaborative work:\b',
    r'\bplay a key role in\b|\bplays a key role in\b',
    r'^scale’s rapidly growing',
    r'^about the role',
    r'^about the team',
    r'^role overview',
]

def is_clean(text):
    for b in BANNED:
        if re.search(b, text, re.I):
            return False
    return True

print("Checking baseline...")
